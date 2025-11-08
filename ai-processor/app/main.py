import asyncio
from mcp_core.mcp_client import ClashRoyaleAssistant 

async def run_assistant():
    assistant = ClashRoyaleAssistant()
    await assistant.initialize_agent()
    await assistant.interactive_chat()

if __name__ == "__main__":
    asyncio.run(run_assistant())
