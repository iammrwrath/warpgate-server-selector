"""
Game Profiles & Regional Datacenter Maps for WARPGATE Server Selector.
Contains exact, game-specific server regions, datacenters, and ping targets for:
- Overwatch 2 (Blizzard AS57976 + Google Cloud / AWS)
- Battlefield 2042 / Battlefield 6 (EA / i3D.net AS49544 + AWS)
- Apex Legends (Respawn / EA AWS + GCP)
- Marvel Rivals (NetEase / AWS GameLift)
- All Games (System-Wide Global Routing Mode)
"""
import os
from typing import Dict, List, Optional

GAME_CONFIGS = {
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
        ],
        "regions": {
            "NA Central (ORD1 / Chicago)": {
                "tag": "ORD1",
                "ping_host": "24.105.62.129",
                "file": "Ip_ranges_NA_central.txt",
                "desc": "Chicago, IL (Blizzard + GCP Central)"
            },
            "NA West (LAX1 / Los Angeles)": {
                "tag": "LAX1",
                "ping_host": "24.105.30.129",
                "file": "Ip_ranges_NA_West.txt",
                "desc": "Los Angeles, CA / Silicon Valley"
            },
            "NA East (GUE4 / Virginia)": {
                "tag": "GUE4",
                "ping_host": "137.221.72.1",
                "file": "Ip_ranges_NA_East.txt",
                "desc": "Sterling, VA / Ashburn (Blizzard + AWS)"
            },
            "Europe (Amsterdam / AMS1)": {
                "tag": "AMS1",
                "ping_host": "185.60.112.157",
                "file": "Ip_ranges_EU.txt",
                "desc": "Amsterdam, Netherlands (Blizzard EU Hub)"
            },
            "Europe (Paris / CDG1)": {
                "tag": "CDG1",
                "ping_host": "37.244.50.1",
                "file": "cfg - EU - France - CDG1.txt",
                "desc": "Paris, France"
            },
            "Europe (Frankfurt / GEW3)": {
                "tag": "GEW3",
                "ping_host": "35.198.64.1",
                "file": "cfg - EU - Germany 2 - GEW3.txt",
                "desc": "Frankfurt, Germany (GCP Europe-West3)"
            },
            "Middle East (Bahrain / MES1 / Dubai)": {
                "tag": "MES1",
                "ping_host": "157.175.0.1",
                "file": "Ip_ranges_ME.txt",
                "desc": "Bahrain / UAE / KSA (AWS Middle East)"
            },
            "Asia - Tokyo (GTK1)": {
                "tag": "GTK1",
                "ping_host": "59.153.40.1",
                "file": "Ip_ranges_AS_Japan.txt",
                "desc": "Tokyo, Japan"
            },
            "Asia - Seoul (ICN1 / GAN3)": {
                "tag": "GAN3",
                "ping_host": "211.234.110.1",
                "file": "Ip_ranges_AS_Korea.txt",
                "desc": "Seoul, South Korea"
            },
            "Asia - Taiwan (TPE1)": {
                "tag": "TPE1",
                "ping_host": "203.66.81.98",
                "file": "Ip_ranges_AS_Taiwan.txt",
                "desc": "Taipei, Taiwan (HiNet / Blizzard TW)"
            },
            "Asia - Singapore (GSG1)": {
                "tag": "GSG1",
                "ping_host": "103.4.114.1",
                "file": "Ip_ranges_AS_Singapore.txt",
                "desc": "Singapore (SE-Asia Hub)"
            },
            "Australia (SYD2 / Sydney)": {
                "tag": "SYD2",
                "ping_host": "137.221.81.1",
                "file": "Ip_ranges_Australia.txt",
                "desc": "Sydney, Australia"
            },
            "South America (GBR1 / São Paulo)": {
                "tag": "GBR1",
                "ping_host": "54.207.107.12",
                "file": "Ip_ranges_Brazil.txt",
                "desc": "São Paulo, Brazil"
            }
        }
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
        ],
        "regions": {
            "US East (Ashburn / Virginia)": {
                "tag": "US_EAST",
                "ping_host": "162.244.54.53",
                "file": "games/battlefield/BF_US_East.txt",
                "desc": "Virginia / Ashburn (i3D.net + AWS East)"
            },
            "US West (San Jose / Los Angeles)": {
                "tag": "US_WEST",
                "ping_host": "162.244.52.53",
                "file": "games/battlefield/BF_US_West.txt",
                "desc": "California / Oregon (i3D.net Bare Metal)"
            },
            "Europe (Frankfurt / Amsterdam)": {
                "tag": "EU_CENTRAL",
                "ping_host": "213.163.64.1",
                "file": "games/battlefield/BF_Europe.txt",
                "desc": "Frankfurt / Rotterdam (i3D HQ Main Hub)"
            },
            "Asia (Tokyo / Japan)": {
                "tag": "ASIA_TOKYO",
                "ping_host": "103.194.166.85",
                "file": "games/battlefield/BF_Asia_Tokyo.txt",
                "desc": "Tokyo Datacenter (i3D Asia-East)"
            },
            "Asia (Singapore)": {
                "tag": "ASIA_SINGAPORE",
                "ping_host": "213.179.200.53",
                "file": "games/battlefield/BF_Asia_Singapore.txt",
                "desc": "Singapore Datacenter (i3D SE-Asia)"
            },
            "Oceania (Sydney / Australia)": {
                "tag": "OCEANIA_SYDNEY",
                "ping_host": "109.200.215.1",
                "file": "games/battlefield/BF_Oceania_Sydney.txt",
                "desc": "Sydney, Australia (i3D Oceania)"
            },
            "South America (São Paulo)": {
                "tag": "SA_SAOPAULO",
                "ping_host": "185.197.24.1",
                "file": "games/battlefield/BF_South_America.txt",
                "desc": "São Paulo, Brazil"
            },
            "Middle East & South Africa": {
                "tag": "ME_AFRICA",
                "ping_host": "185.50.104.1",
                "file": "games/battlefield/BF_Middle_East_Africa.txt",
                "desc": "Dubai / Johannesburg Hubs"
            }
        }
    },
    "Apex Legends": {
        "tag": "APEX",
        "search_paths": [
            r"C:\Program Files (x86)\Steam\steamapps\common\Apex Legends\r5apex.exe",
            r"C:\Program Files (x86)\Steam\steamapps\common\Apex Legends\r5apex_dx12.exe",
            r"D:\SteamLibrary\steamapps\common\Apex Legends\r5apex.exe",
            r"D:\SteamLibrary\steamapps\common\Apex Legends\r5apex_dx12.exe",
            r"E:\SteamLibrary\steamapps\common\Apex Legends\r5apex.exe",
            r"E:\SteamLibrary\steamapps\common\Apex Legends\r5apex_dx12.exe",
            r"C:\Program Files\EA Games\Apex\r5apex.exe",
            r"C:\Program Files\EA Games\Apex\r5apex_dx12.exe",
            r"D:\EA Games\Apex\r5apex.exe",
            r"D:\EA Games\Apex\r5apex_dx12.exe",
            r"E:\EA Games\Apex\r5apex.exe",
            r"E:\EA Games\Apex\r5apex_dx12.exe",
        ],
        "regions": {
            "NA East (us-east-1 / Virginia)": {
                "tag": "US_EAST_1",
                "ping_host": "dynamodb.us-east-1.amazonaws.com",
                "file": "games/apex/APEX_US_East.txt",
                "desc": "N. Virginia / Ohio (AWS us-east)"
            },
            "NA West (us-west-2 / Oregon)": {
                "tag": "US_WEST_2",
                "ping_host": "dynamodb.us-west-2.amazonaws.com",
                "file": "games/apex/APEX_US_West.txt",
                "desc": "Oregon / N. California (AWS us-west)"
            },
            "Europe (eu-central-1 / Frankfurt)": {
                "tag": "EU_CENTRAL_1",
                "ping_host": "dynamodb.eu-central-1.amazonaws.com",
                "file": "games/apex/APEX_Europe.txt",
                "desc": "Frankfurt / London / Ireland (AWS Europe)"
            },
            "Asia - Tokyo (ap-northeast-1)": {
                "tag": "AP_NE_1",
                "ping_host": "dynamodb.ap-northeast-1.amazonaws.com",
                "file": "games/apex/APEX_Asia_Tokyo.txt",
                "desc": "Tokyo, Japan"
            },
            "Asia - Singapore (ap-southeast-1)": {
                "tag": "AP_SE_1",
                "ping_host": "dynamodb.ap-southeast-1.amazonaws.com",
                "file": "games/apex/APEX_Asia_Singapore.txt",
                "desc": "Singapore / Hong Kong"
            },
            "Oceania (ap-southeast-2 / Sydney)": {
                "tag": "AP_SE_2",
                "ping_host": "dynamodb.ap-southeast-2.amazonaws.com",
                "file": "games/apex/APEX_Australia_Sydney.txt",
                "desc": "Sydney, Australia"
            },
            "South America (sa-east-1 / São Paulo)": {
                "tag": "SA_EAST_1",
                "ping_host": "dynamodb.sa-east-1.amazonaws.com",
                "file": "games/apex/APEX_South_America.txt",
                "desc": "São Paulo, Brazil"
            },
            "Middle East (me-south-1 / Bahrain)": {
                "tag": "ME_SOUTH_1",
                "ping_host": "dynamodb.me-south-1.amazonaws.com",
                "file": "games/apex/APEX_Middle_East.txt",
                "desc": "Bahrain / UAE Cluster"
            }
        }
    },
    "Marvel Rivals": {
        "tag": "RIVALS",
        "search_paths": [
            r"C:\Program Files (x86)\Steam\steamapps\common\MarvelRivals\MarvelGame\Marvel\Binaries\Win64\Marvel-Win64-Shipping.exe",
            r"C:\Program Files (x86)\Steam\steamapps\common\MarvelRivals\MarvelGame\Marvel.exe",
            r"D:\SteamLibrary\steamapps\common\MarvelRivals\MarvelGame\Marvel\Binaries\Win64\Marvel-Win64-Shipping.exe",
            r"D:\SteamLibrary\steamapps\common\MarvelRivals\MarvelGame\Marvel.exe",
            r"E:\SteamLibrary\steamapps\common\MarvelRivals\MarvelGame\Marvel\Binaries\Win64\Marvel-Win64-Shipping.exe",
            r"E:\SteamLibrary\steamapps\common\MarvelRivals\MarvelGame\Marvel.exe",
        ],
        "regions": {
            "NA Central (Dallas / Ohio)": {
                "tag": "DALLAS",
                "ping_host": "dynamodb.us-east-2.amazonaws.com",
                "file": "games/rivals/RIVALS_US_Central_Dallas.txt",
                "desc": "Dallas / Ohio (NetEase Central Node)"
            },
            "NA East (Northern Virginia)": {
                "tag": "VA_EAST",
                "ping_host": "dynamodb.us-east-1.amazonaws.com",
                "file": "games/rivals/RIVALS_US_East_Virginia.txt",
                "desc": "Northern Virginia Hub"
            },
            "NA West (Oregon)": {
                "tag": "OREGON_WEST",
                "ping_host": "dynamodb.us-west-2.amazonaws.com",
                "file": "games/rivals/RIVALS_US_West_Oregon.txt",
                "desc": "Oregon / Pacific Northwest"
            },
            "Europe (Frankfurt / Warsaw)": {
                "tag": "FRANKFURT",
                "ping_host": "dynamodb.eu-central-1.amazonaws.com",
                "file": "games/rivals/RIVALS_Europe_Frankfurt.txt",
                "desc": "Frankfurt, Germany / Warsaw"
            },
            "Asia - Tokyo (Japan)": {
                "tag": "TOKYO",
                "ping_host": "dynamodb.ap-northeast-1.amazonaws.com",
                "file": "games/rivals/RIVALS_Asia_Tokyo.txt",
                "desc": "Tokyo Datacenter Cluster"
            },
            "Asia - Singapore": {
                "tag": "SINGAPORE",
                "ping_host": "dynamodb.ap-southeast-1.amazonaws.com",
                "file": "games/rivals/RIVALS_Asia_Singapore.txt",
                "desc": "Singapore Datacenter Cluster"
            },
            "Oceania (Sydney / Australia)": {
                "tag": "SYDNEY",
                "ping_host": "dynamodb.ap-southeast-2.amazonaws.com",
                "file": "games/rivals/RIVALS_Australia_Sydney.txt",
                "desc": "Sydney, Australia"
            },
            "South America (São Paulo)": {
                "tag": "SAOPAULO",
                "ping_host": "dynamodb.sa-east-1.amazonaws.com",
                "file": "games/rivals/RIVALS_South_America.txt",
                "desc": "São Paulo, Brazil"
            },
            "Middle East (Dammam / Bahrain)": {
                "tag": "DAMMAM",
                "ping_host": "dynamodb.me-south-1.amazonaws.com",
                "file": "games/rivals/RIVALS_Middle_East.txt",
                "desc": "Dammam, Saudi Arabia"
            }
        }
    },
    "All Games (Global Mode)": {
        "tag": "GLOBAL",
        "search_paths": [],
        "regions": {
            "North America Central (Chicago)": {
                "tag": "GLOBAL_ORD",
                "ping_host": "24.105.62.129",
                "file": "Ip_ranges_NA_central.txt",
                "desc": "Central North America"
            },
            "North America West (California)": {
                "tag": "GLOBAL_LAX",
                "ping_host": "24.105.30.129",
                "file": "Ip_ranges_NA_West.txt",
                "desc": "West Coast North America"
            },
            "North America East (Virginia)": {
                "tag": "GLOBAL_GUE",
                "ping_host": "dynamodb.us-east-1.amazonaws.com",
                "file": "Ip_ranges_NA_East.txt",
                "desc": "East Coast North America"
            },
            "Europe (Central / Amsterdam / Frankfurt)": {
                "tag": "GLOBAL_EU",
                "ping_host": "185.60.112.157",
                "file": "Ip_ranges_EU.txt",
                "desc": "European Datacenters"
            },
            "Asia - Tokyo": {
                "tag": "GLOBAL_TYO",
                "ping_host": "dynamodb.ap-northeast-1.amazonaws.com",
                "file": "Ip_ranges_AS_Japan.txt",
                "desc": "Tokyo, Japan"
            },
            "Asia - Singapore": {
                "tag": "GLOBAL_SIN",
                "ping_host": "dynamodb.ap-southeast-1.amazonaws.com",
                "file": "Ip_ranges_AS_Singapore.txt",
                "desc": "Southeast Asia"
            },
            "Oceania (Australia)": {
                "tag": "GLOBAL_SYD",
                "ping_host": "dynamodb.ap-southeast-2.amazonaws.com",
                "file": "Ip_ranges_Australia.txt",
                "desc": "Sydney, Australia"
            },
            "Middle East": {
                "tag": "GLOBAL_ME",
                "ping_host": "157.175.0.1",
                "file": "Ip_ranges_ME.txt",
                "desc": "Middle East & Gulf"
            }
        }
    }
}

# Alias for backwards compatibility
GAME_PROFILES = GAME_CONFIGS

def get_all_game_executables(game_name: str) -> List[str]:
    """Finds ALL valid installed executables for this game (both Steam and Battle.net/EA)."""
    profile = GAME_CONFIGS.get(game_name)
    if not profile or not profile.get("search_paths"):
        return []
    
    found = []
    for path in profile["search_paths"]:
        if os.path.exists(path) and path not in found:
            found.append(path)
    return found

def get_game_regions(game_name: str) -> Dict[str, dict]:
    """Returns the regional configuration map for the selected game."""
    profile = GAME_CONFIGS.get(game_name, {})
    return profile.get("regions", {})
