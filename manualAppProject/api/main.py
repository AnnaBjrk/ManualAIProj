import os

import psycopg2
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from psycopg2.errors import UniqueViolation
from psycopg2.extras import RealDictCursor
from schemas import RegisterForm
from schemas import LoginForm
from setup import get_connection
import psycopg2.errorcodes


app = FastAPI()


origins = [
    "http://localhost:3000",  # React app URL
    "http://localhost:8000",  # FastAPI app URL
    "http://localhost:5173",  # FastAPI app URL
    "https://jib.nu"                   #URL to EC2
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/register")
def register_user(register_form: RegisterForm):
    con = get_connection()
    try:
        with con:
            with con.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO users (first_name, last_name, email, password, terms_of_agreement) VALUES (%s, %s, %s, %s, %s) RETURNING id;",
                    (register_form.first_name, register_form.last_name,
                     register_form.email, register_form.password, register_form.terms_of_agreement),
                )
                user_id = cursor.fetchone()[0]
        return {"id": user_id, "message": "User registered successfully"}
    except UniqueViolation:
        raise HTTPException(status_code=400, detail="Email already registered")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    except psycopg2.DatabaseError as e:
        print(f"PostgreSQL error {e.pgcode} - {e}")
        raise HTTPException(
            status_code=500, detail=f"Error executing query: {str(e)}")

# kontrollera om användaren finns i db, ta in email och lösenord - om anändaren finns i databasen returna first name


@app.post("/validate_user")
async def validate_user(login_form: LoginForm):
    con = get_connection()
    try:
        with con:
            with con.cursor(cursor_factory=RealDictCursor) as cursor:
                # Correct the query and parameterization
                cursor.execute(
                    "SELECT first_name, password, id FROM users WHERE email=%s", (
                        login_form.email,)
                )

                result = cursor.fetchone()

                # Handle the case where no user is found
                if not result:
                    raise HTTPException(
                        status_code=404, detail="User not found")

                # Check password
                if login_form.password == result['password']:
                    return {"id": result['id'], "first_name": result['first_name']}
                else:
                    raise HTTPException(
                        status_code=401, detail="Password or email is not correct")
    except psycopg2.DatabaseError as e:
        print(f"PostgreSQL error {e.pgcode} - {e}")
        raise HTTPException(
            status_code=500, detail=f"Error executing query: {str(e)}")
