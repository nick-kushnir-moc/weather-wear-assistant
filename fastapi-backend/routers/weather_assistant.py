from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List, Any, Optional
import logging
import requests
import json
import sys
import os
from dotenv import load_dotenv
import re
from datetime import datetime
from openai import OpenAI
from langchain_community.llms import OpenAI as LangchainOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

load_dotenv()

# Import the actual model classes, not the module
from models.weather_assistant import WeatherDressRequest, WeatherDressResponse
from db import get_db
from configs import config

# Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
stream_handler = logging.StreamHandler(sys.stdout)
log_formatter = logging.Formatter("%(asctime)s [%(processName)s: %(process)d] [%(threadName)s: %(thread)d] [%(levelname)s] %(name)s: %(message)s")
stream_handler.setFormatter(log_formatter)
logger.addHandler(stream_handler)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# API configurations
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", OPENAI_API_KEY)
WEATHER_API_KEY = os.getenv("WEATHER_API_KEY", "3a2fe0c82a733d1276bd991c1ba2cb76")  # Replace with your actual key
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/forecast"

# Initialize OpenAI client
openai_client = OpenAI(api_key=OPENAI_API_KEY)

# Initialize LangChain OpenAI client
langchain_openai = LangchainOpenAI(openai_api_key=OPENAI_API_KEY)

router = APIRouter(
    prefix="/api/weather-assistant",
    tags=["weather-assistant"],
)

