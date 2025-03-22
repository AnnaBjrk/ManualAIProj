# from db_setup import get_async_db
from app.security import get_current_user
from app.api.v1.core.models import Users
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, UUID4
from datetime import datetime
from pydantic import BaseModel
from math import ceil
from typing import Optional, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, desc, select, outerjoin, or_
from sqlalchemy.sql.functions import coalesce
from fastapi import FastAPI, Depends, Query, HTTPException
from typing import Annotated
from math import ceil

from app.api.v1.core.models import Tokens, Users, Manuals, UserFileDisplays
from app.api.v1.core.schemas import (
    TokenSchema,
    UserOutSchema,
    RegisterForm,
    PaginatedUserResponse,
    UserResponse,
    AdminStatusUpdate,
    PartnerStatusUpdate,
    DeleteStatusUpdate

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
    """Takes in the data in form submission format, returns access token for user that the 
    frontend puts in local storage"""
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
            "first_name": user.first_name,
            "last_name": user.last_name,
            "is_admin": user.is_admin,
            "is_partner": user.is_partner}


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


# endpoint for admin vidareutveckling sök och lista i bokstavsordning.,filtrering
"""endpoint for the admin view that displays all users. Here the admin can change
status for is_admin, is_partner and mark a user for deletion"""


@router.get("/users_for_admin", response_model=PaginatedUserResponse)
def get_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: Optional[str] = Query(
        None, description="Search for users by first or last name"),
    db: Session = Depends(get_db)
):
    # Calculate offset
    offset = (page - 1) * page_size

    # Subquery to get manual counts per user
    manual_count_subq = (
        select(
            Users.id.label("user_id"),
            func.count(Manuals.id).label("manual_count")
        )
        .outerjoin(Manuals, Users.id == Manuals.user_id)
        .group_by(Users.id)
        .subquery()
    )

    # Subquery to get display counts per user
    display_count_subq = (
        select(
            Users.id.label("user_id"),
            func.count(UserFileDisplays.id).label("display_count")
        )
        .outerjoin(UserFileDisplays, Users.id == UserFileDisplays.user_id)
        .group_by(Users.id)
        .subquery()
    )

    # Subquery to get last login time per user
    last_login_subq = (
        select(
            Tokens.user_id,
            func.max(Tokens.created).label("last_login")
        )
        .group_by(Tokens.user_id)
        .subquery()
    )

    # Main query with all the data joined together
    stmt = (
        select(
            Users.id,  # Added the ID field
            Users.first_name,
            Users.last_name,
            Users.is_admin,
            Users.is_partner,
            Users.deleted,
            coalesce(manual_count_subq.c.manual_count,
                     0).label("manual_count"),
            coalesce(display_count_subq.c.display_count,
                     0).label("display_count"),
            last_login_subq.c.last_login
        )
        .outerjoin(manual_count_subq, Users.id == manual_count_subq.c.user_id)
        .outerjoin(display_count_subq, Users.id == display_count_subq.c.user_id)
        .outerjoin(last_login_subq, Users.id == last_login_subq.c.user_id)
    )

    # Apply search filter if provided
    if search:
        search_pattern = f"%{search}%"
        stmt = stmt.where(
            or_(
                Users.first_name.ilike(search_pattern),
                Users.last_name.ilike(search_pattern)
            )
        )

    # Apply sorting
    stmt = stmt.order_by(Users.last_name, Users.first_name)

    # Count query for pagination info
    count_stmt = select(func.count()).select_from(
        stmt.with_only_columns(Users.id).subquery()
    )
    total = db.scalar(count_stmt)

    # Apply pagination
    paginated_stmt = stmt.offset(offset).limit(page_size)
    result = db.execute(paginated_stmt)
    users = result.mappings().all()

    # Format the response
    user_responses = [
        UserResponse(
            id=str(user["id"]),  # Convert UUID to string
            first_name=user["first_name"],
            last_name=user["last_name"],
            is_admin=user["is_admin"],
            is_partner=user["is_partner"],
            deleted=user["deleted"],
            manual_count=user["manual_count"],
            display_count=user["display_count"],
            last_login=user["last_login"]
        )
        for user in users
    ]

    return PaginatedUserResponse(
        users=user_responses,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=ceil(total / page_size) if total else 0
    )


@router.patch("/users/{userId}/admin-status")
def change_admin_status(
    userId: UUID4,  # Using UUID4 type for automatic validation
    admin_status: AdminStatusUpdate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """
    Toggle a user's admin status.
    Only admin users can perform this action.
    """
    # Check if current user is admin
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized. Admin access required."
        )

    # Find the user to modify
    user = db.query(Users).filter(Users.id == userId).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {userId} not found"
        )

    # Update admin status
    user.is_admin = admin_status.is_admin

    # Commit changes to database
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "user_id": str(userId),
        "is_admin": user.is_admin,
        "message": f"Admin status updated for user {user.first_name} {user.last_name}"
    }


@router.patch("/users/{userId}/partner-status")
def change_partner_status(
    userId: UUID4,
    partner_status: PartnerStatusUpdate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """
    Toggle a user's partner status.
    Only admin users can perform this action.
    """
    # Check if current user is admin
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized. Admin access required."
        )

    # Find the user to modify
    user = db.query(Users).filter(Users.id == userId).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {userId} not found"
        )

    # Update partner status
    user.is_partner = partner_status.is_partner

    # Commit changes to database
    db.add(user)
    db.commit()
    db.refresh(user)

    return {
        "user_id": str(userId),
        "is_partner": user.is_partner,
        "message": f"Partner status updated for user {user.first_name} {user.last_name}"
    }


@router.patch("/users/{userId}/delete-status")
def change_delete_status(
    userId: UUID4,
    delete_status: DeleteStatusUpdate,
    db: Session = Depends(get_db),
    current_user: Users = Depends(get_current_user)
):
    """
    Toggle a user's deletion status (soft delete).
    Only admin users can perform this action.
    """
    # Check if current user is admin
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized. Admin access required."
        )

    # Find the user to modify
    user = db.query(Users).filter(Users.id == userId).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User with ID {userId} not found"
        )

    # Update deletion status
    user.deleted = delete_status.deleted

    # Commit changes to database
    db.add(user)
    db.commit()
    db.refresh(user)

    status_message = "deleted" if user.deleted else "restored"

    return {
        "user_id": str(userId),
        "deleted": user.deleted,
        "message": f"User {user.first_name} {user.last_name} {status_message} successfully"
    }
