from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pathlib import Path
import os
from app.database import connect_to_mongo, close_mongo_connection
from app.routes import router as posts_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    yield
    await close_mongo_connection()

application = FastAPI(
    title="Portfolio Backend API",
    lifespan=lifespan
)

# Allow your production domain and local development
origins = [
    "http://localhost:5173",
    "https://meetkalid.com",
    "https://www.meetkalid.com",
]

application.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Ensure uploads directory exists before mounting
BASE_DIR = Path(__file__).resolve().parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Serve the uploaded images
application.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

application.include_router(posts_router, prefix="/api")

@application.get("/")
async def root():
    return {"status": "ok"}