from fastapi import FastAPI
import requests
from duckduckgo_search import DDGS
import os

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

@app.get("/tool/weather")
def weather(city: str):
    url = f"https://api.weatherapi.com/v1/current.json?key={WEATHER_API_KEY}&q={city}"
    r = requests.get(url)
    return r.json()
