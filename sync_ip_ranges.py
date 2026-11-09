"""
IP Range Synchronizer & Generator for Overwatch 2 Datacenters
Fetches live cloud IP ranges (Google Cloud, AWS where applicable) and combines them
with Blizzard proprietary datacenter CIDR blocks and known edge blocks.
"""
import json
import urllib.request
import ipaddress
import os
import glob

# Datacenter to GCP scope mapping
GCP_SCOPE_MAP = {
    'ORD1': ['us-central1'],
    'LAX1': ['us-west1'],
    'GUW2': ['us-west1', 'us-west2'],
    'GUE4': ['us-east1', 'us-east4'],
    'AMS1': ['europe-west4'],
    'GEN1': ['europe-north1'],
    'GEW3': ['europe-west3'],
    'CDG1': ['europe-west9'],
    'GSG1': ['asia-southeast1'],
    'GTK1': ['asia-northeast1'],
    'GAN3': ['asia-northeast3'],
    'TPE1': ['asia-east1'],
    'SYD2': ['australia-southeast1'],
    'GBR1': ['southamerica-east1'],
    'GMEC1': ['me-central1'],
    'GMEC2': ['me-central2'],
    'MES1': ['me-west1']
}

GCP_URL = "https://www.gstatic.com/ipranges/cloud.json"

def fetch_gcp_prefixes():
    print(f"Fetching live Google Cloud IP ranges from {GCP_URL}...")
    req = urllib.request.Request(GCP_URL, headers={"User-Agent": "OW2-Server-Selector/6.0"})
    with urllib.request.urlopen(req) as resp:
        data = json.loads(resp.read().decode('utf-8'))
    
    ipv4_by_scope = {}
    ipv6_by_scope = {}
    
    for prefix in data.get('prefixes', []):
        scope = prefix.get('scope')
        if not scope:
            continue
        if 'ipv4Prefix' in prefix:
            ipv4_by_scope.setdefault(scope, []).append(prefix['ipv4Prefix'])
        elif 'ipv6Prefix' in prefix:
            ipv6_by_scope.setdefault(scope, []).append(prefix['ipv6Prefix'])
            
    return ipv4_by_scope, ipv6_by_scope

def load_existing_cfgs(dir_path):
    cfgs = {}
    for f in glob.glob(os.path.join(dir_path, "cfg - *.txt")):
        filename = os.path.basename(f)
        code = None
        for key in GCP_SCOPE_MAP:
            if key in filename:
                code = key
                break
        with open(f, 'r', encoding='utf-8') as fp:
            lines = [line.strip() for line in fp if line.strip() and not line.startswith('#')]
        cfgs[filename] = {
            'path': f,
            'code': code,
            'ranges': lines
        }
    return cfgs

def sync_all(target_dir='ip_lists'):
    ipv4_scopes, ipv6_scopes = fetch_gcp_prefixes()
    cfgs = load_existing_cfgs(target_dir)
    
    print(f"Found {len(cfgs)} cfg files in {target_dir}")
    
    for filename, data in cfgs.items():
        code = data['code']
        existing_ranges = set(data['ranges'])
        initial_count = len(existing_ranges)
        
        if code and code in GCP_SCOPE_MAP:
            scopes = GCP_SCOPE_MAP[code]
            for scope in scopes:
                if scope in ipv4_scopes:
                    existing_ranges.update(ipv4_scopes[scope])
                if scope in ipv6_scopes:
                    existing_ranges.update(ipv6_scopes[scope])
        
        # Sort IPv4 / IPv6 / range entries cleanly
        sorted_ranges = sorted(list(existing_ranges), key=lambda x: (':' in x, x.count('/') == 0, x))
        
        with open(data['path'], 'w', encoding='utf-8') as fp:
            for r in sorted_ranges:
                fp.write(f"{r}\n")
                
        print(f"Updated {filename}: {initial_count} -> {len(sorted_ranges)} prefixes (IPv4 + IPv6)")

    # Now rebuild aggregate Ip_ranges files
    rebuild_aggregates(target_dir)

def rebuild_aggregates(target_dir):
    print("\nRebuilding aggregate regional IP range files...")
    
    # Regional groupings mapping
    region_map = {
        'Ip_ranges_NA_central.txt': ['ORD1'],
        'Ip_ranges_NA_West.txt': ['LAX1', 'GUW2'],
        'Ip_ranges_NA_East.txt': ['GUE4'],
        'Ip_ranges_EU.txt': ['AMS1', 'GEN1', 'GEW3', 'CDG1'],
        'Ip_ranges_ME.txt': ['MES1', 'GMEC1', 'GMEC2'],
        'Ip_ranges_AS_Singapore.txt': ['GSG1'],
        'Ip_ranges_AS_Japan.txt': ['GTK1'],
        'Ip_ranges_AS_Korea.txt': ['ICN1', 'GAN3'],
        'Ip_ranges_AS_Taiwan.txt': ['TPE1'],
        'Ip_ranges_Australia.txt': ['SYD2'],
        'Ip_ranges_Brazil.txt': ['GBR1'],
    }
    
    cfgs = load_existing_cfgs(target_dir)
    
    for agg_name, codes in region_map.items():
        agg_path = os.path.join(target_dir, agg_name)
        combined = set()
        
        # Include existing lines in agg_path (e.g. non-datacenter specific Blizzard ranges)
        if os.path.exists(agg_path):
            with open(agg_path, 'r', encoding='utf-8') as fp:
                for line in fp:
                    l = line.strip()
                    if l and not l.startswith('#'):
                        combined.add(l)
                        
        # Add ranges from mapped cfgs
        for filename, data in cfgs.items():
            if data['code'] in codes:
                combined.update(data['ranges'])
                
        sorted_combined = sorted(list(combined), key=lambda x: (x.count('/') == 0, x))
        with open(agg_path, 'w', encoding='utf-8') as fp:
            for r in sorted_combined:
                fp.write(f"{r}\n")
                
        print(f"Rebuilt {agg_name}: {len(sorted_combined)} prefixes")

if __name__ == '__main__':
    sync_all('ip_lists')
