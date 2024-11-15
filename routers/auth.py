from fastapi import APIRouter, Depends, status
from pydantic import BaseModel
from models import Users
from passlib.context import CryptContext
from database import get_db
from typing import Annotated
from sqlalchemy.orm import Session

router = APIRouter()

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

# Dependancies
db_dependancy = Annotated[Session, Depends(get_db)]

class CreateUserRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str

@router.get('/auth/')
async def get_user():
    return {
        'user': 'authenticated'
    }
    
@router.post('/auth/', status_code=status.HTTP_201_CREATED)
async def create_user(create_user_request: CreateUserRequest, db: db_dependancy):
    create_user_model = Users(
        name=create_user_request.name,
        email=create_user_request.email,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        role=create_user_request.role,
        is_active=True
    )
    
    db.add(create_user_model)
    db.commit()