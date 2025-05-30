# TODO ensure that we have a logic for brand_id och device_type_id that should be displayed in frontend as brand name and device_type type
# TODO fixa pydantic schemas istället för att checka parametrar i endpoints
# Endpoints for uploading manual files and images for modelnumber recognition to a S3 bucket.
# can be run both from local or from S3 bucket by changing function from services_upload
from fastapi import APIRouter, HTTPException, Depends, Body
from pydantic import BaseModel, UUID4
from app.api.v1.core.models import UserFileDisplays, Manuals
from app.api.v1.core.schemas import AddManualToUserListRequest, UserFileResponse, UserFileListResponse
from app.db_setup import get_db
from sqlalchemy import select
from app.api.v1.core.services_upload import store_document, store_document_s3
from app.security import get_current_user
from app.settings import Settings
from app.api.v1.core.models import Manuals, Brands, DeviceTypes
from app.db_setup import get_db, get_s3_client
import os
import io
import uuid
from datetime import datetime, UTC
from sqlalchemy import select, update
from sqlalchemy.orm import Session
from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, status
from typing import List, Dict


settings = Settings()


router = APIRouter(
    prefix="/uploads",
    tags=["uploads"]
)

settings = Settings()

# Configuration for storage mode
STORAGE_MODE = "s3"  # or "local"
LOCAL_UPLOAD_FOLDER = "uploads/documents"
S3_BUCKET = settings.S3_BUCKET
AWS_REGION = settings.AWS_REGION  # Assuming this exists in your Settings class


@router.post("/upload-manual")
def upload_manual(
    file: UploadFile = File(...),
    brand_id: uuid.UUID = Form(...),
    modelnumber: str = Form(...),
    modelname: str = Form(...),
    device_type_id: uuid.UUID = Form(...),
    db: Session = Depends(get_db),
    s3_client=Depends(get_s3_client),
    current_user=Depends(get_current_user)
):
    """
    Uploads a manual directly (file in request body) to storage and records it in the database.
    Uses either local storage or S3 depending on configuration.
    """
    # Validate content type
    allowed_content_types = [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ]

    if file.content_type not in allowed_content_types:
        raise HTTPException(
            status_code=400,
            detail=f"Content type {file.content_type} not allowed. Allowed types: {allowed_content_types}"
        )

    try:
        # Read file content
        content = file.file.read()

        # Get the brand and device_type names from the database
        brand = db.execute(select(Brands).where(
            Brands.id == brand_id)).scalar_one()
        device_type = db.execute(select(DeviceTypes).where(
            DeviceTypes.id == device_type_id)).scalar_one()

        # Check if brand and device_type exist
        if not brand or not device_type:
            raise HTTPException(
                status_code=404, detail="Brand or device type not found")

        # Store document based on storage mode
        if STORAGE_MODE == "local":
            # Use the local storage function
            file_obj = io.BytesIO(content)
            result = store_document(
                file=file_obj,
                filename=file.filename,
                brand=brand.name,
                device_type=device_type.type,
                model=modelnumber,
                upload_folder=LOCAL_UPLOAD_FOLDER
            )
        else:  # S3 mode
            # Use the S3 storage function
            file_obj = io.BytesIO(content)

            result = store_document_s3(
                file=file_obj,
                filename=file.filename,
                brand=brand.name,
                device_type=device_type.type,
                model=modelnumber,
                bucket_name=S3_BUCKET,
                region_name=AWS_REGION,
                s3_client=s3_client  # Pass the injected S3 client
            )

        # Extract results
        s3_key, stored_filename = result

        # Create database record
        new_manual = Manuals(
            user_id=current_user.id,
            file_name=stored_filename,
            brand_id=brand_id,
            modelnumber=modelnumber,
            modelname=modelname,
            device_type_id=device_type_id,
            s3_key=s3_key,
            status='completed',
            completed_at=datetime.now(UTC)
        )

        # Insert into database
        db.add(new_manual)
        db.commit()
        db.refresh(new_manual)

        return {
            "status": "success",
            "fileId": new_manual.id,
            "s3_key": s3_key,
            "filename": stored_filename
        }

    except ValueError as e:
        # Handle file validation errors
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Handle other errors
        raise HTTPException(
            status_code=500, detail=f"Error uploading document: {str(e)}")


