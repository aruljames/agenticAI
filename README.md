# Agentic AI with LangGraph and MCP Server

This project is a Python application for an agentic AI using LangGraph. It includes an API that takes a user's intent and identifies the actual intent. The application is split into two services: an `agent` service and a `mcp_server` service.

The `agent` service contains the LangGraph agent and the API that interacts with the user. The `mcp_server` service handles all external API calls, including geocoding and weather forecasting. The agent communicates with the `mcp_server` to get the data it needs.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

* Docker
* Docker Compose
* An OpenRouter API key

### Installing

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   ```

2. **Create a `.env` file**

   Create a `.env` file in the root of the project and add your OpenRouter API key to it:

   ```
   OPENROUTER_API_KEY=your-api-key
   ```

3. **Build the Docker images**

   ```bash
   docker-compose build
   ```

4. **Run the application**

   ```bash
   docker-compose up
   ```

The `agent` service will be running at `http://localhost:8000`, and the `mcp_server` service will be running at `http://localhost:8001`.

## Usage

You can interact with the API by sending a POST request to the `/invoke` endpoint on the `agent` service. The request body should be a JSON object with an `intent` key.

### Example

```bash
curl -X POST -H "Content-Type: application/json" -d '{"intent": "What is the weather in Berlin?"}' http://localhost:8000/invoke
```

This will return a JSON object with the weather forecast for Berlin.

## Built With

* [LangGraph](https://github.com/langchain-ai/langgraph) - The framework used to build the agentic AI
* [FastAPI](https://fastapi.tiangolo.com/) - The web framework used to build the API
* [Docker](https://www.docker.com/) - The containerization platform used to run the application
* [OpenRouter](https://openrouter.ai/) - The AI model router used by the agent, via the `langchain-openrouter` package
* [Nominatim](https://nominatim.openstreetmap.org/) - The geocoding service used to convert city names to coordinates
* [Open-Meteo](https://open-meteo.com/) - The weather service used to get weather forecasts
