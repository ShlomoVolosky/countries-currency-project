from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from src.api.routes import countries, currencies, health
from src.database.connection import db_connection
from src.config.settings import get_settings
from src.utils.logger import get_logger
from src.monitoring.middleware import PrometheusMiddleware
from src.monitoring.metrics import update_countries_count, update_currency_rates_count

logger = get_logger("api")
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    await db_connection.create_pool()
    logger.info("Application started")
    
    # Update metrics with current data counts
    try:
        from src.database.repositories import CountryRepository, CurrencyRateRepository
        countries_repo = CountryRepository()
        currencies_repo = CurrencyRateRepository()
        
        countries_count = len(await countries_repo.list_all(limit=1000))
        currencies_count = len(await currencies_repo.list_all(limit=1000))
        
        update_countries_count(countries_count)
        update_currency_rates_count(currencies_count)
        
        logger.info(f"Updated metrics: {countries_count} countries, {currencies_count} currency rates")
    except Exception as e:
        logger.error(f"Failed to update initial metrics: {e}")
    
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

# Add Prometheus monitoring middleware
app.add_middleware(PrometheusMiddleware)

app.include_router(countries.router, prefix="/api/v1/countries", tags=["countries"])
app.include_router(currencies.router, prefix="/api/v1/currencies", tags=["currencies"])
app.include_router(health.router, prefix="/api/v1/health", tags=["health"])


@app.get("/")
async def root():
    return {"message": "Countries Currency Service API", "version": settings.app_version}


@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)
