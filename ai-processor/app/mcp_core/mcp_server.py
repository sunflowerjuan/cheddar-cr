from fastmcp import FastMCP
import argparse
from app.mcp_core.tools.player_tools import players_tools
from app.mcp_core.tools.meta_tools import meta_tools


mcp = FastMCP('clash-royale')
players_tools(mcp)
meta_tools(mcp)


if __name__ == "__main__":
    
    print("Starting mcp server... ")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--server_type", type=str, default="sse", choices=["sse", "stdio"],
    )
    args = parser.parse_args()
    mcp.run(args.server_type, host="0.0.0.0", port=8000)


