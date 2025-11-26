import httpx
import os
from app.langfuse_client import getClient

MCP_URL = os.getenv("MCP_SERVER_URL")

async def fetch_tools():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{MCP_URL}/tools")
        return r.json()

async def call_tool(name: str, params: dict):
    trace = getClient().trace(name="mcp_call_tool", input=params)
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.get(f"{MCP_URL}/tool/{name}", params=params)
            data = r.json()
            trace.update(output=data, status="completed")
            return data
    except Exception as e:
        trace.update(output=str(e), status="error")
        raise
