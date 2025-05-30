# I main.py så hanterar vi uppstart av hela FastAPI-applikationen och vissa andra operationer,
# såsom lifecycle operations, inkludering av olika routers.
# main.py behöver vara längst upp för att säkerställa att projekts imports sker korrekt
# - det är ju main vi faktiskt kommer köra när vi startar applikationen. Allt utgår därifrån.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db_setup import init_db
from contextlib import asynccontextmanager

from app.api.v1.routers import router


# Funktion som körs när vi startar FastAPI
# perfekt ställe att skapa en uppkoppling till en databas
@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    # koden här körs innan uppstart
    yield
    # koden här körs vid avslut

# lifespan är en funktion som initierar databasen när app startar
app = FastAPI(lifespan=lifespan)


@app.get("/")
async def read_root():
    return {"message": "API is running!"}

app.include_router(router, prefix="/v1", tags=["v1"])
# both routers -upload and genral are imported with this, no separate needed


origins = [
    "http://localhost:3000",  # React app URL
    "http://localhost:8000",  # FastAPI app URL
    "http://localhost:5173",  # FastAPI app URL
    # mistral api called by the mistral package
    "https://api.mistral.ai/v1/chat/completions",
    "https://jib.nu"  # URL to EC2
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
