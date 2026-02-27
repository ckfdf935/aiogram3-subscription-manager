from models import User
from sqlalchemy import select
from database import SessionLocal
from datetime import datetime, timedelta


SUBSCRIPTION_DAYS = 30

async def activate_subscription(telegram_id: int):
    async with SessionLocal() as session:
        user = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = user.scalar_one()

        if user.subscription_until and user.subscription_until > datetime.utcnow():
            user.subscription_until += timedelta(days=SUBSCRIPTION_DAYS)
        else:
            user.subscription_until = datetime.utcnow() + timedelta(days=SUBSCRIPTION_DAYS)

        session.add(user)
        await session.commit()
