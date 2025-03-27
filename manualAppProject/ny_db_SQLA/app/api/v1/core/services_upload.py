import os
from typing import List, BinaryIO, Optional
import re
import boto3
from botocore.exceptions import ClientError
from .models import Manuals, Users
from app.settings import settings
from app.db_setup import get_db, get_s3_client
from fastapi import APIRouter, Depends, HTTPException
from app.security import get_current_user
from sqlalchemy.orm import Session
from sqlalchemy import select
import uuid


def store_document(
    file: BinaryIO,
    filename: str,
    brand: str,
    device_type: str,
    model: str,
    upload_folder: str = "uploads/documents"
) -> List[str]:
    """
    Store a document (PDF or DOC/DOCX) in a local folder and return the S3 key and filename.

    Parameters:
    - file: The file object (file-like object with read method)
    - filename: Original filename of the uploaded file
    - brand: Brand name
    - device_type: Type of device
    - model: Model name/number
    - upload_folder: Directory path where files should be stored

    Returns:
    - List containing [s3_key, stored_filename]

    Raises:
    - ValueError: If the file type is invalid or there's an issue with the file
    - IOError: If there's an issue writing the file
    """
    # Validate file type
    if not filename:
        raise ValueError("No filename provided")

    file_extension = os.path.splitext(filename)[1].lower()
    if file_extension not in ['.pdf', '.doc', '.docx']:
        raise ValueError(
            "Invalid file type. Only PDF, DOC, and DOCX are allowed.")

    # Create upload folder if it doesn't exist
    os.makedirs(upload_folder, exist_ok=True)

    # Clean and format input parameters for filename
    brand_clean = clean_string_for_filename(brand)
    device_type_clean = clean_string_for_filename(device_type)
    model_clean = clean_string_for_filename(model)

    # Create unique ID
    unique_id = str(uuid.uuid4())

    # Format filename: brand_devicetype_model_uuid.ext
    formatted_filename = f"{brand_clean}_{device_type_clean}_{model_clean}_{unique_id}{file_extension}"

    # Full path for storage
    file_path = os.path.join(upload_folder, formatted_filename)

    # Create S3 key (will be used later when migrating to S3)
    s3_key = f"documents/{brand_clean}/{device_type_clean}/{model_clean}/{formatted_filename}"

    # Save the file
    content = file.read()
    with open(file_path, "wb") as f:
        f.write(content)

    # Return just the S3 key and filename in a list
    return [s3_key, formatted_filename]


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
    cleaned = re.sub(r'[^\w\-]', '', cleaned)

    # Ensure it's not too long (max 50 chars)
    cleaned = cleaned[:50]

    # Ensure we have at least something
    if not cleaned:
        cleaned = "unknown"

    return cleaned


def store_document_s3(
    file: BinaryIO,
    filename: str,
    brand: str,
    device_type: str,
    model: str,
    bucket_name: str,
    region_name: str = "us-east-1"
) -> List[str]:
    """
    Store a document (PDF or DOC/DOCX) in an S3 bucket and return the S3 key and filename.

    Parameters:
    - file: The file object (file-like object with read method)
    - filename: Original filename of the uploaded file
    - brand: Brand name
    - device_type: Type of device
    - model: Model name/number
    - bucket_name: The name of the S3 bucket
    - region_name: AWS region name

    Returns:
    - List containing [s3_key, stored_filename]

    Raises:
    - ValueError: If the file type is invalid
    - ClientError: If there's an issue with S3 upload
    """
    # Validate file type
    if not filename:
        raise ValueError("No filename provided")

    file_extension = os.path.splitext(filename)[1].lower()
    if file_extension not in ['.pdf', '.doc', '.docx']:
        raise ValueError(
            "Invalid file type. Only PDF, DOC, and DOCX are allowed.")

    # Clean and format input parameters for filename
    brand_clean = clean_string_for_filename(brand)
    device_type_clean = clean_string_for_filename(device_type)
    model_clean = clean_string_for_filename(model)

    # Create unique ID
    unique_id = str(uuid.uuid4())

    # Format filename: brand_devicetype_model_uuid.ext
    formatted_filename = f"{brand_clean}_{device_type_clean}_{model_clean}_{unique_id}{file_extension}"

    # Create S3 key with logical path structure
    s3_key = f"documents/{brand_clean}/{device_type_clean}/{model_clean}/{formatted_filename}"

    # Initialize S3 client
    s3_client = boto3.client('s3', region_name=region_name)

    # Upload file to S3
    try:
        content = file.read()
        s3_client.put_object(
            Body=content,
            Bucket=bucket_name,
            Key=s3_key,
            ContentType=get_content_type(file_extension)
        )
    except ClientError as e:
        raise e

    # Return just the S3 key and filename in a list
    return [s3_key, formatted_filename]


def get_content_type(file_extension: str) -> str:
    """
    Return the appropriate MIME type based on file extension
    """
    content_types = {
        '.pdf': 'application/pdf',
        '.doc': 'application/msword',
        '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    }

    return content_types.get(file_extension, 'application/octet-stream')


def get_manual_url_for_download(
    file_id: str,
    current_user: Users = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Returns a download URL for the specified file"""
    try:
        # Get file record from database using SQLAlchemy 2.0 style
        stmt = select(Manuals).where(
            Manuals.id == file_id,
            Manuals.user_id == current_user.id
        )
        result = db.execute(stmt)
        file_upload = result.scalar_one_or_none()

        if not file_upload:
            raise HTTPException(status_code=404, detail="File not found")

        # Print for debugging
        print(f"S3 Key: {file_upload.s3_key}")

        # Get S3 client
        s3_client = get_s3_client()

        # Generate a presigned GET URL
        print(f"Generating presigned URL for {file_upload.s3_key}")
        download_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': settings.S3_BUCKET,
                'Key': file_upload.s3_key
            },
            ExpiresIn=3600  # 1 hour expiration
        )
        print(f"URL generated successfully: {download_url[:30]}...")
        return {"downloadUrl": download_url}

    except ClientError as e:
        print(f"S3 client error: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Error generating download URL")
    except Exception as e:
        print(f"Unexpected error: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
