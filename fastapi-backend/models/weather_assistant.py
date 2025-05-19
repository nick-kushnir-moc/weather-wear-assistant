from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import date

class WeatherDressRequest(BaseModel):
    """
    Request model for weather-based clothing recommendations
    """
    user_id: int
    location: str
    date: str  # Format: YYYY-MM-DD
    occasion: Optional[str] = None
    preferences: Optional[str] = None

class WeatherDressResponse(BaseModel):
    """
    Response model for weather-based clothing recommendations
    """
    date: str
    location: str
    weather_summary: str
    temperature: float
    conditions: str
    recommendations: Dict[str, Any]