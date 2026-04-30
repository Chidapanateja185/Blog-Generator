from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.database import init_db
from src.router.routes import api_router as main_router

import os

from src import models    

app = FastAPI(
    title="Blog Generation API",
    version="1.0.0",
    description="FastAPI backend for blog generation system"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://blog-generator-app-nu.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(main_router)


@app.on_event("startup")
def on_startup():
    print("🚀 Starting application...")

    try:
        # Only initialize DB in dev (safe for Cloud Run)
        if os.getenv("ENV", "prod") == "dev":
            init_db()
            print("✅ Database initialized (DEV mode)")
        else:
            print("⚡ Skipping DB init in PROD")

    except Exception as e:
        # IMPORTANT: do NOT crash container
        print("❌ DB initialization failed:", str(e))


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/health")
def health():
    return {"message": "🚀 Blog Generation API is running"}