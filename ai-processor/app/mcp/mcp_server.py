from mcp.server.fastmcp import FastMCP
import argparse
from tools.player_tools import players_tools

mcp = FastMCP('clash-royale')
players_tools(mcp)


if __name__ == "__main__":
    
    print("Starting mcp server... ")

    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--server_type", type=str, default="sse", choices=["sse", "stdio"],
    )
    args = parser.parse_args()
    mcp.run(args.server_type)

