
import os
import requests
from langchain_openrouter import ChatOpenRouter
from langchain.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from typing import TypedDict, Annotated, List
import operator
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.messages import BaseMessage
from dotenv import load_dotenv

load_dotenv()

# Define the state of the agent
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]

MCP_SERVER_URL = "http://mcp_server:8001"

@tool
def get_weather_forecast(latitude: float, longitude: float) -> dict:
    """
    Fetches the weather forecast for a given latitude and longitude from the MCP server.
    """
    response = requests.post(f"{MCP_SERVER_URL}/weather", json={"latitude": latitude, "longitude": longitude})
    response.raise_for_status()
    return response.json()

@tool
def get_coordinates(city_name: str) -> dict:
    """
    Fetches the latitude and longitude for a given city name from the MCP server.
    """
    response = requests.post(f"{MCP_SERVER_URL}/geocode", json={"city_name": city_name})
    response.raise_for_status()
    return response.json()

# Define the agent model
llm = ChatOpenRouter()
tools = [get_weather_forecast, get_coordinates]
llm_with_tools = llm.bind_tools(tools)

# Define the agent node
def agent_node(state):
    response = llm_with_tools.invoke(state["messages"])
    if not isinstance(response.tool_calls, list) or not response.tool_calls:
        # If there are no tool calls, we return an AgentFinish object with the response content.
        return {"messages": [AgentFinish(return_values={"output": response.content}, log=response.content)]}
    # Otherwise, we create an AgentAction object for the first tool call.
    tool_call = response.tool_calls[0]
    action = AgentAction(tool=tool_call['name'], tool_input=tool_call['args'], log=str(tool_call))
    return {"messages": [action]}

# Define the graph
def create_agent_graph():
    graph = StateGraph(AgentState)
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(tools))
    graph.set_entry_point("agent")

    def should_continue(state):
        if isinstance(state["messages"][-1], AgentFinish):
            return "end"
        return "continue"

    graph.add_conditional_edges(
        "agent",
        should_continue,
        {
            "continue": "tools",
            "end": END,
        },
    )
    graph.add_edge("tools", "agent")
    return graph

if __name__ == "__main__":
    from langchain_core.messages import HumanMessage
    # This part is for local testing and will not work without the MCP server running.
    # To test, you would need to run the MCP server first.
    print("This script is intended to be run as part of the Docker Compose setup.")
    print("To test the agent, run the entire application with 'docker-compose up'.")

    # The following code is for demonstration purposes and will likely fail if run directly
    # without the MCP server being accessible.
    try:
        app = create_agent_graph().compile()
        inputs = [HumanMessage(content="what is the weather in berlin?")]
        result = app.invoke({"messages": inputs})
        print(result)
    except Exception as e:
        print(f"Encountered an error during local testing: {e}")
        print("This is expected if the MCP server is not running and accessible.")
