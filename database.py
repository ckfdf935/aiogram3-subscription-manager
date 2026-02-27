from os import getenv
from dotenv import load_dotenv

from models import Base
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

load_dotenv()
DATABASE_URL = getenv("DATABASE_URL")

engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)