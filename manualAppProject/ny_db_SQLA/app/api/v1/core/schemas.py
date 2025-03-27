# Addera fler schemas till endpoints som saknar
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from uuid import UUID


class RegisterForm(BaseModel):
    """form for registration of user in users table"""
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
    """form for user login"""
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


class TokenSchema(BaseModel):
    """For setting validating password creating a token and returning info for local storage"""
    access_token: str
    token_type: str
    first_name: str | None = None
    last_name: str | None = None
    is_admin: bool
    is_partner: bool

    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "first_name": "John",
                "last_name": "Doe",
                "is_admin": "True",
                "is_partner": "False"
            }
        }
    )


class UserOutSchema(BaseModel):
    """validates input in registerform"""
    id: UUID
    email: str
    last_name: str
    first_name: str
    is_admin: bool
    is_partner: bool
    model_config = ConfigDict(from_attributes=True)

# används ej ta bort?
# class SearchRequest(BaseModel):
    modelnumber: str = ""
    modelname: str = ""
    brand: str = ""
    device_type: str = ""


class UserResponse(BaseModel):
    """for endpoint that lists all users for the admin view, validates output"""
    id: UUID
    first_name: str
    last_name: str
    is_admin: bool
    is_partner: bool
    deleted: bool
    manual_count: int
    display_count: int
    last_login: Optional[datetime] = None


class PaginatedUserResponse(BaseModel):
    """for endpoint that lists all users in the admin view, validates output when pagination is used"""
    users: List[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class AdminStatusUpdate(BaseModel):
    """for the endpoint that changes admin status"""
    is_admin: bool


class PartnerStatusUpdate(BaseModel):
    """for the endpoint that changes partner status"""
    is_partner: bool


class DeleteStatusUpdate(BaseModel):
    """for the endpoint that sets the user delete field to true"""
    deleted: bool


class DeleteManualRequest(BaseModel):
    """for the partner function that marks or permanently deletes a manual from the database"""
    file_id: int = Field(...,
                         description="The ID of the manual file to delete")
    hard_delete: bool = Field(
        False, description="Whether to permanently delete or just hide the entry")


class DeleteManualResponse(BaseModel):
    """for response to deleting a manual - in partner table"""
    success: bool
    message: str


class AddManualToUserListRequest(BaseModel):
    file_id: UUID
    users_own_naming: str


class UserFileResponse(BaseModel):
    file_id: str
    users_own_naming: str
    brand: str
    device_type: str
    model_numbers: str
    remove_from_view: bool


class UserFileListResponse(BaseModel):
    files: List[UserFileResponse]
