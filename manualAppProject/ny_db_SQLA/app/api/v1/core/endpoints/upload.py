from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime, UTC
import uuid

from app.db_setup import get_db, get_s3_client, oauth2_scheme  # verify_token
from app.api.v1.core.models import FileUpload
from app.settings import Settings

router = APIRouter(
    prefix="/api",
    tags=["uploads"]
)

settings = Settings()


@router.post("/get-upload-url")
async def get_upload_url(
    filename: str,
    content_type: str,
    brand: str,
    modelnumber_1: str,
    modelnumber_2: str,
    device_type: str,
    db: Session = Depends(get_db),
    s3_client=Depends(get_s3_client),
    token: str = Depends(oauth2_scheme)
):

    # Validate content type, This parameter is typically sent by the client (frontend) when making the request to get the upload URL.
    allowed_types = [
        'application/pdf',
        'image/jpeg',
        'image/png',
        'text/csv'
    ]

    if content_type not in allowed_types:
        raise HTTPException(
            status_code=400,
            detail=f"Content type {content_type} not allowed. Allowed types: {allowed_types}"
        )

    # Verify user from token
    # user = verify_token(token)

    # Generate unique file ID
    file_id = str(uuid.uuid4())

    # Create S3 key
    s3_key = f"uploads/{user.id}/{file_id}_{filename}"

    # Generate presigned URL
    try:
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': settings.S3_BUCKET,
                'Key': s3_key,
                'ContentType': content_type
            },
            ExpiresIn=3600
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    # Create database record
    file_upload = FileUpload(
        user_id=user.id,
        url_to_file=presigned_url,
        brand=brand,
        modelnumber_1=modelnumber_1,
        modelnumber_2=modelnumber_2,
        device_type=device_type,
        s3_key=s3_key,
        status='pending'
    )
    db.add(file_upload)
    db.commit()

    return {
        "uploadUrl": presigned_url,
        "fileId": file_id
    }


@router.post("/confirm-upload")
async def confirm_upload(
    file_id: str,
    db: Session = Depends(get_db),
    s3_client=Depends(get_s3_client),  # Changed to use dependency
    token: str = Depends(oauth2_scheme)
):
    # Verify user from token
    # user = verify_token(token)

    # Get file upload record
    stmt = select(FileUpload).where(
        FileUpload.id == file_id,
        FileUpload.user_id == user.id
    )
    file_upload = db.scalar(stmt)

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
    file_upload.status = 'completed'
    file_upload.completed_at = datetime.now(UTC)
    db.commit()

    return {"status": "success"}
