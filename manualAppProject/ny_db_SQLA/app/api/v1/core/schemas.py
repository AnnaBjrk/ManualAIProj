# pydantic modeller ev ska vi lägga till en validation??

# från tobias fil anpassa till mina
from typing import List
from datetime import datetime
from enum import Enum

from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict

# heter i tobias fil class UserRegisterSchema


class RegisterForm(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    password: str
    # password: str = Field(..., min_length=8)
    terms_of_agreement: bool

    @field_validator("first_name", "last_name")
    def name_must_not_be_empty(cls, v):
        if not v.strip():
            raise ValueError("must not be empty")
        return v

    @field_validator("password")
    def password_must_contain_special_char(cls, v):
        if len(v) <= 8:
            raise ValueError("Password length must be greater than 8")
        if not any(char in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for char in v):
            raise ValueError("Password must contain a special character")
        return v

    @field_validator("terms_of_agreement")
    def terms_must_be_accepted(cls, v):
        if not v:
            raise ValueError("You must accept the terms")
        return v

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "first_name": "Anna",
                "last_name": "Anderssson",
                "email": "info@techuniversity.com",
                "password": "Summer12234!",
                "terms_of_agreement": True,
            }
        }
    )


class LoginForm(BaseModel):
    email: EmailStr
    password: str
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "email": "info@techuniversity.com",
                "password": "Summer12234!",
            }
        }
    )


# We use this for our auth - ny
class TokenSchema(BaseModel):
    access_token: str
    token_type: str
    first_name: str | None = None
    last_name: str | None = None

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "first_name": "John",
                "last_name": "Doe"
            }
        }
    )


# We use this to return user data in authentication
class UserOutSchema(BaseModel):
    id: int
    email: str
    last_name: str
    first_name: str
    is_superuser: bool
    model_config = ConfigDict(from_attributes=True)

# for search without image


class SearchRequest(BaseModel):
    modelnumber: str = ""
    modelname: str = ""
    brand: str = ""
    device_type: str = ""
