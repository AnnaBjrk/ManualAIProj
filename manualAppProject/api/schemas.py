# från tobias fil anpassa till mina
from typing import List

from pydantic import BaseModel, EmailStr, Field, field_validator


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


class LoginForm(BaseModel):
    email: EmailStr
    password: str
