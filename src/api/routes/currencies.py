from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from datetime import date
from src.database.repositories import CurrencyRateRepository
from src.models.currency import CurrencyRate
from src.models.api import CurrencyRatesResponse, APIResponse
from src.monitoring.metrics import track_currency_rates_processed, track_api_call

router = APIRouter()
repository = CurrencyRateRepository()


@router.get("/", response_model=CurrencyRatesResponse)
async def get_currency_rates(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    currency_code: Optional[str] = Query(default=None),
    country_name: Optional[str] = Query(default=None)
):
    try:
        rates = await repository.list_all(limit=limit, offset=offset)
        
        if currency_code:
            rates = [r for r in rates if r.currency_code == currency_code.upper()]
        
        if country_name:
            rates = [r for r in rates if r.country_name.lower() == country_name.lower()]
        
        return CurrencyRatesResponse(
            success=True,
            message=f"Retrieved {len(rates)} currency rates",
            data=[rate.model_dump() for rate in rates]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve currency rates: {str(e)}")


@router.get("/latest", response_model=CurrencyRatesResponse)
async def get_latest_rates():
    try:
        rates = await repository.get_latest_rates()
        
        return CurrencyRatesResponse(
            success=True,
            message=f"Retrieved {len(rates)} latest currency rates",
            data=[rate.model_dump() for rate in rates]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve latest rates: {str(e)}")


@router.post("/process", response_model=APIResponse)
async def process_currencies():
    """Trigger currencies data processing"""
    try:
        from src.processors.currencies import CurrencyProcessor
        processor = CurrencyProcessor()
        success = await processor.process()
        
        if success:
            track_currency_rates_processed("success")
            track_api_call("currency_processor", "success")
            return APIResponse(
                success=True,
                message="Currencies data processing completed successfully",
                data={"processed": True}
            )
        else:
            track_currency_rates_processed("failed")
            track_api_call("currency_processor", "failed")
            raise HTTPException(status_code=500, detail="Currencies data processing failed")
    except Exception as e:
        track_currency_rates_processed("error")
        track_api_call("currency_processor", "error")
        raise HTTPException(status_code=500, detail=f"Failed to process currencies: {str(e)}")


@router.get("/convert/{currency_code}", response_model=APIResponse)
async def convert_to_ils(currency_code: str, amount: float = Query(default=1.0, ge=0.01)):
    try:
        rates = await repository.get_latest_rates()
        target_rate = next((r for r in rates if r.currency_code == currency_code.upper()), None)
        
        if not target_rate:
            raise HTTPException(status_code=404, detail=f"Currency {currency_code} not found")
        
        ils_amount = float(amount * float(target_rate.shekel_rate))
        
        return APIResponse(
            success=True,
            message="Conversion successful",
            data={
                "from_currency": currency_code.upper(),
                "to_currency": "ILS",
                "amount": amount,
                "rate": float(target_rate.shekel_rate),
                "result": ils_amount
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to convert currency: {str(e)}")


@router.get("/{rate_id}", response_model=APIResponse)
async def get_currency_rate(rate_id: int):
    try:
        rate = await repository.get_by_id(rate_id)
        if not rate:
            raise HTTPException(status_code=404, detail="Currency rate not found")
        
        return APIResponse(
            success=True,
            message="Currency rate retrieved successfully",
            data=rate.model_dump()
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve currency rate: {str(e)}")

