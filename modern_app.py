"""
Modern Multi-Game Server Selector v6.5 (Portable Edition)
Supports:
- Overwatch 2 (Blizzard AS57976 + Google Cloud / AWS)
- Battlefield 2042 / Battlefield 6 (EA / i3D.net AS49544 + AWS)
- Apex Legends (Respawn / EA AWS + GCP)
- Marvel Rivals (NetEase / AWS GameLift)
- System-Wide Global Game Matchmaking Block

Key Features:
- Dynamic Game-Specific Server Lists: GUI automatically refreshes and displays exact regional datacenters, descriptions, and ping targets when switching games.
- Safe UDP-Only Filtering: Never blocks TCP login/auth/Battle.net/EA app servers (prevents "Time out communicating with Battle.net services" error).
- Executable Auto-Scoping: Automatically discovers and binds firewall rules to all game .exe files (Battle.net AND Steam).
"""
import sys
import os
import threading
from typing import Dict, List, Optional

import customtkinter as ctk
import pythonping

from firewall_engine import FirewallManager, is_admin
from game_profiles import GAME_PROFILES, get_all_game_executables, get_game_regions
import sync_ip_ranges

def get_resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller bundle."""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

class UniversalServerSelectorApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("WARPGATE - Universal PvP Server Selector")
        self.geometry("880x720")
        self.minsize(820, 640)
        
        ctk.set_appearance_mode("Dark")
        ctk.set_default_color_theme("blue")

        self.selected_game = ctk.StringVar(value="Overwatch 2")
        self.detected_exe = ctk.StringVar(value="")
        self.selected_region = ctk.StringVar(value="")
        self.ipv6_enabled = ctk.BooleanVar(value=True)
        self.udp_only_mode = ctk.BooleanVar(value=True)
        self.ping_labels: Dict[str, ctk.CTkLabel] = {}
        self.status_var = ctk.StringVar(value="Status: Ready")

        self._create_layout()
        self._check_admin_privileges()
        self._on_game_change(self.selected_game.get())

    def _create_layout(self):
        # Header banner
        header_frame = ctk.CTkFrame(self, corner_radius=10, fg_color="#1a1d24")
        header_frame.pack(fill="x", padx=15, pady=(15, 10))

        title_lbl = ctk.CTkLabel(
            header_frame, 
            text="⚡ WARPGATE PVP SERVER SELECTOR", 
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
            width=220
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
        self.regions_scroll = ctk.CTkScrollableFrame(
            content_frame, 
            label_text="Available Server Regions", 
            label_font=ctk.CTkFont(size=14, weight="bold")
        )
        self.regions_scroll.pack(side="left", fill="both", expand=True, padx=(0, 10))

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
        """Called whenever the user selects a different game from the dropdown."""
        exes = get_all_game_executables(game_name)
        if exes:
            names = [os.path.basename(os.path.dirname(os.path.dirname(e))) or os.path.basename(e) for e in exes]
            self.detected_exe.set(f"✓ Bound to {len(exes)} executable(s): {', '.join(names)}")
        else:
            if game_name == "All Games (Global Mode)":
                self.detected_exe.set("● Applies system-wide to outbound matchmaking traffic")
            else:
                self.detected_exe.set("▲ Not found in standard paths (system-wide rule will apply)")

        # Rebuild the region list dynamically for this specific game
        self._rebuild_region_list(game_name)
        self.refresh_pings_async()

    def _rebuild_region_list(self, game_name: str):
        """Clears and dynamically populates the region cards for the chosen game."""
        # Destroy all existing widgets inside the scrollable region frame
        for child in self.regions_scroll.winfo_children():
            child.destroy()

        self.ping_labels.clear()
        regions = get_game_regions(game_name)
        
        # Update scrollable frame label
        self.regions_scroll.configure(label_text=f"Available Server Regions — {game_name}")

        # Auto-select the first region by default
        first_region = next(iter(regions.keys())) if regions else ""
        self.selected_region.set(first_region)

        for reg_name, meta in regions.items():
            card = ctk.CTkFrame(self.regions_scroll, corner_radius=6, fg_color="#282c34")
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

        self.status_var.set(f"Loaded {len(regions)} regions for {game_name}.")

    def _check_admin_privileges(self):
        if is_admin():
            self.admin_lbl.configure(text="● Admin Mode (Active)", text_color="#2ea043")
        else:
            self.admin_lbl.configure(text="▲ Not Admin (Run as Administrator to apply rules)", text_color="#e3b341")

    def _on_region_select(self):
        reg = self.selected_region.get()
        self.status_var.set(f"Selected: {reg}. Click 'Lock Selected Region' to enforce.")

    def refresh_pings_async(self):
        game = self.selected_game.get()
        regions = get_game_regions(game)
        
        self.status_var.set(f"Testing ping latencies to {game} datacenters...")
        for lbl in self.ping_labels.values():
            lbl.configure(text="...", text_color="#888888")

        def run_pings():
            for name, meta in regions.items():
                host = meta.get("ping_host")
                if not host:
                    continue
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
            self.after(0, lambda: self.status_var.set(f"Pings refreshed for {game}."))

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

        game = self.selected_game.get()
        regions = get_game_regions(game)
        target = self.selected_region.get()

        if target not in regions:
            self.status_var.set("Select a valid region first.")
            return

        app_paths = get_all_game_executables(game)
        self.status_var.set(f"Applying rules for {game} to isolate {target}...")

        def run_lock():
            FirewallManager.delete_all_selector_rules()
            base_dir = get_resource_path('ip_lists')
            ips_to_block = []
            
            # Smart exemption map: For Overwatch 2 in North America, Blizzard's matchmaker
            # uses ORD1 (Central) and GUE4 (East) concurrently for matchmaking signaling, relays,
            # and practice range instances. If NA Central or NA East is locked, keep the adjacent
            # NA local region unblocked to prevent "Failed to connect to server" handshake timeouts,
            # while blocking all transatlantic / foreign datacenters (Europe, Middle East, Asia, Oceania, South America).
            exempt_regions = {target}
            if game == "Overwatch 2":
                if "NA Central" in target:
                    exempt_regions.add("NA East (GUE4 / Virginia)")
                elif "NA East" in target:
                    exempt_regions.add("NA Central (ORD1 / Chicago)")

            for name, meta in regions.items():
                if name in exempt_regions:
                    continue
                file_rel = meta.get("file", "")
                file_path = os.path.join(base_dir, file_rel)
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding='utf-8') as fp:
                        for l in fp:
                            clean = l.strip()
                            if clean and not clean.startswith('#'):
                                ips_to_block.append(clean)

            game_tag = GAME_PROFILES.get(game, {}).get('tag', 'GAME')
            region_tag = regions[target].get('tag', 'REGION')
            
            # Enforce UDP-only to preserve TCP authentication/login
            ok = FirewallManager.block_ip_ranges(
                ips_to_block,
                rule_name=f"{game_tag}_{region_tag}",
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
        regions = get_game_regions(game)
        app_paths = get_all_game_executables(game)

        # Find the Middle East entry in this game's regions
        me_entry = None
        for rname, rmeta in regions.items():
            if "Middle East" in rname or "me-" in rname.lower() or "dammam" in rname.lower():
                me_entry = rmeta
                break

        if not me_entry:
            self.status_var.set(f"No specific Middle East region defined for {game}.")
            return

        self.status_var.set(f"Blocking Middle East servers for {game}...")
        def run_block():
            FirewallManager.delete_all_selector_rules()
            base_dir = get_resource_path('ip_lists')
            file_path = os.path.join(base_dir, me_entry["file"])
            
            ips = []
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as fp:
                    for l in fp:
                        clean = l.strip()
                        if clean and not clean.startswith('#'):
                            ips.append(clean)

            game_tag = GAME_PROFILES.get(game, {}).get('tag', 'GAME')
            ok = FirewallManager.block_ip_ranges(
                ips,
                rule_name=f"{game_tag}_BLOCK_ME_ONLY",
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
