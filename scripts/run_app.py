#!/usr/bin/env python3
import uvicorn
from src.config.settings import get_settings

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "src.api.app:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.logging.level.lower()
    )
