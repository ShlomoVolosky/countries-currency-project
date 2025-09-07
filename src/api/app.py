from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from src.api.routes import countries, currencies, health
from src.database.connection import db_connection
from src.config.settings import get_settings
from src.utils.logger import get_logger

logger = get_logger("api")
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_connection.create_pool()
    logger.info("Application started")
    yield
    await db_connection.close_pool()
    logger.info("Application shutdown")


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Countries and Currency Exchange Service",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(countries.router, prefix="/api/v1/countries", tags=["countries"])
app.include_router(currencies.router, prefix="/api/v1/currencies", tags=["currencies"])
app.include_router(health.router, prefix="/api/v1/health", tags=["health"])


@app.get("/")
async def root():
    return {"message": "Countries Currency Service API", "version": settings.app_version}
