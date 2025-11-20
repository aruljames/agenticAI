# Agentic AI with LangGraph

This project is a Python application for an agentic AI using LangGraph. It includes an API that takes a user's intent and identifies the actual intent. The application also includes a weather tool that uses an open API to get weather forecasts based on user requests. The agent can take a city name as input and will use a geocoding service to find the coordinates.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

* Docker
* Docker Compose
* An OpenAI API key

### Installing

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   ```

2. **Create a `.env` file**

   Create a `.env` file in the root of the project and add your OpenAI API key to it:

   ```
   OPENAI_API_KEY=your-api-key
   ```

3. **Build the Docker image**

   ```bash
   docker-compose build
   ```

4. **Run the application**

   ```bash
   docker-compose up
   ```

The API will be running at `http://localhost:8000`.

## Usage

You can interact with the API by sending a POST request to the `/invoke` endpoint. The request body should be a JSON object with an `intent` key.

### Example

```bash
curl -X POST -H "Content-Type: application/json" -d '{"intent": "What is the weather in Berlin?"}' http://localhost:8000/invoke
```

This will return a JSON object with the weather forecast for Berlin.

## Built With

* [LangGraph](https://github.com/langchain-ai/langgraph) - The framework used to build the agentic AI
* [FastAPI](https://fastapi.tiangolo.com/) - The web framework used to build the API
* [Docker](https://www.docker.com/) - The containerization platform used to run the application
* [Nominatim](https://nominatim.openstreetmap.org/) - The geocoding service used to convert city names to coordinates
