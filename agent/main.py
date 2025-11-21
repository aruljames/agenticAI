from fastapi import FastAPI
from pydantic import BaseModel
from src.agent import create_agent_graph
from langchain_core.messages import HumanMessage

app = FastAPI()
agent = create_agent_graph().compile()

class UserRequest(BaseModel):
    intent: str

@app.post("/invoke")
async def invoke(request: UserRequest):
    inputs = [HumanMessage(content=request.intent)]
    result = agent.invoke({"messages": inputs})
    return {"response": result['messages'][-1].content}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
