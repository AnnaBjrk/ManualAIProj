# # anpassa till min databas - hanterar databas relaterad setup
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.api.v1.core.models import Base
from app.settings import settings

from fastapi.security import OAuth2PasswordBearer

import boto3
import os


load_dotenv()
# OAuth2 scheme for token authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")
# echo = True to see the SQL queries
engine = create_engine(f"{settings.DB_URL}", echo=True)


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    with Session(engine, expire_on_commit=False) as session:
        yield session


# S3 client dependency, for connection to S3 bucket
# S3 client dependency, for connection to S3 bucket
#
def get_s3_client():

    # Check environment variables directly
    print("Checking environment variables:")
    print(f"AWS_ACCESS_KEY env: {os.environ.get('AWS_ACCESS_KEY')}")
    print(f"AWS_SECRET_KEY env: {os.environ.get('AWS_SECRET_KEY')}")
    print(f"AWS_REGION env: {os.environ.get('AWS_REGION')}")

    # Check settings object
    print("Checking settings object:")
    print(f"settings.AWS_ACCESS_KEY: {settings.AWS_ACCESS_KEY}")
    print(
        f"settings.AWS_SECRET_KEY: {settings.AWS_SECRET_KEY[:5]}..." if settings.AWS_SECRET_KEY else "None")
    print(f"settings.AWS_REGION: {settings.AWS_REGION}")

    # Create client with explicit parameters
    try:
        client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_SECRET_KEY,
            region_name=settings.AWS_REGION
        )
        return client
    except Exception as e:
        print(f"Error creating S3 client: {e}")
        raise
