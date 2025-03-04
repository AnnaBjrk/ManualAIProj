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

# Token verification - inte helt säker på denna något som Claude hittat på, vi - kolla på Tobias authentication
# om denna är värd att använda...


# def verify_token(token: str = Depends(oauth2_scheme)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )

#     try:
#         payload = jwt.decode(token, settings.SECRET_KEY,
#                              algorithms=[settings.ALGORITHM])
#         user_id: str = payload.get("sub")
#         if user_id is None:
#             raise credentials_exception
#     except jwt.PyJWTError:
#         raise credentials_exception

#     # Get user from database
#     db = next(get_db())
#     user = db.query(User).filter(User.id == user_id).first()
#     if user is None:
#         raise credentials_exception

#     return user


# import os
# import time
# import psycopg2
# from dotenv import load_dotenv
# from fastapi import HTTPException
# import psycopg2.errorcodes

# load_dotenv(override=True)

# DATABASE = os.getenv("DATABASE")
# PASSWORD = os.getenv("PASSWORD")
# POSTGRES_USER = os.getenv("POSTGRES_USER")


# def get_connection():
#     """
#     Function that returns a single connection
#     In reality, we might use a connection pool, since
#     this way we'll start a new connection each time
#     someone hits one of our endpoints, which isn't great for performance
#     """
#     return psycopg2.connect(
#         dbname=DATABASE,
#         user=POSTGRES_USER,  # change if needed
#         password=PASSWORD,
#         host="db",  # change if needed
#         port="5432",  # change if needed
#     )


# def create_tables():
#     con = get_connection()
#     create_users_table = """
#         CREATE TABLE IF NOT EXISTS users (
#             id SERIAL PRIMARY KEY,
#             first_name VARCHAR(255) NOT NULL,
#             last_name VARCHAR(255) NOT NULL,
#             email VARCHAR(255) NOT NULL,
#             password VARCHAR(255) NOT NULL,
#             terms_of_agreement BOOLEAN NOT NULL

#         )
#         """
#     try:
#         with con:
#             with con.cursor() as cursor:
#                 cursor.execute(create_users_table)

#     except psycopg2.DatabaseError as e:
#         print(f"PostgreSQL error {e.pgcode} - {e}")
#         raise HTTPException(
#             status_code=500, detail=f"Error executing query: {str(e)}")


# def insert_dummy_data():
#     con = get_connection()
#     with con:
#         with con.cursor() as cursor:
#             cursor.execute("SELECT COUNT(*) FROM users;")
#             count = cursor.fetchone()[0]
#             if count == 0:
#                 cursor.execute(
#                     """
#                     INSERT INTO users (first_name, last_name, email, password, terms_of_agreement)
#                     VALUES
#                     ('Lars', 'Johansson', 'lars.johansson@example.com', 'password123!', TRUE),
#                     ('Emilia', 'Andersson', 'emilia.andersson@example.com', 'secure!Pass1', TRUE),
#                     ('Johan', 'Karlsson', 'johan.karlsson@example.com', 'password!456', TRUE),
#                     ('Astrid', 'Nilsson', 'astrid.nilsson@example.com', 'mySecurePass!', TRUE),
#                     ('Oskar', 'Larsson', 'oskar.larsson@example.com', 'password!789', TRUE),
#                     ('Freja', 'Svensson', 'freja.svensson@example.com', 'superSecret1!', TRUE),
#                     ('Erik', 'Persson', 'erik.persson@example.com', 'hunter2!!!!', TRUE),
#                     ('Klara', 'Lindberg', 'klara.lindberg@example.com', 'pass1234!', TRUE),
#                     ('Nils', 'Bergström', 'nils.bergstrom@example.com', 'password!555', TRUE),
#                     ('Elin', 'Åkesson', 'elin.akesson@example.com', 'p@ssw0rd!', TRUE),
#                     ('Ahmed', 'Al-Farsi', 'ahmed.alfarsi@example.com', 'secure!PassA1', TRUE),
#                     ('Fatima', 'Hassan', 'fatima.hassan@example.com', 'mySecret!99', TRUE),
#                     ('Carlos', 'García', 'carlos.garcia@example.com', 'password!CARL', TRUE),
#                     ('Sofía', 'Martínez', 'sofia.martinez@example.com', 'passMART!', TRUE),
#                     ('John', 'Smith', 'john.smith@example.com', 'smit!hPass1', TRUE),
#                     ('Emily', 'Johnson', 'emily.johnson@example.com', 'johnson!123!', TRUE),
#                     ('Oliver', 'Brown', 'oliver.brown@example.com', 'Brownie!777', TRUE);

#                     """
#                 )
#     con.close()


# if __name__ == "__main__":
#     # Wait for the database to be ready
#     time.sleep(5)
#     create_tables()
#     insert_dummy_data()
