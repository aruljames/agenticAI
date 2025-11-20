import requests

def get_weather_forecast(latitude, longitude):
    """
    Fetches the weather forecast for a given latitude and longitude.

    Args:
        latitude (float): The latitude of the location.
        longitude (float): The longitude of the location.

    Returns:
        dict: A dictionary containing the weather forecast data, or None if the request fails.
    """
    url = f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current_weather=true"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for bad status codes
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching weather data: {e}")
        return None

if __name__ == '__main__':
    # Example usage: Get the weather forecast for a specific location
    latitude = 52.52
    longitude = 13.41
    forecast = get_weather_forecast(latitude, longitude)
    if forecast:
        print(forecast)
