
import os
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain.tools import tool
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from typing import TypedDict, Annotated, List, Union
import operator
from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.messages import BaseMessage
from dotenv import load_dotenv

load_dotenv()

# Define the state of the agent
class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]

@tool
def get_weather_forecast(latitude: float, longitude: float) -> dict:
    """
    Fetches the weather forecast for a given latitude and longitude.
    """
    from tools.weather import get_weather_forecast as fetch_weather
    return fetch_weather(latitude, longitude)

@tool
def get_coordinates(city_name: str) -> dict:
    """
    Fetches the latitude and longitude for a given city name.
    """
    from tools.geocoding import get_coordinates as fetch_coordinates
    return fetch_coordinates(city_name)

# Define the agent model
llm = ChatOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
tools = [get_weather_forecast, get_coordinates]
llm_with_tools = llm.bind_tools(tools)

# Define the agent node
def agent_node(state):
    response = llm_with_tools.invoke(state["messages"])
    if not isinstance(response.tool_calls, list) or not response.tool_calls:
        return {"messages": [AgentFinish(return_values={"output": response.content}, log=response.content)]}
    action = AgentAction(tool=response.tool_calls[0]['name'], tool_input=response.tool_calls[0]['args'], log=str(response.tool_calls))
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
    app = create_agent_graph().compile()
    inputs = [HumanMessage(content="what is the weather in berlin?")]
    result = app.invoke({"messages": inputs})
    print(result)
