from langchain_openrouter import ChatOpenRouter
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.utils.function_calling import format_tool_to_openai_function
from langgraph.prebuilt import ToolExecutor
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolInvocation
from langchain_core.messages import FunctionMessage, BaseMessage
from typing import TypedDict, Annotated, Sequence
import operator
import json
from os import getenv
from .tools import get_coordinates, get_weather_forecast

def create_agent_graph():
    """
    Creates the agent graph.
    """
    tools = [get_coordinates, get_weather_forecast]
    tool_executor = ToolExecutor(tools)

    model = ChatOpenRouter(
        model_name=getenv("MODEL_NAME", "google/gemini-flash-1.5"),
        temperature=0.0
    )

    functions = [format_tool_to_openai_function(t) for t in tools]
    model = model.bind_functions(functions)

    class AgentState(TypedDict):
        messages: Annotated[Sequence[BaseMessage], operator.add]

    def should_continue(state):
        messages = state['messages']
        last_message = messages[-1]
        if "function_call" not in last_message.additional_kwargs:
            return "end"
        else:
            return "continue"

    def call_model(state):
        messages = state['messages']
        response = model.invoke(messages)
        return {"messages": [response]}

    def call_tool(state):
        messages = state['messages']
        last_message = messages[-1]
        action = ToolInvocation(
            tool=last_message.additional_kwargs["function_call"]["name"],
            tool_input=json.loads(last_message.additional_kwargs["function_call"]["arguments"])
        )
        response = tool_executor.invoke(action)
        function_message = FunctionMessage(content=str(response), name=action.tool)
        return {"messages": [function_message]}

    workflow = StateGraph(AgentState)

    workflow.add_node("agent", call_model)
    workflow.add_node("action", call_tool)

    workflow.set_entry_point("agent")

    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "continue": "action",
            "end": END
        }
    )

    workflow.add_edge('action', 'agent')

    return workflow
