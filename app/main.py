from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router.auth import user_router
from app.utils.settings import settings

app = FastAPI(
    title="Lunchpaad",
    description="Lunchpaad Backend API",
    version="1.0.0",
)

# CORS — allow the configured frontend origin plus local dev
origins = [
    settings.FE_URL,
    "http://localhost:3000",
    "http://localhost:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "Lunchpaad API is running."}