@router.post("/upload-manual-presigned")
def upload_manual_presigned(
    filename: str,
    content_type: str,
    brand_id: uuid.UUID,
    modelnumber: str,
    modelname: str,
    device_type_id: uuid.UUID,
    db: Session = Depends(get_db),
    s3_client=Depends(get_s3_client),
    current_user=Depends(get_current_user)
):
    """Creates a presigned URL for uploading a manual to S3 and registers it in the database"""

    # Validate content type
    allowed_types = [
        'application/pdf',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    ]

    if content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Content type {content_type} not allowed. Allowed types: {allowed_types}"
        )

    # Create database record first (without S3 URL)
    file_upload = Manuals(
        user_id=current_user.id,
        file_name=filename,  # Original filename
        brand_id=brand_id,
        modelnumber=modelnumber,
        modelname=modelname,
        device_type_id=device_type_id,
        status='pending',
        s3_key=""  # Temporary placeholder
    )

    db.add(file_upload)
    db.commit()
    db.refresh(file_upload)  # Get the generated ID

    # Clean string values for creating S3 key
    brand_clean = clean_string_for_filename(brand_id)
    device_type_clean = clean_string_for_filename(device_type_id)
    model_clean = clean_string_for_filename(modelnumber)
    unique_id = str(uuid.uuid4())

    # Generate proper filename and S3 key
    file_extension = os.path.splitext(filename)[1].lower()
    formatted_filename = f"{brand_clean}_{device_type_clean}_{model_clean}_{unique_id}{file_extension}"
    s3_key = f"documents/{brand_clean}/{device_type_clean}/{model_clean}/{formatted_filename}"

    # Generate presigned URL with this key
    presigned_url = s3_client.generate_presigned_url(
        'put_object',
        Params={
            'Bucket': settings.S3_BUCKET,
            'Key': s3_key,
            'ContentType': content_type
        },
        ExpiresIn=3600
    )

    # Update the record with the actual key
    stmt = update(Manuals).where(
        Manuals.id == file_upload.id).values(s3_key=s3_key)
    db.execute(stmt)
    db.commit()

    return {
        "uploadUrl": presigned_url,
        "fileId": file_upload.id,
        "s3_key": s3_key
    }


@router.post("/confirm-manual-upload")
def confirm_manual_upload(
    file_id: int,
    db: Session = Depends(get_db),
    s3_client=Depends(get_s3_client),
    current_user=Depends(get_current_user)
):
    """Confirms that a manual has been successfully uploaded to S3"""

    # Get file upload record
    stmt = select(Manuals).where(
        Manuals.id == file_id,
        Manuals.user_id == current_user.id
    )
    result = db.execute(stmt)
    file_upload = result.scalar_one_or_none()

    if not file_upload:
        raise HTTPException(status_code=404, detail="File upload not found")

    # Verify file exists in S3
    try:
        s3_client.head_object(
            Bucket=settings.S3_BUCKET,
            Key=file_upload.s3_key
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail="File not found in S3")

    # Update status
    update_stmt = update(Manuals).where(
        Manuals.id == file_id
    ).values(
        status='completed',
        completed_at=datetime.now(UTC)
    )

    db.execute(update_stmt)
    db.commit()

    return {"status": "success"}


# Helper function from our document storage module
def clean_string_for_filename(input_string: str) -> str:
    """
    Clean a string to make it safe for filenames:
    - Convert to lowercase
    - Replace spaces with underscores
    - Remove special characters
    - Limit length
    """
    if not input_string:
        return "unknown"

    # Convert to lowercase and replace spaces with underscores
    cleaned = input_string.lower().strip().replace(" ", "_")

    # Remove special characters
    import re
    cleaned = re.sub(r'[^\w\-]', '', cleaned)

    # Ensure it's not too long (max 50 chars)
    cleaned = cleaned[:50]

    # Ensure we have at least something
    if not cleaned:
        cleaned = "unknown"

    return cleaned

