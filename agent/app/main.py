from fastapi import FastAPI
from pydantic import BaseModel
from app.workflow import run_user_query
from app.session_store import get_or_create_session
from app.models import QueryRequest

app = FastAPI()

@app.post("/query")
async def process_query(req: QueryRequest):
    session = get_or_create_session(req.session_id)

    response = await run_user_query(req.user_query, session)

    return response
