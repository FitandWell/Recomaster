from fastapi import APIRouter, HTTPException, Depends, status
from pydantic import BaseModel
from passlib.context import CryptContext
from sqlalchemy import text
from sqlalchemy.orm import Session
from database import get_db
import os
from dotenv import load_dotenv

load_dotenv()

router = APIRouter()

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Pydantic model for signup
class UserCreate(BaseModel):
    username: str
    email: str
    password: str

# Signup route
@router.post("/signup", status_code=status.HTTP_201_CREATED)
def signup(user: UserCreate, db: Session = Depends(get_db)):
    # Check if the username or email already exists
    query = text("SELECT * FROM users WHERE username = :username OR email = :email")
    existing_user = db.execute(query, {"username": user.username, "email": user.email}).fetchone()
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or email already registered",
        )
    
    # Hash the password
    hashed_password = pwd_context.hash(user.password)

    # Insert the new user into the database
    insert_query = text("INSERT INTO users (username, email, password) VALUES (:username, :email, :password)")
    db.execute(insert_query, {"username": user.username, "email": user.email, "password": hashed_password})
    db.commit()
    
    return {"message": "User created successfully"}
