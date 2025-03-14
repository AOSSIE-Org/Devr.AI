from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from db.db import AsyncSessionLocal
from models.models import (
    User
)
from schemas.schema import (
    UserCreate
)

from fastapi import APIRouter, HTTPException
import os
from supabase import create_client, Client
from dotenv import load_dotenv
import uuid
from datetime import datetime, timezone

# Load environment variables
load_dotenv()
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

# Define Router
router = APIRouter()

# Helper Functions
def generate_uuid():
    return str(uuid.uuid4())

def current_timestamp():
    return datetime.now(timezone.utc).isoformat()

# ========== USER ROUTES ==========
@router.post("/users/")
async def create_user(user: UserCreate):
    user_id = generate_uuid()
   
    response = supabase.table("users").insert({
        "id": user_id,
        "username": user.username,
        "email": user.email,
        "password_hash": user.password_hash,  
       
    }).execute()

    return response

@router.get("/users/")
async def get_users():
    result = supabase.table("users").select("*").execute()
    return result
