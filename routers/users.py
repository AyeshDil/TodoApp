from fastapi import APIRouter, Depends, HTTPException, status, Path, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import Annotated
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from passlib.context import CryptContext



from database import get_db
from models import Users
from routers.auth import get_current_user

db_dependancy = Annotated[Session, Depends(get_db)]
user_dependancy = Annotated[dict, Depends(get_current_user)]

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


router = APIRouter(
    prefix='/users',
    tags=['users']
)


class ChangePasswordRequest(BaseModel):
    password: str = Field(min_length=8)



@router.get('/get-user', status_code=status.HTTP_200_OK)
async def get_user(user: user_dependancy, db: db_dependancy):
    user_model = db.query(Users).filter(Users.id == user.get('user_id')).first()
    if not user_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found")
    return user_model.__response__()


@router.put('/change-password', status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependancy, db: db_dependancy, change_password_request: ChangePasswordRequest):
    user_model = db.query(Users).filter(Users.id == user.get('user_id')).first()
    if not user_model:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User Not Found")
    
    user_model.hashed_password = bcrypt_context.hash(change_password_request.password)
    db.add(user_model)
    db.commit()