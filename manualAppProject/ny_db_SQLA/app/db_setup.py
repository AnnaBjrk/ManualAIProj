# # anpassa till min databas - hanterar databas relaterad setup
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from .api.v1.core.models import Base
from .settings import settings

from fastapi.security import OAuth2PasswordBearer

import boto3


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
def get_s3_client():
    return boto3.client(
        's3',
        # config=Config(signature_version='s3v4')
        aws_access_key_id=settings.AWS_ACCESS_KEY,
        aws_secret_access_key=settings.AWS_SECRET_KEY,
        region_name=settings.AWS_REGION
    )
