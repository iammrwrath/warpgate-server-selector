"""
Game Profiles & Multi-Binary Auto-Detection Engine for WARPGATE.
Discovers ALL existing installations of a game (Battle.net AND Steam simultaneously).
"""
import os
from typing import Dict, List, Optional

GAME_PROFILES = {
    "Overwatch 2": {
        "tag": "OW2",
        "search_paths": [
            r"E:\SteamLibrary\steamapps\common\Overwatch\Overwatch.exe",
            r"C:\Program Files (x86)\Steam\steamapps\common\Overwatch\Overwatch.exe",
            r"D:\SteamLibrary\steamapps\common\Overwatch\Overwatch.exe",
            r"F:\SteamLibrary\steamapps\common\Overwatch\Overwatch.exe",
            r"E:\Overwatch\_retail_\Overwatch.exe",
            r"C:\Program Files (x86)\Overwatch\_retail_\Overwatch.exe",
            r"D:\Overwatch\_retail_\Overwatch.exe",
            r"F:\Overwatch\_retail_\Overwatch.exe",
        ]
    },
    "Battlefield 2042 / 6": {
        "tag": "BF",
        "search_paths": [
            r"C:\Program Files (x86)\Steam\steamapps\common\Battlefield 2042\BF2042.exe",
            r"D:\SteamLibrary\steamapps\common\Battlefield 2042\BF2042.exe",
            r"E:\SteamLibrary\steamapps\common\Battlefield 2042\BF2042.exe",
            r"C:\Program Files\EA Games\Battlefield 2042\BF2042.exe",
            r"D:\EA Games\Battlefield 2042\BF2042.exe",
            r"E:\EA Games\Battlefield 2042\BF2042.exe",
            r"C:\Program Files (x86)\Steam\steamapps\common\Battlefield 6\BF6.exe",
            r"D:\SteamLibrary\steamapps\common\Battlefield 6\BF6.exe",
            r"E:\SteamLibrary\steamapps\common\Battlefield 6\BF6.exe",
            r"C:\Program Files\EA Games\Battlefield 6\BF6.exe",
            r"D:\EA Games\Battlefield 6\BF6.exe",
            r"E:\EA Games\Battlefield 6\BF6.exe",
        ]
    },
    "Apex Legends": {
        "tag": "APEX",
        "search_paths": [
            r"C:\Program Files (x86)\Steam\steamapps\common\Apex Legends\r5apex.exe",
            r"D:\SteamLibrary\steamapps\common\Apex Legends\r5apex.exe",
            r"E:\SteamLibrary\steamapps\common\Apex Legends\r5apex.exe",
            r"C:\Program Files\EA Games\Apex\r5apex.exe",
            r"D:\EA Games\Apex\r5apex.exe",
            r"E:\EA Games\Apex\r5apex.exe",
        ]
    },
    "Marvel Rivals": {
        "tag": "RIVALS",
        "search_paths": [
            r"C:\Program Files (x86)\Steam\steamapps\common\MarvelRivals\Marvel-Win64-Shipping.exe",
            r"D:\SteamLibrary\steamapps\common\MarvelRivals\Marvel-Win64-Shipping.exe",
            r"E:\SteamLibrary\steamapps\common\MarvelRivals\Marvel-Win64-Shipping.exe",
        ]
    },
    "All Games (Global Mode)": {
        "tag": "GLOBAL",
        "search_paths": []
    }
}

def get_all_game_executables(game_name: str) -> List[str]:
    """Finds ALL valid installed executables for this game (both Steam and Battle.net/EA)."""
    profile = GAME_PROFILES.get(game_name)
    if not profile or not profile["search_paths"]:
        return []
    
    found = []
    for path in profile["search_paths"]:
        if os.path.exists(path) and path not in found:
            found.append(path)
    return found
