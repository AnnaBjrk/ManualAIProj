#I main.py så hanterar vi uppstart av hela FastAPI-applikationen och vissa andra operationer, 
# såsom lifecycle operations, inkludering av olika routers. 
# main.py behöver vara längst upp för att säkerställa att projekts imports sker korrekt 
# - det är ju main vi faktiskt kommer köra när vi startar applikationen. Allt utgår därifrån.

from fastapi import FastAPI, HTTPException, Depends, status
from app.db_setup import init_db, get_db
from contextlib import asynccontextmanager
from fastapi import Request
from sqlalchemy.orm import Session, joinedload, selectinload
from sqlalchemy import select, update, delete, insert
from app.api.v1.core.models import Company
from app.api.v1.core.schemas import CompanySchema
from app.api.v1.routers import router


# Funktion som körs när vi startar FastAPI - 
# perfekt ställe att skapa en uppkoppling till en databas
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db() 
    #koden här körs innan uppstart
    yield
    #koden här körs vid avslut

app = FastAPI(lifespan=lifespan)
app.include_router(router, prefix="/v1", tags=["v1"])


# Depends is FastAPI's dependency injection system
# It means "this function depends on get_db"
# get_db will be called first to create a database session
# The result (a database session) is automatically passed to the db parameter
# This ensures each request gets its own database session

# select(Company) Creates a SELECT SQL query. Similar to writing "SELECT * FROM companies" in SQL
# Company refers to your SQLAlchemy model class

# scalars returnar resulteatet som en lista - vilket är cleanare än om man skulle köra utan det, finns inget retrunar den 404

@app.get("/company", status_code=200)
def list_companies(db: Session = Depends(get_db)):
    programs = db.scalars(select(Company)).all()
    if not programs:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No companies found")
    return programs

...
from app.api.v1.core.schemas import CompanySchema

@app.post("/company", status_code=201)
def add_company(company: CompanySchema, db: Session = Depends(get_db)) -> CompanySchema:
    db_company = Company(**company.model_dump(exclude_unset=True)) # **data.dict() deprecated
    db.add(db_company)
    db.commit()
    db.refresh(db_company) # Vi ser till att vi får den uppdaterade versionen med ID't
		# Du kan skippa .refresh() om du använt expire_on_commit=False i ditt sessionobjekt
    return db_company



############################################
# import os

# import psycopg2
# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from psycopg2.errors import UniqueViolation
# from psycopg2.extras import RealDictCursor
# from manualAppProject.api_sqlAlchemy.schemasSA import RegisterForm
# from manualAppProject.api_sqlAlchemy.schemasSA import LoginForm
# from manualAppProject.api_sqlAlchemy.setupSA import get_connection
# import psycopg2.errorcodes


# app = FastAPI()


# origins = [
#     "http://localhost:3000",  # React app URL
#     "http://localhost:8000",  # FastAPI app URL
#     "http://localhost:5173",  # FastAPI app URL
#     "https://jib.nu"                   #URL to EC2
# ]

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# @app.post("/register")
# def register_user(register_form: RegisterForm):
#     con = get_connection()
#     try:
#         with con:
#             with con.cursor() as cursor:
#                 cursor.execute(
#                     "INSERT INTO users (first_name, last_name, email, password, terms_of_agreement) VALUES (%s, %s, %s, %s, %s) RETURNING id;",
#                     (register_form.first_name, register_form.last_name,
#                      register_form.email, register_form.password, register_form.terms_of_agreement),
#                 )
#                 user_id = cursor.fetchone()[0]
#         return {"id": user_id, "message": "User registered successfully"}
#     except UniqueViolation:
#         raise HTTPException(status_code=400, detail="Email already registered")
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
#     except psycopg2.DatabaseError as e:
#         print(f"PostgreSQL error {e.pgcode} - {e}")
#         raise HTTPException(
#             status_code=500, detail=f"Error executing query: {str(e)}")

# # kontrollera om användaren finns i db, ta in email och lösenord - om anändaren finns i databasen returna first name


# @app.post("/validate_user")
# async def validate_user(login_form: LoginForm):
#     con = get_connection()
#     try:
#         with con:
#             with con.cursor(cursor_factory=RealDictCursor) as cursor:
#                 # Correct the query and parameterization
#                 cursor.execute(
#                     "SELECT first_name, password, id FROM users WHERE email=%s", (
#                         login_form.email,)
#                 )

#                 result = cursor.fetchone()

#                 # Handle the case where no user is found
#                 if not result:
#                     raise HTTPException(
#                         status_code=404, detail="User not found")

#                 # Check password
#                 if login_form.password == result['password']:
#                     return {"id": result['id'], "first_name": result['first_name']}
#                 else:
#                     raise HTTPException(
#                         status_code=401, detail="Password or email is not correct")
#     except psycopg2.DatabaseError as e:
#         print(f"PostgreSQL error {e.pgcode} - {e}")
#         raise HTTPException(
#             status_code=500, detail=f"Error executing query: {str(e)}")