# This code should be added to an existing endpoints file in your project
# For example, you could add this to app/api/v1/core/endpoints/user_manuals.py
# or create a new file for it


# If you're creating a new file, you need to define the router:
# router = APIRouter(
#     prefix="/v1/gen",
#     tags=["user manuals"]
# )

# If you're adding to an existing file, use the router that's already defined there

# Pydantic model for request validation


@router.post("/add_manual_to_user_list")
def add_manual_to_user_list(
    request: AddManualToUserListRequest = Body(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """
    Add a manual to the user's personal list with a custom name for the device.
    """
    try:
        # First, verify that the manual exists
        manual = db.execute(
            select(Manuals)
            .where(Manuals.id == request.file_id)
        ).scalars().first()

        if not manual:
            raise HTTPException(
                status_code=404,
                detail=f"Manual with ID {request.file_id} not found"
            )

        # Check if this manual is already in the user's list
        existing_entry = db.execute(
            select(UserFileDisplays)
            .where(
                UserFileDisplays.user_id == current_user.id,
                UserFileDisplays.file_id == request.file_id,
                UserFileDisplays.remove_from_view == False
            )
        ).scalars().first()

        if existing_entry:
            # Update the existing entry with the new name
            existing_entry.users_own_naming = request.users_own_naming
            db.commit()

            return {
                "status": "success",
                "message": "Manual name updated in your list",
                "display_id": str(existing_entry.id)
            }

        # Create a new entry in the UserFileDisplays table
        new_display = UserFileDisplays(
            user_id=current_user.id,
            file_id=request.file_id,  # Now correctly using UUID
            users_own_naming=request.users_own_naming,
            remove_from_view=False
        )

        db.add(new_display)
        db.commit()
        db.refresh(new_display)

        return {
            "status": "success",
            "message": "Manual added to your list",
            "display_id": str(new_display.id)
        }

    except Exception as e:
        # Rollback the transaction if an error occurs
        db.rollback()
        # Log the error for debugging
        print(f"Error adding manual to user list: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to add manual to your list: {str(e)}"
        )


@router.get("/get_user_file_list", response_model=UserFileListResponse)
def get_user_file_list(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    """Retrieve a list of files that the user has saved to their list"""
    # Explicit check to ensure user is authenticated
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    try:
        # Make sure we have a valid user ID
        if not current_user.id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid user session"
            )

        # Log the user access
        print(f"User {current_user.id} requested their file list")

        # Create a query to get all user files with related info
        stmt = (
            select(
                UserFileDisplays.file_id,
                UserFileDisplays.users_own_naming,
                UserFileDisplays.remove_from_view,
                Brands.name.label('brand'),
                DeviceTypes.type.label('device_type'),
                Manuals.modelnumber.label('model_numbers')
            )
            .join(Manuals, UserFileDisplays.file_id == Manuals.id)
            .join(Brands, Manuals.brand_id == Brands.id)
            .join(DeviceTypes, Manuals.device_type_id == DeviceTypes.id)
            .where(UserFileDisplays.user_id == current_user.id)
            .order_by(UserFileDisplays.users_own_naming)
        )

        # Execute the query
        result = db.execute(stmt)

        # Convert the result to a list of dictionaries
        files = []
        for row in result:
            files.append({
                "file_id": str(row.file_id),
                "users_own_naming": row.users_own_naming,
                "brand": row.brand,
                "device_type": row.device_type,
                "model_numbers": row.model_numbers,
                "remove_from_view": row.remove_from_view
            })

        return {"files": files}

    except Exception as e:
        # Log the error for debugging
        print(f"Error in get_user_file_list: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve user files: {str(e)}"
        )
