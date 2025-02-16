#create fronted for uploading files

import React, { useState } from 'react';
import { Upload } from 'lucide-react';

const FileUpload = () => {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState('');
  const [progress, setProgress] = useState(0);

  const handleFileSelect = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile && selectedFile.type === 'application/pdf') {
      setFile(selectedFile);
      setError('');
    } else {
      setError('Please select a PDF file');
      setFile(null);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    try {
      setUploading(true);
      setProgress(0);

      // First, get the presigned URL from your backend
      const response = await fetch('/api/get-upload-url', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          filename: file.name,
          contentType: file.type,
        }),
      });

      if (!response.ok) throw new Error('Failed to get upload URL');
      
      const { uploadUrl, fileId } = await response.json();

      // Upload to S3 using the presigned URL
      const uploadResponse = await fetch(uploadUrl, {
        method: 'PUT',
        body: file,
        headers: {
          'Content-Type': file.type,
        },
      });

      if (!uploadResponse.ok) throw new Error('Upload failed');

      // Notify backend that upload is complete
      await fetch('/api/confirm-upload', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ fileId }),
      });

      setProgress(100);
      setFile(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div className="w-full max-w-md mx-auto p-6 bg-white rounded-lg shadow">
      <div className="flex items-center justify-center w-full">
        <label className="flex flex-col items-center justify-center w-full h-64 border-2 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100">
          <div className="flex flex-col items-center justify-center pt-5 pb-6">
            <Upload className="w-10 h-10 mb-3 text-gray-400" />
            <p className="mb-2 text-sm text-gray-500">
              <span className="font-semibold">Click to upload</span> or drag and drop
            </p>
            <p className="text-xs text-gray-500">PDF files only</p>
          </div>
          <input
            type="file"
            className="hidden"
            accept="application/pdf"
            onChange={handleFileSelect}
            disabled={uploading}
          />
        </label>
      </div>

      {file && (
        <div className="mt-4">
          <p className="text-sm text-gray-600">Selected: {file.name}</p>
          <button
            onClick={handleUpload}
            disabled={uploading}
            className="mt-2 w-full px-4 py-2 text-white bg-blue-500 rounded hover:bg-blue-600 disabled:bg-blue-300"
          >
            {uploading ? 'Uploading...' : 'Upload PDF'}
          </button>
        </div>
      )}

      {error && (
        <div className="mt-4 text-sm text-red-500">
          {error}
        </div>
      )}

      {uploading && (
        <div className="mt-4">
          <div className="w-full bg-gray-200 rounded-full h-2.5">
            <div
              className="bg-blue-600 h-2.5 rounded-full"
              style={{ width: `${progress}%` }}
            ></div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FileUpload;

##Fast API for upload
from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from boto3.session import Session as AWSSession
from botocore.config import Config
import boto3
import uuid
from datetime import datetime
from typing import Optional

from .database import get_db
from .models import FileUpload
from .config import Settings

app = FastAPI()
settings = Settings()

# AWS Configuration
aws_session = AWSSession()
s3_client = aws_session.client(
    's3',
    config=Config(signature_version='s3v4'),
    region_name=settings.AWS_REGION,
    aws_access_key_id=settings.AWS_ACCESS_KEY,
    aws_secret_access_key=settings.AWS_SECRET_KEY
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/api/get-upload-url")
async def get_upload_url(
    filename: str,
    content_type: str,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    # Verify user from token
    user = verify_token(token)  # Implement your token verification
    
    # Generate unique file ID
    file_id = str(uuid.uuid4())
    
    # Create S3 key (you might want to organize files by user/date)
    s3_key = f"uploads/{user.id}/{datetime.now().strftime('%Y-%m')}_{filename}"
    
    # Generate presigned URL
    try:
        presigned_url = s3_client.generate_presigned_url(
            'put_object',
            Params={
                'Bucket': settings.S3_BUCKET,
                'Key': s3_key,
                'ContentType': content_type
            },
            ExpiresIn=3600  # URL expires in 1 hour
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    # Create database record
    file_upload = FileUpload(
        id=file_id,
        user_id=user.id,
        filename=filename,
        s3_key=s3_key,
        content_type=content_type,
        status='pending'
    )
    db.add(file_upload)
    db.commit()
    
    return {
        "uploadUrl": presigned_url,
        "fileId": file_id
    }

@app.post("/api/confirm-upload")
async def confirm_upload(
    file_id: str,
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    # Verify user from token
    user = verify_token(token)
    
    # Get file upload record
    file_upload = db.query(FileUpload).filter(
        FileUpload.id == file_id,
        FileUpload.user_id == user.id
    ).first()
    
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
    file_upload.completed_at = datetime.utcnow()
    db.commit()
    
    return {"status": "success"}

    ##### Database model

    from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from .database import Base

class FileUpload(Base):
    __tablename__ = "file_uploads"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    filename = Column(String, nullable=False)
    s3_key = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    status = Column(String, nullable=False)  # pending, completed, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)