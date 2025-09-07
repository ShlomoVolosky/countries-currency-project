from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from src.database.repositories import CountryRepository
from src.models.country import Country
from src.models.api import CountriesListResponse, APIResponse
from src.monitoring.metrics import track_countries_processed, track_api_call, update_countries_count

router = APIRouter()
repository = CountryRepository()


@router.get("/", response_model=CountriesListResponse)
async def get_countries(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    continent: Optional[str] = Query(default=None),
    un_member: Optional[bool] = Query(default=None)
):
    try:
        countries = await repository.list_all(limit=limit, offset=offset)
        
        if continent:
            countries = [c for c in countries if c.continent == continent]
        
        if un_member is not None:
            countries = [c for c in countries if c.is_un_member == un_member]
        
        return CountriesListResponse(
            success=True,
            message=f"Retrieved {len(countries)} countries",
            data=[country.model_dump() for country in countries]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve countries: {str(e)}")


@router.post("/process", response_model=APIResponse)
async def process_countries():
    """Trigger countries data processing"""
    try:
        from src.processors.countries import CountriesProcessor
        processor = CountriesProcessor()
        success = await processor.process()
        
        if success:
            # Get the actual count of countries processed
            from src.database.repositories import CountryRepository
            repo = CountryRepository()
            countries_count = len(await repo.list_all(limit=1000))
            track_countries_processed("success")
            update_countries_count(countries_count)
            track_api_call("countries_processor", "success")
            return APIResponse(
                success=True,
                message=f"Countries data processing completed successfully. Total countries: {countries_count}",
                data={"processed": True, "count": countries_count}
            )
        else:
            track_countries_processed("failed")
            track_api_call("countries_processor", "failed")
            raise HTTPException(status_code=500, detail="Countries data processing failed")
    except Exception as e:
        track_countries_processed("error")
        track_api_call("countries_processor", "error")
        raise HTTPException(status_code=500, detail=f"Failed to process countries: {str(e)}")


@router.post("/process-all", response_model=APIResponse)
async def process_countries_and_currencies():
    """Trigger combined countries and currencies data processing"""
    try:
        import asyncio
        from src.processors.countries import CountriesProcessor
        from src.processors.currencies import CurrencyProcessor
        
        # Process countries first
        countries_processor = CountriesProcessor()
        countries_success = await countries_processor.process()
        
        # Then process currencies
        currencies_processor = CurrencyProcessor()
        currencies_success = await currencies_processor.process()
        
        if countries_success and currencies_success:
            return APIResponse(
                success=True,
                message="Countries and currencies data processing completed successfully",
                data={"countries_processed": True, "currencies_processed": True}
            )
        else:
            raise HTTPException(
                status_code=500, 
                detail=f"Processing failed - Countries: {countries_success}, Currencies: {currencies_success}"
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to process countries and currencies: {str(e)}")


@router.get("/search/{country_name}", response_model=APIResponse)
async def search_country(country_name: str):
    try:
        country = await repository.get_by_name(country_name)
        if not country:
            raise HTTPException(status_code=404, detail="Country not found")
        
        return APIResponse(
            success=True,
            message="Country found",
            data=country.model_dump()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search country: {str(e)}")


@router.get("/{country_id}", response_model=APIResponse)
async def get_country(country_id: int):
    try:
        country = await repository.get_by_id(country_id)
        if not country:
            raise HTTPException(status_code=404, detail="Country not found")
        
        return APIResponse(
            success=True,
            message="Country retrieved successfully",
            data=country.model_dump()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve country: {str(e)}")

