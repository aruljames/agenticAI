import requests

def get_coordinates(city_name: str) -> dict:
    """
    Fetches the latitude and longitude for a given city name.

    Args:
        city_name (str): The name of the city.

    Returns:
        dict: A dictionary containing the latitude and longitude, or None if the request fails.
    """
    url = f"https://nominatim.openstreetmap.org/search?q={city_name}&format=json"
    try:
        response = requests.get(url, headers={'User-Agent': 'agentic-ai-app/1.0'})
        response.raise_for_status()  # Raise an exception for bad status codes
        data = response.json()
        if data:
            return {"latitude": data[0]["lat"], "longitude": data[0]["lon"]}
        else:
            return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching coordinates: {e}")
        return None

if __name__ == '__main__':
    # Example usage: Get the coordinates for a specific city
    city = "Berlin"
    coordinates = get_coordinates(city)
    if coordinates:
        print(coordinates)
