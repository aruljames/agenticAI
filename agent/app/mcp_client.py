import httpx
import os

MCP_URL = os.getenv("MCP_SERVER_URL")

async def fetch_tools():
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{MCP_URL}/tools")
        return r.json()

async def call_tool(name: str, params: dict):
    async with httpx.AsyncClient() as client:
        r = await client.get(f"{MCP_URL}/tool/{name}", params=params)
        return r.json()
