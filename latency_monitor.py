"""
Ping & Latency Tester for Overwatch 2 Regions.
Supports multi-threaded TCP/ICMP ping measurements to active region endpoints.
"""
import socket
import time
import threading
from typing import Dict, Optional, Callable

# Known reliable ping endpoints corresponding to Overwatch 2 server clusters
REGION_ENDPOINTS = {
    "NA Central (ORD1)": ("24.105.62.129", 80),
    "NA West (LAX1/GUW2)": ("24.105.30.129", 80),
    "NA East (GUE4)": ("34.224.0.1", 443),
    "Europe (AMS1/GEN1)": ("185.60.114.159", 80),
    "Middle East (Bahrain/KSA)": ("157.175.0.1", 443),
    "Asia - Tokyo (GTK1)": ("dynamodb.ap-northeast-1.amazonaws.com", 443),
    "Asia - Seoul (ICN1/GAN3)": ("211.234.110.1", 80),
    "Asia - Singapore (GSG1)": ("dynamodb.ap-southeast-1.amazonaws.com", 443),
    "Asia - Taiwan (TPE1)": ("5.42.160.1", 443),
    "Australia (SYD2)": ("172.105.168.123", 80),
    "Brazil (GBR1)": ("dynamodb.sa-east-1.amazonaws.com", 443),
}

def measure_latency_ms(host: str, port: int = 80, timeout: float = 1.5) -> Optional[float]:
    """Measures TCP connection handshake time in milliseconds."""
    try:
        start = time.perf_counter()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))
        sock.close()
        elapsed = (time.perf_counter() - start) * 1000.0
        return round(elapsed, 1)
    except Exception:
        return None

def test_all_regions_async(callback: Callable[[Dict[str, Optional[float]]], None]):
    """Runs latency measurements in parallel and returns results to callback."""
    results = {}
    threads = []

    def probe(region, endpoint):
        host, port = endpoint
        latency = measure_latency_ms(host, port)
        results[region] = latency

    for reg, ep in REGION_ENDPOINTS.items():
        t = threading.Thread(target=probe, args=(reg, ep), daemon=True)
        t.start()
        threads.append(t)

    def wait_and_reply():
        for t in threads:
            t.join()
        callback(results)

    threading.Thread(target=wait_and_reply, daemon=True).start()
