"""
Game Profiles & Auto-Detection Engine for Multi-Game Server Selector.
Supports Overwatch 2, Battlefield 2042 / Battlefield 6, Apex Legends, Marvel Rivals, and generic routing.
"""
import os
import glob
from typing import Dict, List, Optional

GAME_PROFILES = {
    "Overwatch 2": {
        "tag": "OW2",
        "udp_only": True,
        "default_ports": "12000-64000",
        "search_paths": [
            r"C:\Program Files (x86)\Overwatch\_retail_\Overwatch.exe",
            r"D:\Overwatch\_retail_\Overwatch.exe",
            r"E:\Overwatch\_retail_\Overwatch.exe",
            r"F:\Overwatch\_retail_\Overwatch.exe",
            r"C:\Program Files (x86)\Steam\steamapps\common\Overwatch\Overwatch.exe",
            r"D:\SteamLibrary\steamapps\common\Overwatch\Overwatch.exe",
            r"E:\SteamLibrary\steamapps\common\Overwatch\Overwatch.exe",
            r"F:\SteamLibrary\steamapps\common\Overwatch\Overwatch.exe",
        ],
        "default_ip_folder": "ip_lists"
    },
    "Battlefield 2042 / 6": {
        "tag": "BF",
        "udp_only": True,
        "default_ports": "All",
        "search_paths": [
            r"C:\Program Files\EA Games\Battlefield 2042\BF2042.exe",
            r"D:\EA Games\Battlefield 2042\BF2042.exe",
            r"E:\EA Games\Battlefield 2042\BF2042.exe",
            r"C:\Program Files (x86)\Steam\steamapps\common\Battlefield 2042\BF2042.exe",
            r"D:\SteamLibrary\steamapps\common\Battlefield 2042\BF2042.exe",
            r"E:\SteamLibrary\steamapps\common\Battlefield 2042\BF2042.exe",
            r"C:\Program Files\EA Games\Battlefield 6\BF6.exe",
            r"D:\EA Games\Battlefield 6\BF6.exe",
            r"E:\EA Games\Battlefield 6\BF6.exe",
            r"C:\Program Files (x86)\Steam\steamapps\common\Battlefield 6\BF6.exe",
            r"D:\SteamLibrary\steamapps\common\Battlefield 6\BF6.exe",
            r"E:\SteamLibrary\steamapps\common\Battlefield 6\BF6.exe",
        ],
        "default_ip_folder": "ip_lists"
    },
    "Apex Legends": {
        "tag": "APEX",
        "udp_only": True,
        "default_ports": "All",
        "search_paths": [
            r"C:\Program Files\EA Games\Apex\r5apex.exe",
            r"D:\EA Games\Apex\r5apex.exe",
            r"E:\EA Games\Apex\r5apex.exe",
            r"C:\Program Files (x86)\Steam\steamapps\common\Apex Legends\r5apex.exe",
            r"D:\SteamLibrary\steamapps\common\Apex Legends\r5apex.exe",
            r"E:\SteamLibrary\steamapps\common\Apex Legends\r5apex.exe",
        ],
        "default_ip_folder": "ip_lists"
    },
    "Marvel Rivals": {
        "tag": "RIVALS",
        "udp_only": True,
        "default_ports": "All",
        "search_paths": [
            r"C:\Program Files (x86)\Steam\steamapps\common\MarvelRivals\Marvel-Win64-Shipping.exe",
            r"D:\SteamLibrary\steamapps\common\MarvelRivals\Marvel-Win64-Shipping.exe",
            r"E:\SteamLibrary\steamapps\common\MarvelRivals\Marvel-Win64-Shipping.exe",
        ],
        "default_ip_folder": "ip_lists"
    },
    "All Games (Global Firewall)": {
        "tag": "GLOBAL",
        "udp_only": True,
        "default_ports": "All",
        "search_paths": [],
        "default_ip_folder": "ip_lists"
    }
}

def detect_game_executable(game_name: str) -> Optional[str]:
    profile = GAME_PROFILES.get(game_name)
    if not profile or not profile["search_paths"]:
        return None
    for path in profile["search_paths"]:
        if os.path.exists(path):
            return path
    return None
