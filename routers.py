from os import getenv
from dotenv import load_dotenv
from aiogram import types, Router, F
from aiogram.filters import   Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

from models import Payment, User
from database import SessionLocal
from payments import activate_subscription

from datetime import datetime
from sqlalchemy import select


load_dotenv()
router = Router()

payment_token = getenv('PAYMENT_PROVIDER_TOKEN')
admin_id = getenv('ADMIN_ID')


@router.message(Command("start", "buy"))
async def command_start(message: types.Message):
    async with SessionLocal() as session:
        # Поиск в базе данных
        res = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = res.scalar_one_or_none()

        if not user:
            user = User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                is_admin=message.from_user.id == admin_id
            )

            session.add(user)
            await session.commit()

    buider = InlineKeyboardBuilder()
    buider.row(types.InlineKeyboardButton(text="💵 Купить подписку", callback_data="money"))
    await message.answer(
        f"👋 Добро пожаловать!\n\n"
        f"Оформите подписку, чтобы получить доступ к закрытому каналу.\n"
        f"💰 Стоимость: 10₽ / 30 дней",
        reply_markup=buider.as_markup()
    )


@router.callback_query(F.data == "money")
async def money(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer_invoice(
        title="Подписка",
        description="Доступ к тг каналу",
        provider_token=payment_token,
        currency="RUB",
        prices=[types.LabeledPrice(label="Подписка 30 дней", amount=1000)],
        payload="subscription",
        start_parameter="create_subscription"
    )


#PreCheckout
@router.pre_checkout_query()
async def pre_checkout_query(query: types.PreCheckoutQuery):
    await query.bot.answer_pre_checkout_query(query.id, ok=True)


#Successful payment
@router.message(F.successful_payment)
async def successful_payment(message: types.Message):
    payment = message.successful_payment 

    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one()

        new_payment = Payment(
            user_id=user.id,
            amount=payment.total_amount,
            currency=payment.currency,
            provider_payment_id=payment.telegram_payment_charge_id
        )
        session.add(new_payment)
        await session.commit()

    await activate_subscription(message.from_user.id)
    builder = InlineKeyboardBuilder()
    builder.row(types.InlineKeyboardButton(text="💎 Перейти в канал", url="https://t.me/autoido"))

    await message.answer(
        "✅ Доступ открыт! Нажмите на кнопку ниже, чтобы вступить:",
        reply_markup=builder.as_markup()
    )


#Status
@router.message(Command("status"))
async def status(message: types.Message):
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )
        user = result.scalar_one_or_none()

        if user.subscription_until and user.subscription_until > datetime.utcnow():

            await message.answer(f"✅ Подписка активна до {user.subscription_until.strftime('%H:%M')}\n")
        else:
            await message.answer("❌ Подписка не активна")


@router.message(Command("channel"))
async def chanale(message: types.Message):
    async with SessionLocal() as session:
        result = await session.execute(
            select(User).where(User.telegram_id == message.from_user.id)
        )

        user = result.scalar_one()

        if user.subscription_until and user.subscription_until > datetime.utcnow():
            await message.answer("https://t.me/autoido")
        else:
            await message.answer("Срок действия подписки истёк")



@router.message(Command("broadcast"))
async def broadcast(message: types.Message):

    if message.from_user.id != int(admin_id):
        return

    text = message.text.replace("/broadcast", "")

    if not text:
        await message.answer("Введите текст: начинающийся с /broadcast")
        return

    async with SessionLocal() as session:
        res = await session.execute(select(User.telegram_id))

        user = res.scalars().all()
        async with SessionLocal() as session:
            res = await session.execute(select(User.telegram_id))
            users = res.scalars().all()

            count = 0
            for uid in users:
                try:
                    if uid == int(admin_id):
                        continue
                    await message.bot.send_message(uid, text)
                    count += 1
                except Exception:
                    pass  

            await message.answer(f"📢 Рассылка завершена. Получили {count} чел.")

