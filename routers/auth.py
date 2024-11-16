from fastapi import APIRouter, Depends, status, HTTPException
from pydantic import BaseModel
from models import Users
from passlib.context import CryptContext
from database import get_db
from typing import Annotated
from sqlalchemy.orm import Session
from datetime import timedelta, datetime

from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError
import pytz

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY = "ae488423364d214e03bc1dfc2ec8fdcb34103e3240c0916ea8c73ff212c0cf5c"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')

# Dependancies
db_dependancy = Annotated[Session, Depends(get_db)]

class CreateUserRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str
    

class Token(BaseModel):
    access_token: str
    token_type: str
    
    
    
def authenticated_user(email: str, password: str, db):
    user = db.query(Users).filter(Users.email == email).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user


def create_access_token(email: str, user_id: int, expires_delta: timedelta):
    
    encode ={'sub': email, 'id': user_id}
    
    tz = pytz.timezone("Asia/Colombo")
    expires = datetime.now(tz) + expires_delta
    
    encode.update({'exp': expires})
    
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    
    
async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        email: str = payload.get('sub')
        user_id: int = payload.get('id')
        
        if email is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user') 

        return {
            'email': email,
            'user_id': user_id
        }
        
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user') 


@router.get('/')
async def get_user():
    return {
        'user': 'authenticated'
    }
    
@router.post('/', status_code=status.HTTP_201_CREATED)
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
    
    
@router.post('/token', response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependancy):
    authenticated = authenticated_user(
        email=form_data.username,
        password=form_data.password,
        db=db
    )
    
    if not authenticated:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user') 

    
    token = create_access_token(email=authenticated.email, user_id=authenticated.id, expires_delta=timedelta(minutes=20))
    
    return {
        'access_token': token,
        'token_type': 'bearer'
    }
    
