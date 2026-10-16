from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from models import Users
from starlette import status
from database import SessionLocal
from passlib.context import CryptContext
from .auth import get_current_user

router = APIRouter(
    prefix="/user",
    tags=["user"]
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


class PasswordRequest(BaseModel):
    password: str
    new_password: str = Field(min_length=6)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Authentication Failed")
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    if user_model is not None:
        return user_model
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail="User not found")


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency,
                          db: db_dependency,
                          password_request: PasswordRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="Authentication Failed")
    user_model = db.query(Users).filter(Users.id == user.get("id")).first()
    if not bcrypt_context.verify(password_request.password,
                                 user_model.hashed_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                            detail="Error on password change")

    user_model.hashed_password = bcrypt_context.hash(
        password_request.new_password)
    db.add(user_model)
    db.commit()
