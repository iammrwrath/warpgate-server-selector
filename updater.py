"""
WARPGATE In-App Auto-Updater Module
Checks GitHub Releases API (iammrwrath/warpgate-server-selector) for the latest version.
Handles download with progress callback, batch self-replacement script, and application restart.
"""
import os
import sys
import json
import tempfile
import threading
import urllib.request
from typing import Optional, Tuple, Callable

CURRENT_VERSION = "v6.0.0"
REPO_OWNER = "iammrwrath"
REPO_NAME = "warpgate-server-selector"
RELEASES_API_URL = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/releases"

def parse_semver(v: str) -> Tuple[int, ...]:
    """Converts a tag like 'v6.0.1' or '6.0.0' into a comparable tuple (6, 0, 1)."""
    clean = v.strip().lstrip('vV')
    parts = []
    for x in clean.split('.'):
        digits = ''.join(c for c in x if c.isdigit())
        parts.append(int(digits) if digits else 0)
    return tuple(parts)

class UpdateManager:
    @staticmethod
    def check_for_updates() -> Tuple[bool, Optional[str], Optional[str], int, str]:
        """
        Queries GitHub API for the latest release.
        Returns: (update_available, tag_name, download_url, file_size, release_notes)
        """
        try:
            req = urllib.request.Request(
                RELEASES_API_URL,
                headers={"User-Agent": f"WARPGATE-App/{CURRENT_VERSION}"}
            )
            with urllib.request.urlopen(req, timeout=8) as resp:
                if resp.status != 200:
                    return False, None, None, 0, ""
                releases = json.loads(resp.read().decode('utf-8'))
                if not releases:
                    return False, None, None, 0, ""
                
                latest = releases[0]
                latest_tag = latest.get("tag_name", "")
                notes = latest.get("body", "")
                
                # Check if newer
                if parse_semver(latest_tag) > parse_semver(CURRENT_VERSION):
                    for asset in latest.get("assets", []):
                        name = asset.get("name", "")
                        if name.endswith(".exe"):
                            return True, latest_tag, asset.get("browser_download_url"), asset.get("size", 0), notes
                            
            return False, None, None, 0, ""
        except Exception as e:
            print(f"[UpdateManager] Update check error: {e}")
            return False, None, None, 0, ""

    @staticmethod
    def download_and_install_update(
        download_url: str,
        total_size: int,
        progress_callback: Callable[[float, str], None],
        completion_callback: Callable[[bool, str], None]
    ):
        """
        Downloads the new executable in chunks and executes a replacement script.
        """
        def _run():
            try:
                progress_callback(0.05, "Connecting to download server...")
                req = urllib.request.Request(
                    download_url,
                    headers={"User-Agent": f"WARPGATE-App/{CURRENT_VERSION}"}
                )
                
                temp_dir = tempfile.gettempdir()
                new_exe_path = os.path.join(temp_dir, "WARPGATE_Update.exe")
                
                downloaded = 0
                chunk_size = 65536
                
                with urllib.request.urlopen(req, timeout=30) as response, open(new_exe_path, 'wb') as out_file:
                    content_len = int(response.headers.get('Content-Length', total_size or 1))
                    while True:
                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        out_file.write(chunk)
                        downloaded += len(chunk)
                        pct = min(0.95, downloaded / content_len)
                        mb_done = downloaded / (1024 * 1024)
                        mb_total = content_len / (1024 * 1024)
                        progress_callback(pct, f"Downloading: {mb_done:.1f} MB / {mb_total:.1f} MB ({int(pct*100)}%)")

                progress_callback(1.0, "Download complete! Applying update...")
                
                # Current running executable path
                if getattr(sys, 'frozen', False):
                    current_exe = sys.executable
                else:
                    current_exe = os.path.abspath(sys.argv[0])

                # Create bat script to safely wait, replace current binary, and relaunch
                bat_path = os.path.join(temp_dir, "warpgate_apply_update.bat")
                with open(bat_path, "w", encoding="utf-8") as bat:
                    bat.write(f"""@echo off
chcp 65001 >nul
echo [WARPGATE Auto-Updater] Waiting for application to exit...
timeout /t 2 /nobreak >nul
:retry
move /y "{new_exe_path}" "{current_exe}" >nul 2>&1
if errorlevel 1 (
    timeout /t 1 /nobreak >nul
    goto retry
)
echo [WARPGATE Auto-Updater] Update applied! Relaunching...
start "" "{current_exe}"
del "%~f0"
""")

                completion_callback(True, bat_path)
            except Exception as e:
                completion_callback(False, str(e))

        threading.Thread(target=_run, daemon=True).start()
