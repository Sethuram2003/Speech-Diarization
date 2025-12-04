from dotenv import load_dotenv
load_dotenv()

from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes.HealthCheck import health_check_router
from app.api.routes.SpeechDiarization import diarization_router
from app.core.Models import load_models

from fastapi import FastAPI

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Loading models ....")
    await load_models()

    yield

    print("shutting down fastapi cleaning up models....")

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_check_router)
app.include_router(diarization_router)
