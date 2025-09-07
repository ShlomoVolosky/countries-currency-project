from fastapi import APIRouter, Depends
from src.database.connection import db_connection
from src.models.api import HealthCheckResponse
from src.config.settings import get_settings

router = APIRouter()
settings = get_settings()


async def check_database_connection() -> bool:
    try:
        async with db_connection.get_connection():
            return True
    except Exception:
        return False


@router.get("/", response_model=HealthCheckResponse)
async def health_check():
    db_connected = await check_database_connection()
    
    status = "healthy" if db_connected else "unhealthy"
    
    return HealthCheckResponse(
        status=status,
        version=settings.app_version,
        database_connected=db_connected
    )
