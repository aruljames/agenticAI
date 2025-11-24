from fastapi import FastAPI
import requests
from duckduckgo_search import DDGS
import os
import httpx

app = FastAPI()

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

@app.get("/tools")
def get_tools():
    return {
        "tools": [
            {
                "name": "web_search",
                "required_params": ["query"],
                "description": "Search the web using DuckDuckGo"
            },
            {
                "name": "weather_forecast",
                "required_params": ["city"],
                "description": "Get weather forecast for a city"
            }
        ]
    }

@app.get("/tool/web_search")
def tool_search(query: str):
    with DDGS() as ddgs:
        results = ddgs.text(query, max_results=5)
    return {"results": results}

@app.get("/tool/weather_forecast")
def weather(city: str):
    # Step 1: Convert city → coordinates
    geo_url = "https://geocoding-api.open-meteo.com/v1/search"
    geo_resp = httpx.get(geo_url, params={
        "name": city,
        "count": 1
    }).json()

    if not geo_resp.get("results"):
        return {"error": f"City '{city}' not found"}

    r = geo_resp["results"][0]
    lat, lon = r["latitude"], r["longitude"]

    # Step 2: Fetch weather
    weather_url = "https://api.open-meteo.com/v1/forecast"
    weather_resp = httpx.get(weather_url, params={
        "latitude": lat,
        "longitude": lon,
        "current_weather": "true"
    }).json()

    if "current_weather" not in weather_resp:
        return {"error": "Weather data unavailable"}

    cw = weather_resp["current_weather"]

    return {
        "city": city,
        "latitude": lat,
        "longitude": lon,
        "temperature": cw["temperature"],
        "windspeed": cw["windspeed"],
        "weathercode": cw["weathercode"],
        "time": cw["time"]
    }