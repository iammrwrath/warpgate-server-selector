# <p align="center"><img src="assets/warpgate_logo.png" width="180" alt="WARPGATE Logo"><br><b>WARPGATE</b></p>
<p align="center">
  <b>Next-Generation Ultra-Low Latency PvP Server Selector & Region Lock</b><br>
  <i>Take complete control of your matchmaking routing across competitive shooters.</i>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Release-v6.5-orange.svg" alt="Release">
  <img src="https://img.shields.io/badge/Platform-Windows%2010%20%7C%2011-blue.svg" alt="Platform">
  <img src="https://img.shields.io/badge/Protocol-UDP%20Matchmaking%20Safe-brightgreen.svg" alt="Protocol">
  <img src="https://img.shields.io/badge/Format-Portable%20Single%20EXE-blueviolet.svg" alt="Format">
  <img src="https://img.shields.io/badge/Anti--Cheat-100%25%20Safe%20(Firewall%20Only)-success.svg" alt="Safety">
</p>

---

## ⚡ What is WARPGATE?

**WARPGATE** is a modern, high-performance network routing tool designed for competitive PC gamers who demand strict matchmaking latency. 

Instead of letting game matchmaking algorithms randomly throw you onto distant or unstable server clusters with high ping and packet loss, **WARPGATE** leverages native **Windows Advanced Firewall rules** to filter out unwanted datacenters before the matchmaker can probe them.

### Supported Games
* 🎯 **Overwatch 2** (`Overwatch.exe`)
* 💥 **Battlefield 2042 & Battlefield 6** (`BF2042.exe` / `BF6.exe`)
* ⚡ **Apex Legends** (`r5apex.exe`)
* 🛡️ **Marvel Rivals** (`Marvel-Win64-Shipping.exe`)
* 🌐 **All Multiplayer Games** (System-wide global mode)

---

## 🚀 Key Features

* **🛡️ 100% Anti-Cheat Safe (Warden / Ricochet / EasyAntiCheat)**  
  Zero memory modification, zero DLL injection, zero game file tampering. WARPGATE operates purely on the OS network firewall level (`netsh advfirewall` & Windows Filtering Platform).
* **🔒 Smart UDP Game Isolation**  
  Unlike legacy tools that cause *"Time out communicating with Battle.net services"* or EA App connection errors by blocking all traffic, WARPGATE blocks **UDP match routing only**, leaving critical TCP authentication, login tokens, patch downloaders, and Discord untouched.
* **⚡ Live Latency Monitor**  
  Real-time asynchronous ping telemetry to Blizzard, AWS, and Google Cloud datacenters with color-coded status badges:
  - 🟢 Low Ping (<80ms)
  - 🟡 Moderate Ping (80–160ms)
  - 🔴 High Ping (>160ms)
* **🌐 Dynamic Cloud CIDR Synchronization**  
  Automated live updates syncing directly with Google Cloud and AWS IP blocks to ensure your server blocklists are never obsolete after game patches.
* **📦 Portable Single-Executable**  
  No Python, no installers, no DLL configuration needed. Runs standalone straight from your desktop or USB drive with automatic UAC administrator privilege elevation.

---

## 🗺️ Supported Global Datacenters

| Region Identifier | City / Location | Cloud / Hosting Provider |
| :--- | :--- | :--- |
| **ORD1** | Chicago, IL, USA | Blizzard Core / Google Cloud (`us-central1`) |
| **LAX1 / GUW2** | Los Angeles, CA / Oregon | Blizzard Core / AWS / GCP (`us-west`) |
| **GUE4** | Ashburn, VA, USA | AWS (`us-east-1`) / Google Cloud |
| **AMS1 / GEN1** | Amsterdam / Finland / Frankfurt | European Core / GCP (`europe-west4`, `europe-north1`) |
| **MES1 / GMEC** | Bahrain / Qatar / Saudi Arabia | AWS Middle East / Google Cloud (`me-central`) |
| **GTK1** | Tokyo, Japan | AWS (`ap-northeast-1`) / Google Cloud |
| **ICN1 / GAN3** | Seoul, South Korea | Blizzard Core / AWS / GCP (`asia-northeast3`) |
| **GSG1** | Singapore | AWS (`ap-southeast-1`) / Google Cloud |
| **TPE1** | Taipei, Taiwan | Blizzard Core / GCP (`asia-east1`) |
| **SYD2** | Sydney, Australia | AWS Oceania (`ap-southeast-2`) |
| **GBR1** | São Paulo, Brazil | AWS South America (`sa-east-1`) |

---

## 💻 Quick Start Guide

### Option 1: Run the Precompiled Standalone Executable (Recommended)
1. Head to the **[Releases](https://github.com/iammrwrath/warpgate-server-selector/releases)** or your local `dist/` directory.
2. Launch **`PvP-Server-Selector.exe`** (accept the Windows UAC Administrator prompt).
3. Select your target game from the dropdown.
4. Select your preferred region tile to inspect live ping latencies.
5. Click **"🔒 Lock Selected Region"**.
6. Launch your game and queue into competitive matches!

### Option 2: Running from Source
```bash
# Clone the repository
git clone https://github.com/iammrwrath/warpgate-server-selector.git
cd warpgate-server-selector

# Install dependencies
python -m pip install -r requirements.txt

# Run WARPGATE (Run terminal as Administrator)
python modern_app.py
```

### Option 3: Building the Standalone Executable
```bash
python -m pip install pyinstaller
python -m PyInstaller --clean build_portable.spec
```
The output executable will be generated at `dist/PvP-Server-Selector.exe`.

---

## ❓ Frequently Asked Questions

<details>
<summary><b>Can I get banned for using WARPGATE?</b></summary>
No. WARPGATE does not touch the game client, memory, or storage. It functions identically to configuring outbound packet rules in Windows Defender Firewall or setting QoS rules in your router.
</details>

<details>
<summary><b>Will this kick me from Battle.net or the EA App?</b></summary>
No. WARPGATE specifically implements smart UDP filtering. Platform authentication, license verification, and text/voice chat operate over TCP (ports 80, 443, 1119, 3724) and remain untouched.
</details>

<details>
<summary><b>How do I check which server I am currently on in Overwatch 2?</b></summary>
In an active match or in the Practice Range, press <code>Ctrl + Shift + N</code> to toggle the NetGraph. Look at the top-left corner next to the IP address to see the four-letter server identifier (e.g. <code>[ORD1]</code>).
</details>

<details>
<summary><b>How do I reset all firewall rules?</b></summary>
Simply open the tool and click <b>"🔓 Reset / Unblock All"</b>. All custom server routing rules will be wiped instantly.
</details>

---

## 📜 License & Acknowledgments
* **Author / Maintainer**: [iammrwrath](https://github.com/iammrwrath)
* Originally based on the foundational research of `foryVERX/Overwatch-Server-Selector`.
* Licensed under the MIT License.
