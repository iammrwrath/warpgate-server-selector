"""
Modern Multi-Game Server Selector v6.5 (Portable Edition)
Supports:
- Overwatch 2
- Battlefield 2042 / Battlefield 6
- Apex Legends
- Marvel Rivals
- System-Wide Global Game Matchmaking Block

Key Fixes:
- Safe UDP-only filtering: Never blocks TCP login/auth/Battle.net/EA app servers (prevents "Time out communicating with Battle.net services" error).
- Executable auto-scoping: Automatically binds firewall rules to game .exe files.
"""
import sys
import os
import threading
from typing import Dict, List, Optional

import customtkinter as ctk
import pythonping

from firewall_engine import FirewallManager, is_admin
from game_profiles import GAME_PROFILES, get_all_game_executables
import sync_ip_ranges

def get_resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller bundle."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

# Region Definitions & Live Ping Targets (Shared across modern cloud datacenters GCP/AWS/EA/Blizzard)
REGIONS = {
    "NA Central (ORD1 / Chicago)": {
        "tag": "NA_central",
        "ping_host": "24.105.62.129",
        "file": "Ip_ranges_NA_central.txt",
        "desc": "Chicago / Central US (GCP/Blizzard)"
    },
    "NA West (LAX1 / Oregon / Silicon Valley)": {
        "tag": "NA_West",
        "ping_host": "24.105.30.129",
        "file": "Ip_ranges_NA_West.txt",
        "desc": "Los Angeles / Washington / AWS us-west"
    },
    "NA East (GUE4 / Virginia)": {
        "tag": "NA_East",
        "ping_host": "34.224.0.1",
        "file": "Ip_ranges_NA_East.txt",
        "desc": "Virginia / Ashburn (AWS us-east-1)"
    },
    "Europe (Amsterdam / Frankfurt / Finland)": {
        "tag": "EU",
        "ping_host": "185.60.112.157",
        "file": "Ip_ranges_EU.txt",
        "desc": "Amsterdam / Frankfurt / Paris"
    },
    "Middle East (Bahrain / Dubai / KSA)": {
        "tag": "ME",
        "ping_host": "dynamodb.me-south-1.amazonaws.com",
        "file": "Ip_ranges_ME.txt",
        "desc": "Bahrain / Qatar / Saudi Arabia"
    },
    "Asia - Tokyo (GTK1)": {
        "tag": "AS_Japan",
        "ping_host": "dynamodb.ap-northeast-1.amazonaws.com",
        "file": "Ip_ranges_AS_Japan.txt",
        "desc": "Tokyo, Japan"
    },
    "Asia - Seoul (ICN1 / GAN3)": {
        "tag": "AS_Korea",
        "ping_host": "211.234.110.1",
        "file": "Ip_ranges_AS_Korea.txt",
        "desc": "Seoul, South Korea"
    },
    "Asia - Singapore (GSG1)": {
        "tag": "AS_Singapore",
        "ping_host": "dynamodb.ap-southeast-1.amazonaws.com",
        "file": "Ip_ranges_AS_Singapore.txt",
        "desc": "Singapore (AWS / GCP SE-Asia)"
    },
    "Asia - Taiwan (TPE1)": {
        "tag": "AS_Taiwan",
        "ping_host": "203.66.81.98",
        "file": "Ip_ranges_AS_Taiwan.txt",
        "desc": "Taipei, Taiwan"
    },
    "Australia (SYD2 / Sydney)": {
        "tag": "Australia",
        "ping_host": "dynamodb.ap-southeast-2.amazonaws.com",
        "file": "Ip_ranges_Australia.txt",
        "desc": "Sydney, Australia"
    },
    "South America (GBR1 / São Paulo)": {
        "tag": "Brazil",
        "ping_host": "54.207.107.12",
        "file": "Ip_ranges_Brazil.txt",
        "desc": "São Paulo, Brazil"
    }
}

class UniversalServerSelectorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Universal PvP Server Selector (OW2, Battlefield, Apex)")
        self.geometry("860x700")
        self.minsize(820, 640)
        
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.selected_game = ctk.StringVar(value="Overwatch 2")
        self.detected_exe = ctk.StringVar(value="")
        self.selected_region = ctk.StringVar(value="UNBLOCKED")
        self.ipv6_enabled = ctk.BooleanVar(value=True)
        self.udp_only_mode = ctk.BooleanVar(value=True)
        self.ping_labels: Dict[str, ctk.CTkLabel] = {}
        self.status_var = ctk.StringVar(value="Status: Ready")

        self._create_layout()
        self._check_admin_privileges()
        self._on_game_change(self.selected_game.get())
        self.refresh_pings_async()

    def _create_layout(self):
        # Header banner
        header_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#1a1d24")
        header_frame.pack(fill="x", padx=15, pady=(15, 10))

        title_lbl = ctk.CTkLabel(
            header_frame, 
            text="⚡ UNIVERSAL PVP SERVER SELECTOR", 
            font=ctk.CTkFont(size=19, weight="bold"),
            text_color="#f99f1b"
        )
        title_lbl.pack(side="left", padx=15, pady=12)

        self.admin_lbl = ctk.CTkLabel(
            header_frame,
            text="Admin Status",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#888888"
        )
        self.admin_lbl.pack(side="right", padx=15)

        # Game Selection Bar
        game_bar = ctk.CTkFrame(self, corner_radius=8, fg_color="#21252b")
        game_bar.pack(fill="x", padx=15, pady=(0, 10))

        game_lbl = ctk.CTkLabel(game_bar, text="Target Game:", font=ctk.CTkFont(size=13, weight="bold"))
        game_lbl.pack(side="left", padx=(15, 8), pady=8)

        self.game_dropdown = ctk.CTkOptionMenu(
            game_bar,
            values=list(GAME_PROFILES.keys()),
            variable=self.selected_game,
            command=self._on_game_change,
            width=200
        )
        self.game_dropdown.pack(side="left", padx=5, pady=8)

        self.exe_status_lbl = ctk.CTkLabel(
            game_bar,
            textvariable=self.detected_exe,
            font=ctk.CTkFont(size=11),
            text_color="#7ee787"
        )
        self.exe_status_lbl.pack(side="left", padx=12, pady=8)

        # Main content area (Left: Region cards, Right: Controls & Options)
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=15, pady=0)

        # Region Selector (Left Panel)
        regions_frame = ctk.CTkScrollableFrame(
            content_frame, 
            label_text="Available Server Regions", 
            label_font=ctk.CTkFont(size=14, weight="bold")
        )
        regions_frame.pack(side="left", fill="both", expand=True, padx=(0, 10))

        for reg_name, meta in REGIONS.items():
            card = ctk.CTkFrame(regions_frame, corner_radius=6, fg_color="#282c34")
            card.pack(fill="x", pady=4, padx=5)

            radio = ctk.CTkRadioButton(
                card,
                text=reg_name,
                variable=self.selected_region,
                value=reg_name,
                font=ctk.CTkFont(size=13, weight="bold"),
                command=self._on_region_select
            )
            radio.pack(side="left", padx=10, pady=8)

            desc_lbl = ctk.CTkLabel(card, text=meta["desc"], font=ctk.CTkFont(size=11), text_color="#abb2bf")
            desc_lbl.pack(side="left", padx=5)

            p_lbl = ctk.CTkLabel(card, text="-- ms", font=ctk.CTkFont(size=12, weight="bold"), text_color="#5c6370")
            p_lbl.pack(side="right", padx=10)
            self.ping_labels[reg_name] = p_lbl

        # Action & Settings Panel (Right Panel)
        actions_frame = ctk.CTkFrame(content_frame, width=280, corner_radius=8, fg_color="#21252b")
        actions_frame.pack(side="right", fill="y", padx=0)

        ctrl_title = ctk.CTkLabel(actions_frame, text="Firewall Controls", font=ctk.CTkFont(size=15, weight="bold"))
        ctrl_title.pack(pady=(12, 8), padx=10)

        # Lock / Unlock buttons
        self.lock_btn = ctk.CTkButton(
            actions_frame,
            text="🔒 Lock Selected Region",
            fg_color="#2ea043",
            hover_color="#3fb950",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.lock_server
        )
        self.lock_btn.pack(fill="x", padx=15, pady=6)

        self.block_me_btn = ctk.CTkButton(
            actions_frame,
            text="🚫 Block Middle East Only",
            fg_color="#cf222e",
            hover_color="#da3633",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.block_me_server
        )
        self.block_me_btn.pack(fill="x", padx=15, pady=6)

        self.unlock_btn = ctk.CTkButton(
            actions_frame,
            text="🔓 Reset / Unblock All",
            fg_color="#30363d",
            hover_color="#484f58",
            font=ctk.CTkFont(size=13),
            command=self.unlock_all
        )
        self.unlock_btn.pack(fill="x", padx=15, pady=6)

        # Separator
        sep = ctk.CTkFrame(actions_frame, height=2, fg_color="#30363d")
        sep.pack(fill="x", padx=15, pady=12)

        # Safety & Protocol Options
        opt_lbl = ctk.CTkLabel(actions_frame, text="Safety & Game Traffic", font=ctk.CTkFont(size=13, weight="bold"))
        opt_lbl.pack(anchor="w", padx=15, pady=(0, 4))

        udp_cb = ctk.CTkCheckBox(
            actions_frame, 
            text="UDP Only (Protects Login/Auth)", 
            variable=self.udp_only_mode
        )
        udp_cb.pack(anchor="w", padx=15, pady=4)

        v6_cb = ctk.CTkCheckBox(
            actions_frame, 
            text="Block IPv6 Traffic", 
            variable=self.ipv6_enabled
        )
        v6_cb.pack(anchor="w", padx=15, pady=4)

        # Ping Button
        self.ping_btn = ctk.CTkButton(
            actions_frame,
            text="🔄 Refresh Pings",
            fg_color="#1f6feb",
            hover_color="#388bfd",
            command=self.refresh_pings_async
        )
        self.ping_btn.pack(fill="x", padx=15, pady=8)

        # Sync IP ranges button
        self.sync_btn = ctk.CTkButton(
            actions_frame,
            text="🌐 Update IP Datacenter List",
            fg_color="#21262d",
            hover_color="#30363d",
            border_width=1,
            border_color="#484f58",
            command=self.sync_ip_ranges_async
        )
        self.sync_btn.pack(fill="x", padx=15, pady=8)

        # Status Bar at bottom
        self.status_bar = ctk.CTkLabel(
            self,
            textvariable=self.status_var,
            font=ctk.CTkFont(size=12),
            text_color="#8b949e",
            anchor="w"
        )
        self.status_bar.pack(fill="x", padx=20, pady=(6, 10))

    def _on_game_change(self, game_name: str):
        exes = get_all_game_executables(game_name)
        if exes:
            names = [os.path.basename(os.path.dirname(os.path.dirname(e))) or os.path.basename(e) for e in exes]
            self.detected_exe.set(f"✓ Bound to {len(exes)} executable(s): {', '.join(names)}")
        else:
            if game_name == "All Games (Global Mode)":
                self.detected_exe.set("● Applies to all outbound traffic")
            else:
                self.detected_exe.set("▲ Not found in standard paths (system-wide rule will apply)")

    def _check_admin_privileges(self):
        if is_admin():
            self.admin_lbl.configure(text="● Admin Mode (Active)", text_color="#2ea043")
        else:
            self.admin_lbl.configure(text="▲ Not Admin (Run as Administrator to apply rules)", text_color="#e3b341")

    def _on_region_select(self):
        reg = self.selected_region.get()
        self.status_var.set(f"Selected: {reg}. Click 'Lock Selected Region' to enforce.")

    def refresh_pings_async(self):
        self.status_var.set("Testing ping latencies to regions...")
        for lbl in self.ping_labels.values():
            lbl.configure(text="...", text_color="#888888")

        def run_pings():
            for name, meta in REGIONS.items():
                host = meta["ping_host"]
                try:
                    p = pythonping.ping(host, count=1, timeout=1.2)
                    ms = round(p.rtt_avg_ms, 1)
                    if p.success():
                        color = "#2ea043" if ms < 80 else ("#e3b341" if ms < 160 else "#f85149")
                        text = f"{ms} ms"
                    else:
                        color = "#6c707e"
                        text = "Timeout"
                except Exception:
                    color = "#6c707e"
                    text = "N/A"
                self.after(0, self._update_ping_label, name, text, color)
            self.after(0, lambda: self.status_var.set("Pings refreshed."))

        threading.Thread(target=run_pings, daemon=True).start()

    def _update_ping_label(self, name: str, text: str, color: str):
        if name in self.ping_labels:
            self.ping_labels[name].configure(text=text, text_color=color)

    def sync_ip_ranges_async(self):
        self.status_var.set("Synchronizing latest datacenter CIDR blocks...")
        def run_sync():
            try:
                target_dir = get_resource_path('ip_lists')
                sync_ip_ranges.sync_all(target_dir)
                self.after(0, lambda: self.status_var.set("Datacenter IP lists up to date."))
            except Exception as e:
                self.after(0, lambda: self.status_var.set(f"Sync error: {e}"))
        threading.Thread(target=run_sync, daemon=True).start()

    def lock_server(self):
        if not is_admin():
            self.status_var.set("Error: Must run as Administrator to configure Windows Firewall!")
            return

        target = self.selected_region.get()
        if target not in REGIONS:
            self.status_var.set("Select a valid region first.")
            return

        game = self.selected_game.get()
        app_paths = get_all_game_executables(game)

        self.status_var.set(f"Applying rules for {game} to isolate {target}...")

        def run_lock():
            FirewallManager.delete_all_selector_rules()
            base_dir = get_resource_path('ip_lists')
            ips_to_block = []
            
            for name, meta in REGIONS.items():
                if name == target:
                    continue
                file_path = os.path.join(base_dir, meta["file"])
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as fp:
                        for l in fp:
                            clean = l.strip()
                            if clean and not clean.startswith('#'):
                                ips_to_block.append(clean)

            # Enforce UDP-only to preserve TCP authentication/login
            ok = FirewallManager.block_ip_ranges(
                ips_to_block,
                rule_name=f"{GAME_PROFILES.get(game, {}).get('tag', 'GAME')}_{REGIONS[target]['tag']}",
                app_paths=app_paths,
                block_ipv6=self.ipv6_enabled.get(),
                udp_only=self.udp_only_mode.get()
            )

            msg = f"Locked to {target} ({game})! Auth/login protected." if ok else f"Locked to {target}."
            self.after(0, lambda: self.status_var.set(msg))

        threading.Thread(target=run_lock, daemon=True).start()

    def block_me_server(self):
        if not is_admin():
            self.status_var.set("Error: Must run as Administrator to configure Windows Firewall!")
            return

        game = self.selected_game.get()
        app_paths = get_all_game_executables(game)

        self.status_var.set(f"Blocking Middle East servers for {game}...")
        def run_block():
            FirewallManager.delete_all_selector_rules()
            base_dir = get_resource_path('ip_lists')
            file_path = os.path.join(base_dir, REGIONS["Middle East (Bahrain / Dubai / KSA)"]["file"])
            
            ips = []
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as fp:
                    for l in fp:
                        clean = l.strip()
                        if clean and not clean.startswith('#'):
                            ips.append(clean)

            ok = FirewallManager.block_ip_ranges(
                ips,
                rule_name="BLOCK_ME_ONLY",
                app_paths=app_paths,
                block_ipv6=self.ipv6_enabled.get(),
                udp_only=self.udp_only_mode.get()
            )
            msg = f"Middle East servers blocked for {game}!" if ok else "Applied Middle East block rules."
            self.after(0, lambda: self.status_var.set(msg))

        threading.Thread(target=run_block, daemon=True).start()

    def unlock_all(self):
        if not is_admin():
            self.status_var.set("Error: Must run as Administrator to remove firewall rules!")
            return

        self.status_var.set("Removing all server selector firewall rules...")
        def run_unlock():
            FirewallManager.delete_all_selector_rules()
            self.after(0, lambda: self.status_var.set("All server blocks removed. Normal matchmaking restored."))
        threading.Thread(target=run_unlock, daemon=True).start()

if __name__ == "__main__":
    app = UniversalServerSelectorApp()
    app.mainloop()
