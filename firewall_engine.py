"""
Core Firewall Engine for Universal Multi-Game Server Selector.
Features:
- Application executable scoping (Prevents blocking launcher/auth/Discord/Steam/Battle.net).
- Port exclusion / protocol filtering (Leaves TCP 1119/3724 & 80/443 open for login).
- Multi-game support (Overwatch 2, Battlefield 2042 / 6, Apex Legends, Marvel Rivals, Call of Duty).
"""
import ctypes
import os
import subprocess
import logging
from typing import List, Optional

RULE_PREFIX = "GAMESERV_BLOCK_"

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s'
)

def is_admin() -> bool:
    """Check if the current process has administrative privileges."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception:
        return False

def split_ip_batches(ip_list: List[str], max_batch_size: int = 400) -> List[List[str]]:
    """Splits a list of IPs/CIDRs into batches suitable for netsh commands."""
    batches = []
    current_batch = []
    
    for item in ip_list:
        clean_item = item.strip()
        if not clean_item or clean_item.startswith('#'):
            continue
        current_batch.append(clean_item)
        if len(current_batch) >= max_batch_size:
            batches.append(current_batch)
            current_batch = []
            
    if current_batch:
        batches.append(current_batch)
    return batches

class FirewallManager:
    @staticmethod
    def delete_all_selector_rules() -> bool:
        """Deletes all firewall rules created by this selector or legacy versions."""
        logging.info("Deleting all previous selector rules...")
        ps_cmd = (
            f"Get-NetFirewallRule -Name '{RULE_PREFIX}*' -ErrorAction SilentlyContinue | Remove-NetFirewallRule -ErrorAction SilentlyContinue; "
            f"Get-NetFirewallRule -DisplayName '{RULE_PREFIX}*' -ErrorAction SilentlyContinue | Remove-NetFirewallRule -ErrorAction SilentlyContinue; "
            f"Get-NetFirewallRule -Name 'OW2_BLOCK*' -ErrorAction SilentlyContinue | Remove-NetFirewallRule -ErrorAction SilentlyContinue; "
            f"Get-NetFirewallRule -DisplayName 'OW2_BLOCK*' -ErrorAction SilentlyContinue | Remove-NetFirewallRule -ErrorAction SilentlyContinue; "
            f"Get-NetFirewallRule -DisplayName '_Overwatch*' -ErrorAction SilentlyContinue | Remove-NetFirewallRule -ErrorAction SilentlyContinue; "
            f"Get-NetFirewallRule -DisplayName 'BF_*' -ErrorAction SilentlyContinue | Remove-NetFirewallRule -ErrorAction SilentlyContinue"
        )
        try:
            subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], check=False, capture_output=True)
            return True
        except Exception as e:
            logging.error(f"Error deleting rules: {e}")
            return False

    @staticmethod
    def block_ip_ranges(
        ip_ranges: List[str],
        rule_name: str = "DEFAULT",
        app_paths: Optional[List[str]] = None,
        block_ipv6: bool = True,
        udp_only: bool = True
    ) -> bool:
        """
        Blocks traffic to target IP ranges.
        If app_paths is provided, limits rule to only those executables.
        If udp_only is True (recommended for OW2 & PvP shooters), blocks UDP only so TCP login/auth servers stay 100% accessible.
        """
        ipv4_list = []
        ipv6_list = []
        
        for item in ip_ranges:
            clean = item.strip()
            if not clean:
                continue
            if ':' in clean:
                if block_ipv6:
                    ipv6_list.append(clean)
            else:
                ipv4_list.append(clean)
                
        all_success = True
        
        # Build program args
        valid_apps = [p for p in (app_paths or []) if p and os.path.exists(p)]
        if not valid_apps:
            valid_apps = [None] # System-wide fallback if no path specified

        for app_exe in valid_apps:
            # Apply IPv4 rules
            if ipv4_list:
                batches = split_ip_batches(ipv4_list, 400)
                for idx, batch in enumerate(batches):
                    name = f"{RULE_PREFIX}{rule_name}_v4_{idx}"
                    ip_str = ",".join(batch)
                    ok = FirewallManager._create_rule(name, ip_str, app_exe, udp_only=udp_only)
                    if not ok:
                        all_success = False

            # Apply IPv6 rules
            if ipv6_list:
                batches = split_ip_batches(ipv6_list, 400)
                for idx, batch in enumerate(batches):
                    name = f"{RULE_PREFIX}{rule_name}_v6_{idx}"
                    ip_str = ",".join(batch)
                    ok = FirewallManager._create_rule(name, ip_str, app_exe, udp_only=udp_only)
                    if not ok:
                        all_success = False

        return all_success

    @staticmethod
    def _create_rule(name: str, remote_ips: str, app_path: Optional[str] = None, udp_only: bool = True) -> bool:
        try:
            app_arg = f'program="{app_path}"' if app_path else ''
            proto_arg = 'protocol=udp' if udp_only else ''
            
            cmd = (
                f'netsh advfirewall firewall add rule name="{name}" dir=out action=block '
                f'remoteip="{remote_ips}" {proto_arg} {app_arg}'
            )
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return res.returncode == 0
        except Exception as e:
            logging.error(f"Failed to create firewall rule: {e}")
            return False
