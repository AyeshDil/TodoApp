from fastapi import APIRouter, Depends, HTTPException, Path, status
import models 
from database import get_db
from typing import Annotated
from sqlalchemy.orm import Session
from models import Todos
from pydantic import BaseModel, Field

from routers.auth import get_current_user

router = APIRouter()

# Dependancies
db_dependancy = Annotated[Session, Depends(get_db)]
user_dependancy = Annotated[dict, Depends(get_current_user)]

# Schemas
class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=255)
    priority: int = Field(gt=0, lt=10)
    isCompleted: bool


# Routes

@router.get('/')
async def index():
    return "TODO APPLICATION"


@router.get('/todos', status_code=status.HTTP_200_OK)
async def get_all_todos(user: user_dependancy, db: db_dependancy):
    return db.query(Todos).filter(Todos.owner_id == user.get('user_id')).all()


@router.get('/todos/{todo_id}', status_code=status.HTTP_200_OK)
async def get_todo(user: user_dependancy, db: db_dependancy, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get('user_id')).first()
    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found")


@router.post('/todos', status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependancy, db: db_dependancy, todo_request: TodoRequest):
    
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Authentication Failed")
    
    todo_model = Todos(
        title = todo_request.title,
        description = todo_request.description,
        priority = todo_request.priority,
        is_completed = todo_request.isCompleted,
        owner_id = user.get('user_id')
    )
    db.add(todo_model)
    db.commit()
    

@router.put('/todos/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependancy, db: db_dependancy, todo_id: int, todo_request: TodoRequest):
    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get('user_id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    todo_model.title = todo_request.title
    todo_model.description = todo_request.description
    todo_model.priority = todo_request.priority
    todo_model.is_completed = todo_request.isCompleted
    
    db.add(todo_model)
    db.commit()
    
    
@router.delete('/todos/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependancy, db: db_dependancy, todo_id: int = Path(gt=0)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
        .filter(Todos.owner_id == user.get('user_id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    db.delete(todo_model)
    db.commit()

