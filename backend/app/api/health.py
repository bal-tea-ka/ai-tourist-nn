from fastapi import APIRouter
from datetime import datetime

router = APIRouter()


@router.get("/health")
async def health_check():

    return {
        "status": "ok",
        "version": "1.0.0",
        "environment": "development",
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
