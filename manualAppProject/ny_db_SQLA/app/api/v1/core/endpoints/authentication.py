from typing import Annotated

from app.api.v1.core.models import Tokens, Users
from app.api.v1.core.schemas import (
    TokenSchema,
    UserOutSchema,
    RegisterForm,
)
from app.db_setup import get_db
from app.security import (
    create_database_token,
    get_current_token,
    hash_password,
    verify_password,
    get_current_user
)
from fastapi import APIRouter, Depends, HTTPException, Response, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import ValidationError
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

router = APIRouter(tags=["auth"], prefix="/auth")


@router.post("/token_login")
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db),
) -> TokenSchema:
    """Takes in the data in form submission format"""
    # Keep in mind that without the response model or return schema
    # we would expose the hashed password, which absolutely cannot happen
    # Perhaps better to use .only or select the columns explicitly
    user = (
        db.execute(
            select(Users).where(Users.email == form_data.username),
        )
        .scalars()
        .first()
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User does not exist",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Passwords do not match",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_database_token(user_id=user.id, db=db)
    return {"access_token": access_token.token,
            "token_type": "bearer",
            "access_token": access_token.token,
            "first_name": user.first_name,
            "last_name": user.last_name}


@router.post("/register", status_code=status.HTTP_201_CREATED)
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

# ev ta bort eller flytta


@router.delete("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout(
    current_token: Tokens = Depends(get_current_token),
    db: Session = Depends(get_db),
):
    db.execute(delete(Tokens).where(Tokens.token == current_token.token))
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

# ev ta bort eller flytta


@router.get("/me", response_model=UserOutSchema)
def read_users_me(current_user: Users = Depends(get_current_user)):
    return current_user


@router.get("/user/name")
def get_user_name(current_user: Users = Depends(get_current_user)):
    return {"first_name": current_user.first_name, "last_name": current_user.last_name}
