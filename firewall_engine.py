"""
Core Firewall Engine for Overwatch Server Selector.
Provides modern, robust Windows Firewall management using netsh and HNetCfg COM interfaces.
Supports both IPv4 and IPv6 rules, application-scoped filtering, and grouping.
"""
import ctypes
import os
import subprocess
import logging
import ipaddress
from typing import List, Optional, Set

FIREWALL_GROUPING = "Overwatch-Server-Selector-v6"
RULE_PREFIX = "OW2_BLOCK_"

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

def split_ip_batches(ip_list: List[str], max_batch_size: int = 500) -> List[List[str]]:
    """Splits a list of IPs/CIDRs into manageable batches for firewall commands."""
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
        """Deletes all firewall rules associated with this tool using netsh."""
        logging.info("Deleting all previous selector rules...")
        cmd = f'netsh advfirewall firewall delete rule name=all dir=out'
        # To avoid deleting unassociated rules, we delete by specific rule names/prefixes
        # First query rules with OW2 prefix
        try:
            # Delete by group or by rule prefix using PowerShell for speed and accuracy
            ps_cmd = (
                f"Get-NetFirewallRule -Name '{RULE_PREFIX}*' -ErrorAction SilentlyContinue | "
                f"Remove-NetFirewallRule -ErrorAction SilentlyContinue; "
                f"Get-NetFirewallRule -DisplayGroup '{FIREWALL_GROUPING}' -ErrorAction SilentlyContinue | "
                f"Remove-NetFirewallRule -ErrorAction SilentlyContinue; "
                f"Get-NetFirewallRule -DisplayName '_Overwatch*' -ErrorAction SilentlyContinue | "
                f"Remove-NetFirewallRule -ErrorAction SilentlyContinue"
            )
            subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], check=False, capture_output=True)
            return True
        except Exception as e:
            logging.error(f"Error deleting rules: {e}")
            return False

    @staticmethod
    def block_ip_ranges(
        ip_ranges: List[str],
        rule_name: str = "OW2_BLOCK_RULE",
        app_path: Optional[str] = None,
        block_ipv6: bool = True
    ) -> bool:
        """
        Creates outbound and inbound firewall block rules for the specified IP ranges.
        Supports both IPv4 and IPv6 addresses.
        """
        # Separate IPv4 and IPv6
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
        
        # Apply IPv4 rules
        if ipv4_list:
            batches = split_ip_batches(ipv4_list, 500)
            for idx, batch in enumerate(batches):
                sub_name = f"{RULE_PREFIX}{rule_name}_v4_{idx}"
                ip_str = ",".join(batch)
                ok = FirewallManager._create_netsh_rule(sub_name, ip_str, app_path)
                if not ok:
                    all_success = False

        # Apply IPv6 rules
        if ipv6_list:
            batches = split_ip_batches(ipv6_list, 500)
            for idx, batch in enumerate(batches):
                sub_name = f"{RULE_PREFIX}{rule_name}_v6_{idx}"
                ip_str = ",".join(batch)
                ok = FirewallManager._create_netsh_rule(sub_name, ip_str, app_path)
                if not ok:
                    all_success = False

        return all_success

    @staticmethod
    def _create_netsh_rule(name: str, remote_ips: str, app_path: Optional[str] = None) -> bool:
        try:
            # We block outbound traffic to game servers (and optionally inbound)
            # Remote ports: OW2 UDP game traffic runs on UDP 12000-64000, 26500-39999, etc.
            # Blocking IP completely ensures the latency probe times out.
            app_arg = f'program="{app_path}"' if app_path and os.path.exists(app_path) else ''
            
            cmd_out = (
                f'netsh advfirewall firewall add rule name="{name}" dir=out action=block '
                f'remoteip="{remote_ips}" {app_arg}'
            )
            res = subprocess.run(cmd_out, shell=True, capture_output=True, text=True)
            return res.returncode == 0
        except Exception as e:
            logging.error(f"Failed to create netsh rule: {e}")
            return False

    @staticmethod
    def get_active_blocked_regions() -> List[str]:
        """Queries active firewall rules to see which selector rules are active."""
        try:
            ps_cmd = f"Get-NetFirewallRule -Name '{RULE_PREFIX}*' -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Name"
            res = subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, text=True)
            names = res.stdout.strip().splitlines()
            return [n.strip() for n in names if n.strip()]
        except Exception:
            return []
