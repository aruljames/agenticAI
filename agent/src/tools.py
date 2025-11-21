import requests
from langchain.tools import tool

@tool
def get_coordinates(city_name: str) -> dict:
    """
    Fetches the latitude and longitude for a given city name.
    """
    url = "http://mcp_server:8001/geocode"
    try:
        response = requests.post(url, json={"city_name": city_name})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return {"error": "Could not fetch coordinates for the specified city."}

@tool
def get_weather_forecast(latitude: float, longitude: float) -> dict:
    """
    Fetches the weather forecast for a given latitude and longitude.
    """
    url = "http://mcp_server:8001/weather"
    try:
        response = requests.post(url, json={"latitude": latitude, "longitude": longitude})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException:
        return {"error": "Could not fetch weather forecast for the specified location."}
