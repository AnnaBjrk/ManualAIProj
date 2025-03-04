from typing import Annotated

from app.api.v1.core.models import Token, Users
from app.api.v1.core.schemas import (
    TokenSchema,
    UserOutSchema,
    RegisterForm,
)
from app.db_setup import get_db
from app.security import (
    hash_password
)
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import ValidationError
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

router = APIRouter(tags=["auth"], prefix="/auth")


@router.post("/user/create", status_code=status.HTTP_201_CREATED)
def register_user(
    user: RegisterForm, db: Session = Depends(get_db)
) -> UserOutSchema:
    # TODO ADD VALIDATION TO CREATION OF PASSWORD
    hashed_password = hash_password(user.password)
    # We exclude password from the validated pydantic model since the field/column is called hashed_password, we add that manually
    new_user = Users(
        **user.model_dump(exclude={"password"}), password=hashed_password
    )
    db.add(new_user)
    db.commit()
    return new_user
