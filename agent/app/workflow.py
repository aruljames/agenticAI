from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from app.llm import llm
from app.mcp_client import fetch_tools, call_tool
from app.session_store import update_session
from typing import Optional, Dict, Any, List
from pydantic import BaseModel
import json


class Message(BaseModel):
    role: str
    content: str


class AgentState(BaseModel):
    query: Optional[str] = None
    intent: Optional[str] = None
    selected_tool: Optional[str] = None

    required_params: Optional[Dict[str, Any]] = None
    collected_params: Optional[Dict[str, Any]] = None

    session_history: Optional[List[Message]] = None

    tool_output: Optional[Dict[str, Any]] = None

    # NEW FIELDS → required for workflow
    analysis: Optional[Dict[str, Any]] = None
    needs_more_input: bool = False
    tool_result: Optional[Dict[str, Any]] = None
    final: Optional[Any] = None


# -----------------------------
# NODE: Decide Intent
# -----------------------------
async def decide_intent(state: AgentState):
    query = state.query
    tools = await fetch_tools()

    prompt = f"""
    You are a tool-selection agent.
    User query: "{query}"

    Available tools:
    {tools}

    Decide:
    - intent (name of the tool)
    - relevant_tool
    - required_parameters
    - missing_parameters

    Return ONLY valid JSON in the EXACT format:

    {{
        "intent": "...",
        "relevant_tool": "... or null",
        "required_parameters": {{ }},
        "missing_parameters": []
    }}

    No explanation. No text outside JSON.
    """

    print("######### prompt =======> ", prompt)

    raw_output = await llm(prompt)
    print("######### LLM raw_output =======> ", raw_output)

    try:
        parsed = json.loads(raw_output)
    except:
        # If LLM returns garbage, fallback
        parsed = {
            "intent": None,
            "relevant_tool": None,
            "required_parameters": {},
            "missing_parameters": []
        }

    # Return a NEW updated state model (Pydantic requirement)
    new_state = state.model_copy(update={"analysis": parsed})
    return new_state


# -----------------------------
# NODE: Maybe Call Tool
# -----------------------------
async def maybe_call_tool(state: AgentState):
    analysis = state.analysis or {}
    print("######### maybe_call_tool =======> ", analysis)
    # Missing params?
    if analysis.get("missing_parameters"):
        return state.model_copy(update={
            "needs_more_input": True
        })
    print("##### 1")
    # No tool selected?
    if not analysis.get("relevant_tool"):
        return state.model_copy(update={"tool_result": None})
    print("##### 2")
    # Call the tool
    tool_name = analysis["relevant_tool"]
    params = analysis["required_parameters"]
    print("##### 3")
    tool_output = await call_tool(tool_name, params)
    print("##### 4")
    return state.model_copy(update={"tool_result": tool_output})


# -----------------------------
# NODE: Generate Final Response
# -----------------------------
async def generate_final_response(state: AgentState):
    query = state.query
    print("##### 5")
    # Ask for missing parameters
    if state.needs_more_input:
        missing = state.analysis.get("missing_parameters")
        return state.model_copy(update={
            "final": {
                "type": "ask_missing_parameters",
                "missing": missing
            }
        })
    print("##### 6")
    # Tool generated output
    if state.tool_result:
        print("##### 7")
        prompt = f"""
        User query: {query}
        Tool output: {state.tool_result}
        Summarize and generate JSON output.
        """

        response = await llm(prompt)
        print("##### 8", response)
        if isinstance(response, str):
            response = json.loads(response)
        return state.model_copy(update={"final": response})
    print("##### 9")
    # Fallback: direct answer
    llm_response = await llm(query)
    print("##### 10")
    return state.model_copy(update={"final": llm_response})


# -----------------------------
# Build LangGraph
# -----------------------------
builder = StateGraph(AgentState)

builder.add_node("decide_intent", decide_intent)
builder.add_node("maybe_call_tool", maybe_call_tool)
builder.add_node("generate_final_response", generate_final_response)

builder.set_entry_point("decide_intent")

builder.add_edge("decide_intent", "maybe_call_tool")
builder.add_edge("maybe_call_tool", "generate_final_response")
builder.add_edge("generate_final_response", END)

graph = builder.compile(checkpointer=MemorySaver())


# -----------------------------
# Run the Workflow
# -----------------------------
async def run_user_query(user_query: str, session_id: str):
    previous_state = session_id
    if previous_state and previous_state.get("intent"):
        state = AgentState(**previous_state)

        # User is providing missing parameters
        if state.analysis and state.analysis.get("missing_parameters"):
            missing = state.analysis["missing_parameters"]

            # Inject new user input into collected_params
            state.collected_params = state.collected_params or {}

            # Very simple parser: user_query = "city = Chennai"
            key, value = [x.strip() for x in user_query.split("=", 1)]
            if key in missing:
                state.collected_params[key] = value
                state.analysis["missing_parameters"].remove(key)

            # If now all params collected → go call tool
            if not state.analysis["missing_parameters"]:
                state.needs_more_input = False

        graph_input = state
    else:
        # First API call
        graph_input = AgentState(query=user_query)

    result = await graph.ainvoke(
        graph_input.model_dump(),
        config={"configurable": {"thread_id": session_id}}
    )

    # 3️⃣ Save updated state in MongoDB
    update_session(previous_state.get("session_id"), result)
    # 4️⃣ Return final response
    print("###### result ====>", result)
    return result.get("final")
