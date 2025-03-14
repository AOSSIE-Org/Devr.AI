from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import SQLAlchemyError
import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Fetch database credentials
USER = os.getenv("user")
PASSWORD = os.getenv("password")
HOST = os.getenv("host")
PORT = os.getenv("port")
DBNAME = os.getenv("dbname")

# Corrected async SQLAlchemy connection string (removed `sslmode=require`)
DATABASE_URL = f"postgresql+asyncpg://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}"

# Initialize async SQLAlchemy components
try:
    engine = create_async_engine(DATABASE_URL, echo=True, connect_args={"ssl": "require"})

    AsyncSessionLocal = sessionmaker(
        bind=engine, class_=AsyncSession, expire_on_commit=False
    )
    Base = declarative_base()
    print("✅ Database connected successfully!")
except SQLAlchemyError as e:
    print(f"❌ Error connecting to the database: {e}")
    engine = None
    AsyncSessionLocal = None
    Base = None
