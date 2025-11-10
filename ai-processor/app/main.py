# main.py
import asyncio
from mcp_core.mcp_worker import MCPWorker

async def main():
    worker = MCPWorker()
    await worker.run()

if __name__ == "__main__":
    asyncio.run(main())
