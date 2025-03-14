from sqlalchemy import Column, String, Integer, ForeignKey, Float, Text, JSON, DECIMAL, TIMESTAMP
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from db.db import Base
import uuid

def generate_uuid():
    return str(uuid.uuid4())

# User Table (Creators & Brands)
class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=generate_uuid)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
   