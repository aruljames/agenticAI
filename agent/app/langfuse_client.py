import os
from langfuse import Langfuse

# Langfuse client
langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST", "http://langfuse-server:3000"),
)

def getClient():
    global langfuse
    return langfuse