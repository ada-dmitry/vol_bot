from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
import os
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()
engine = create_async_engine(os.getenv("DATABASE_URL"))
async_session = async_sessionmaker(engine, expire_on_commit=False)

