import logging
import config
import re
from jsoncomment import JsonComment


def jsonc_configs() -> dict:
    """
    Read the JSONC configuration file
        Returns:
        The JSON configuration data
    """
    parse = JsonComment()
    with open("episodios/Configs.jsonc", "r") as f:
        data = f.read()
        json_data = parse.loads(data)
        return json_data



def completed_episode() -> bool:
    """
    Check if the episode is completed
        Returns:
        True if the episode is completed, False otherwise
    """
    Jsonc_Configs: dict = jsonc_configs()

    if Jsonc_Configs.get("episodes")[Jsonc_Configs.get("current_episode") - 1].get("completed") == True:
        print("Completed episode")
        return True
    else:
        print("Not completed episode")
        return False

def get_frame_interator_value() -> int:
    """
    Get the frame interator value from the JSON configuration
        Returns:
        The frame interator value
    """
    Jsonc_Configs: dict = jsonc_configs()
    frame_interator = Jsonc_Configs.get("episodes")[Jsonc_Configs.get("current_episode") - 1].get("frame_interator")
    
    return frame_interator
