from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.database import init_db
from src.router.routes import api_router as main_router

from src import models    

app = FastAPI(
    title="Blog Generation API",
    version="1.0.0",
    description="FastAPI backend for blog generation system"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(main_router)

@app.on_event("startup")
def on_startup():
    print("🚀 Starting application...")
    init_db()
    print("✅ Database initialized")


@app.get("/health")
def home():
    return {"message": "🚀 Blog Generation API is running"}

