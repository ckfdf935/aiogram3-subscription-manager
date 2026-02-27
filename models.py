from datetime import datetime
from sqlalchemy import BigInteger
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy import Column, Integer, String, DateTime, Boolean, ForeignKey


Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    telegram_id = Column(BigInteger, unique=True)
    username = Column(String, nullable=True)
    is_admin = Column(Boolean, default=False)
    subscription_until = Column(DateTime, nullable=True)

    payments = relationship("Payment", back_populates="user")


class Payment(Base): 
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id")) 
    amount = Column(Integer) 
    currency = Column(String)
    provider_payment_id = Column(String) 
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="payments")
