from sqlalchemy import Column, BigInteger, Boolean, String
from database import Base

class User(Base):
    __tablename__ = "users"

    user_id = Column(BigInteger, primary_key=True)
    full_name = Column(String, nullable=False)
    study_group = Column(String, nullable=False)
    is_subscribed = Column(Boolean, default=True)
