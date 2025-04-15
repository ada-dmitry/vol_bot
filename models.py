from sqlalchemy import Column, BigInteger, Boolean
from database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True)
    is_subscribed = Column(Boolean, default=True)
