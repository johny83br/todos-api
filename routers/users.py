from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException, Path
from pydantic import BaseModel
from models import Users
from starlette import status
from database import SessionLocal
from passlib.context import CryptContext
from .auth import get_current_user

router = APIRouter(
    prefix="/users",
    tags=["users"]
)
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


class UserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency,
                   db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    return db.query(Users).all()


@router.get("/{user_id}", status_code=status.HTTP_200_OK)
async def read_user(user: user_dependency,
                    db: db_dependency,
                    user_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    user_model = db.query(Users).filter(Users.id == user_id).first()

    if user_model is not None:
        return user_model
    raise HTTPException(status_code=404, detail="User not found")


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, user_request: UserRequest = None):
    create_user_model = Users(
        username=user_request.username,
        email=user_request.email,
        first_name=user_request.first_name,
        last_name=user_request.last_name,
        hashed_password=bcrypt_context.hash(user_request.password),
        role=user_request.role,
        is_active=True
    )
    db.add(create_user_model)
    db.commit()


@router.put("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_user(user: user_dependency,
                      db: db_dependency,
                      user_request: UserRequest,
                      user_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    user_model = db.query(Users).filter(Users.id == user_id).first()

    if user_model is None:
        raise HTTPException(status_code=404, detail="User not found")

    user_model.username = user_request.username
    user_model.email = user_request.email
    user_model.first_name = user_request.first_name
    user_model.last_name = user_request.last_name
    user_model.role = user_request.role

    if user_request.password:
        user_model.hashed_password = bcrypt_context.hash(user_request.password)

    db.add(user_model)
    db.commit()


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user: user_dependency,
                      db: db_dependency,
                      user_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    user_model = db.query(Users).filter(Users.id == user_id).first()

    if user_model is None:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user_model)
    db.commit()
