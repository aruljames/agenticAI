from fastapi import FastAPI
from pydantic import BaseModel
from tools.geocoding import get_coordinates
from tools.weather import get_weather_forecast

app = FastAPI()

class GeocodeRequest(BaseModel):
    city_name: str

class WeatherRequest(BaseModel):
    latitude: float
    longitude: float

@app.post("/geocode")
async def geocode(request: GeocodeRequest):
    return get_coordinates(request.city_name)

@app.post("/weather")
async def weather(request: WeatherRequest):
    return get_weather_forecast(request.latitude, request.longitude)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