@router.post("/dress-recommendation", response_model=WeatherDressResponse)
async def get_dress_recommendation(
    request: WeatherDressRequest, 
    db=Depends(get_db)
):
    """
    Get clothing recommendations based on weather forecast for a specific date
    """
    try:
        # 1. Get weather forecast for the specified location and date
        weather_data = await get_weather_forecast(request.location, request.date)
        
        # 2. Get user's clothing inventory from database or mock data
        user_clothes = get_user_clothes(db, request.user_id)
        
        # 3. Use OpenAI to generate clothing recommendations
        recommendations = get_clothing_recommendations(
            weather_data, 
            user_clothes,
            request.occasion,
            request.preferences
        )
        
        return WeatherDressResponse(
            date=request.date,
            location=request.location,
            weather_summary=weather_data["summary"],
            temperature=weather_data["temperature"],
            conditions=weather_data["conditions"],
            recommendations=recommendations
        )
    
    except Exception as e:
        logger.error(f"Error generating dress recommendations: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

async def get_weather_forecast(location: str, date: str) -> Dict[str, Any]:
    """
    Get weather forecast for a specific location and date from OpenWeatherMap API
    """
    try:
        # Convert date string to datetime
        target_date = datetime.strptime(date, "%Y-%m-%d")
        
        # Make API request to OpenWeatherMap
        params = {
            "q": location,
            "appid": WEATHER_API_KEY,
            "units": "metric"  # Use metric units (Celsius)
        }
        
        response = requests.get(WEATHER_API_URL, params=params)
        response.raise_for_status()
        
        forecast_data = response.json()
        
        # Find forecast for the target date (closest match to noon)
        target_forecast = None
        min_diff = float('inf')
        
        for forecast in forecast_data["list"]:
            forecast_datetime = datetime.fromtimestamp(forecast["dt"])
            
            # Check if this is the correct date
            if forecast_datetime.date() == target_date.date():
                # Find the forecast closest to noon
                hours_from_noon = abs(forecast_datetime.hour - 12)
                if hours_from_noon < min_diff:
                    min_diff = hours_from_noon
                    target_forecast = forecast
        
        if not target_forecast:
            # If no exact match, take the closest available forecast
            # (This would happen if the target date is beyond the 5-day forecast range)
            raise HTTPException(
                status_code=400, 
                detail=f"Weather forecast not available for {date}. Please choose a date within the next 5 days."
            )
        
        # Extract relevant weather information
        weather_data = {
            "temperature": target_forecast["main"]["temp"],
            "feels_like": target_forecast["main"]["feels_like"],
            "humidity": target_forecast["main"]["humidity"],
            "conditions": target_forecast["weather"][0]["main"],
            "description": target_forecast["weather"][0]["description"],
            "wind_speed": target_forecast["wind"]["speed"],
            "summary": f"{target_forecast['weather'][0]['main']} with temperature of {target_forecast['main']['temp']}°C"
        }
        
        return weather_data
    
    except requests.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving weather data: {str(e)}")

def get_user_clothes(db, user_id: int) -> Dict[str, Any]:
    """
    For the demo, we're using mock clothing inventory since your database schema 
    doesn't include a clothing table. In a production app, you'd create this table.
    """
    try:
        # Check if the user exists in the employees table
        cur = db.cursor()
        cur.execute('SELECT id, name FROM "employees" WHERE id = %s', (user_id,))
        user = cur.fetchone()
        cur.close()
        
        if not user:
            logger.warning(f"User ID {user_id} not found in employees table")
            # Continue with mock data anyway for demo purposes
        else:
            logger.info(f"Found user: {user[1]} (ID: {user[0]})")
        
        # Mock clothing inventory - in production, this would come from a user_clothes table
        mock_inventory = {
            "tops": [
                {"id": 1, "type": "t-shirt", "color": "white", "material": "cotton", "warmth": "light"},
                {"id": 2, "type": "sweater", "color": "gray", "material": "wool", "warmth": "warm"},
                {"id": 3, "type": "hoodie", "color": "black", "material": "cotton", "warmth": "medium"},
                {"id": 4, "type": "jacket", "color": "blue", "material": "denim", "warmth": "medium"},
                {"id": 5, "type": "coat", "color": "brown", "material": "wool", "warmth": "heavy"},
            ],
            "bottoms": [
                {"id": 1, "type": "jeans", "color": "blue", "material": "denim", "warmth": "medium"},
                {"id": 2, "type": "shorts", "color": "khaki", "material": "cotton", "warmth": "light"},
                {"id": 3, "type": "sweatpants", "color": "gray", "material": "cotton", "warmth": "medium"},
                {"id": 4, "type": "slacks", "color": "black", "material": "polyester", "warmth": "medium"},
            ],
            "footwear": [
                {"id": 1, "type": "sneakers", "color": "white", "material": "canvas", "warmth": "medium"},
                {"id": 2, "type": "boots", "color": "brown", "material": "leather", "warmth": "warm"},
                {"id": 3, "type": "sandals", "color": "brown", "material": "leather", "warmth": "light"},
            ],
            "accessories": [
                {"id": 1, "type": "hat", "color": "black", "material": "wool", "warmth": "warm"},
                {"id": 2, "type": "scarf", "color": "red", "material": "wool", "warmth": "warm"},
                {"id": 3, "type": "gloves", "color": "black", "material": "leather", "warmth": "warm"},
                {"id": 4, "type": "sunglasses", "color": "black", "material": "plastic", "warmth": "light"},
                {"id": 5, "type": "umbrella", "color": "blue", "material": "nylon", "warmth": "light"},
            ]
        }
        
        return mock_inventory
        
    except Exception as e:
        logger.error(f"Error fetching user clothes: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error fetching user clothes: {str(e)}")

def get_clothing_recommendations(weather_data: Dict[str, Any], user_clothes: Dict[str, Any], occasion: Optional[str] = None, preferences: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate clothing recommendations using OpenAI
    """
    # Construct the prompt for OpenAI
    prompt = f"""
    Generate clothing recommendations based on the following weather forecast and available clothing items.
    
    Weather forecast:
    - Temperature: {weather_data['temperature']}°C
    - Conditions: {weather_data['conditions']}
    - Description: {weather_data['description']}
    
    Available clothing items:
    {json.dumps(user_clothes, indent=2)}
    """
    
    # Add occasion if provided
    if occasion:
        prompt += f"\nOccasion: {occasion}"
    
    # Add preferences if provided
    if preferences:
        prompt += f"\nPreferences: {preferences}"
    
    prompt += """
    
    Provide clothing recommendations in the following format:
    1. A summary of the weather and how to dress for it
    2. Specific clothing items to wear from the available inventory
    3. Additional tips based on the weather conditions
    
    The response should be structured as a JSON object with the following format:
    {
        "summary": "A summary of the weather and general clothing advice",
        "outfit": {
            "top": ["item_id", "description"],
            "bottom": ["item_id", "description"],
            "footwear": ["item_id", "description"],
            "accessories": [["item_id", "description"], ...]
        },
        "tips": ["tip1", "tip2", ...]
    }
    """
    
    try:
        # Call OpenAI Chat API
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful fashion and weather assistant."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=800
        )
        
        # Extract the recommendations from the response
        recommendations_text = response.choices[0].message.content.strip()
        
        # Extract the JSON part if it's surrounded by markdown code blocks
        if "```json" in recommendations_text:
            recommendations_text = recommendations_text.split("```json")[1].split("```")[0].strip()
        elif "```" in recommendations_text:
            recommendations_text = recommendations_text.split("```")[1].split("```")[0].strip()
        
        # Parse the recommendations as JSON
        recommendations = json.loads(recommendations_text)
        return recommendations
    
    except json.JSONDecodeError:
        # If parsing fails, return a basic structure with the raw text
        return {
            "summary": recommendations_text,
            "outfit": {},
            "tips": []
        }
    except Exception as e:
        logger.error(f"Error generating clothing recommendations: {str(e)}", exc_info=True)
        return {
            "summary": f"Error generating recommendations: {str(e)}",
            "outfit": {},
            "tips": []
        }