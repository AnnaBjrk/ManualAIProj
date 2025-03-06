# I main.py så hanterar vi uppstart av hela FastAPI-applikationen och vissa andra operationer,
# såsom lifecycle operations, inkludering av olika routers.
# main.py behöver vara längst upp för att säkerställa att projekts imports sker korrekt
# - det är ju main vi faktiskt kommer köra när vi startar applikationen. Allt utgår därifrån.
# import os  # ev behövs den inte - används för att importera från env
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db_setup import init_db
from contextlib import asynccontextmanager
# from fastapi import Request
# from sqlalchemy.orm import Session, joinedload, selectinload
# from sqlalchemy import select, update, delete, insert
from app.api.v1.routers import router
# alternativ till psycopg2 error hantering
# from sqlalchemy.exc import IntegrityError
# for fileupdates - lite konstigt här finns ingen uploads....
# psycopg2 behöver inte importas - men man behöver köra pip install psycopg2-binary. SQLAlchemy hittar den automatiskt sen


# Funktion som körs när vi startar FastAPI -
# perfekt ställe att skapa en uppkoppling till en databas
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    # koden här körs innan uppstart
    yield
    # koden här körs vid avslut

# lifespan är en funktion som initierar databasen när app startar
app = FastAPI(lifespan=lifespan)
app.include_router(router, prefix="/v1", tags=["v1"])
# both routers -upload and genral are imported with this, no separate needed


origins = [
    "http://localhost:3000",  # React app URL
    "http://localhost:8000",  # FastAPI app URL
    "http://localhost:5173",  # FastAPI app URL
    "https://jib.nu"  # URL to EC2
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
