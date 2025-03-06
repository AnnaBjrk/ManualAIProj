# # anpassa till min databas - hanterar databas relaterad setup
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
# from sqlalchemy.ext.declarative import declarative_base
from .api.v1.core.models import Base
from .settings import settings

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

import boto3
# import jwt
import uuid
from datetime import datetime

from .settings import settings
# from .api.v1.core.models import Users

load_dotenv()


# echo = True to see the SQL queries
engine = create_engine(f"{settings.DB_URL}", echo=True)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    with Session(engine, expire_on_commit=False) as session:
        yield session


# S3 client dependency
def get_s3_client():
    return boto3.client(
        's3',
        # config=Config(signature_version='s3v4')
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_KEY,
        region_name=settings.AWS_REGION
    )


# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")
