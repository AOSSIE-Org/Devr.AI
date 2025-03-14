from pydantic import BaseModel
from typing import Optional, Dict
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    email: str
    password_hash: str
   
