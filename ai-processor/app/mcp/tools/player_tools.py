import logging
from .tool_utils import APIConnector as api
from utils.logger import get_logger
logger = get_logger(__name__)


def players_tools(mcp):
    """
    Collect all clash royale data from data-collector API.
    
    Args:
        mcp: The FastMCP server instance
    """
    api()
    @mcp.tool()
    def get_player_data(player_tag: str) -> dict:
        """
        Fetch player data from the Clash Royale data-collector API. A player tag must be provided to look up a player.

        Args:
            player_tag: The player tag to look up (e.g. #ABCDEF). This should either be provided by the user in the
            format of a string with a leading '#', or retrieved as a part of a reponse from a different tool.
            
        Returns:
            Player data pre-procesed including stats, cards, etc. The following is some mock data of the player info response:
            
            {
                "tag": "#9GQYJJR",
                "name": "Player Name",
                "level": 50,
                "trophies": 1234,
                "arena": "Arena Name",
                "cards": {
                    "allCards": [
                        {
                            "level": 1,
                            "name": "card name"
                        }
                    ],
                    "currentDeck": [
                        {
                            "level": 8,
                            "name": "card name"
                        },
                    ]
                },
                "performance": {
                    "battles": 2938,
                    "losses": 1309,
                    "win_rate": 55.45,
                    "wins": 1629
                },
                "previousSeason": {
                    "bestTrophies": null,
                    "trophies": null
                }
            },
        """
        logger.info(f"get_player_info called with player_tag: {player_tag}")
                
        result = api.get_player_data(player_tag)
        logger.info(f"get_player_info completed successfully for player: {result.get('name', 'Unknown')}")
        return result

    @mcp.tool()
    def get_player_battle_log(player_tag: str) -> dict:
        """
        Fetch battle log for a player from the Clash Royale data-collector API. A player tag must be provided to look up a player.
        
        Args:
            player_tag: The player tag to look up (e.g. #ABCDEF). This should either be provided by the user in the
            format of a string with a leading '#', or retrieved as a part of a reponse from a different tool.
    
        Returns:
            Battle log information including the battle details. Details returned include the gamemode, details about the
            cards in each player's deck and the outcome. The following is some mock data of the log info response:
            
            
        """
        logger.info(f"get_player_battle_log called with player_tag: {player_tag}")
        
        result = api.get_battle_log(player_tag)
        logger.info(f"get_player_battle_log completed successfully. Found {len(result)} battles")
        return result