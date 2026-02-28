<div align="center">

```
 __  __                          ______ _______ _    _            ______                   _   
|  \/  |                        |  ____|__   __| |  | |          |  ____|                 | |  
| \  / |   ___    __ _    __ _  | |__     | |  | |__| |  ______  | |__ __ _ _   _  ___ ___| |_ 
| |\/| |  / _ \  / _` |  / _` | |  __|    | |  |  __  | |______| |  __/ _` | | | |/ __/ _ \ __|
| |  | | |  __/ | (_| | | (_| | | |____   | |  | |  | |          | | | (_| | |_| | (_|  __/ |_ 
|_|  |_|  \___|  \__, |  \__,_| |______|  |_|  |_|  |_|          |_|  \__,_|\__,_|\___\___|\__|
                  __/ |                                                                        
                 |___/                                                                         
```

### Automated Faucet Claimer for MegaETH Testnet

[![Python](https://img.shields.io/badge/Python-3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20Linux%20%7C%20macOS-blue?style=for-the-badge)]()
[![MegaETH](https://img.shields.io/badge/MegaETH-Testnet-FF6B35?style=for-the-badge)](https://testnet.megaeth.com)

**Multi-threaded testnet token claimer** with 2Captcha Turnstile integration, proxy rotation, and Rich CLI.
Built for MegaETH — Ethereum's real-time L2 with 100,000+ TPS.

[Getting Started](#-getting-started) · [Features](#-features) · [Configuration](#-configuration) · [Usage](#-usage) · [FAQ](#-faq)

</div>

---

## 🔗 Official MegaETH Links

| Step | Link | Description |
|:----:|------|-------------|
| **1** | [MegaETH Homepage](https://megaeth.com) | Official website — real-time Ethereum Layer 2 |
| **2** | [MegaETH Testnet Faucet](https://testnet.megaeth.com) | Claim testnet tokens for testing and development |
| **3** | [MegaETH Docs](https://docs.megaeth.com) | Technical documentation and RPC endpoints |
| **4** | [MegaExplorer](https://www.megaexplorer.xyz) | Block explorer — verify transactions and balances |

> MegaETH is an Ethereum Layer 2 scaling solution targeting 100,000+ TPS with sub-millisecond latency. Backed by Vitalik Buterin, it uses JIT bytecode compilation, parallel execution, and EigenDA for real-time blockchain performance.

---

## ⚡ Features

<table>
<tr>
<td width="50%">

**Claiming Engine**
- ✅ Automated Turnstile captcha solving via 2Captcha
- ✅ Multi-threaded wallet processing (1–20 workers)
- ✅ Proxy rotation with `ip:port` and `ip:port:user:pass`
- ✅ Auto-retry on failure (3 attempts per wallet)
- ✅ Duplicate claim detection (cooldown handling)

</td>
<td width="50%">

**CLI & Logging**
- ✅ Rich-styled terminal UI (tables, panels, spinners)
- ✅ Wallet input via `wallet.txt` and `wallets.json`
- ✅ Success/fail logging (`success.txt`, `fail.txt`)
- ✅ Balance checker module
- ✅ Interactive settings and proxy configuration

</td>
</tr>
</table>

---

## 📦 Getting Started

### Prerequisites

- **Python 3.8** or higher ([download](https://python.org/downloads/))
- **pip** (included with Python)
- A [2Captcha](https://2captcha.com) account with API key (required for Turnstile solving)
- Ethereum wallet addresses to receive testnet tokens

### Installation

**Option A — Windows (one-click):**

Double-click `run.bat` — it starts the application immediately.

**Option B — Manual (all platforms):**

```bash
git clone https://github.com/user/MegaETH-Faucet.git
cd MegaETH-Faucet
pip install -r requirements.txt
python main.py
```

### Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `rich` | ≥ 13.0 | Terminal UI — tables, panels, progress bars |
| `requests` | ≥ 2.28 | HTTP client for faucet API and proxy checks |
| `twocaptcha` | ≥ 1.2 | 2Captcha API — automated Turnstile solving |
| `colorama` | ≥ 0.4 | Cross-platform terminal colors |
| `pytz` | ≥ 2023.3 | Timezone support for logging timestamps |
| `tzlocal` | ≥ 5.0 | Local timezone detection |

---

## ⚙ Configuration

### `config.json` — Main Settings

Configured via the Settings menu (option 2) or edit directly:

```json
{
  "two_captcha_api_key": "your_2captcha_api_key_here",
  "threads": 5,
  "turnstile_sitekey": "0x4AAAAAABA4JXCaw9E2Py-9",
  "turnstile_page_url": "https://testnet.megaeth.com/",
  "megaeth_api_url": "https://carrot.megaeth.com/claim",
  "rpc_endpoint": "https://carrot.megaeth.com/rpc"
}
```

| Setting | Description |
|---------|-------------|
| `two_captcha_api_key` | Your 2Captcha API key (**required** for captcha solving) |
| `threads` | Number of parallel workers (1–20, default: 5) |
| `turnstile_sitekey` | Cloudflare Turnstile site key (auto-configured) |
| `turnstile_page_url` | Faucet page URL for captcha context |
| `megaeth_api_url` | MegaETH faucet claim API endpoint |
| `rpc_endpoint` | MegaETH testnet RPC for balance checks |

### `wallet.txt` — Wallet Addresses

One Ethereum address per line:

```
0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18
0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48
0xdAC17F958D2ee523a2206206994597C13D831ec7
```

### `wallets.json` — Alternative Wallet Format

```json
[
  {"address": "0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18"},
  {"address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"}
]
```

> Both files are read automatically. Duplicates between `wallet.txt` and `wallets.json` are processed.

### `proxy.txt` — Proxy List (Optional)

One proxy per line. Two formats supported:

```
192.168.1.100:8080
31.56.139.207:6276:username:password
```

> Proxies are rotated round-robin across threads. Leave empty to use direct connection.

---

## 🚀 Usage

```bash
python main.py
```

The interactive menu:

```
╔═══════════════════════════════════════════════════════════╗
║                  MegaETH Faucet                            ║
║           Automated Testnet Token Claimer                   ║
╚═══════════════════════════════════════════════════════════╝

  ╭──────────────────────────────────────────────────────╮
  │  1   Install Dependencies                            │
  │  2   Settings — 2Captcha API key, threads, RPC       │
  │  3   Add Wallet — add addresses to wallet.txt        │
  │  4   Proxy Config — configure proxy.txt              │
  │  5   Run Faucet — start automated claiming           │
  │  6   Check Balance — query wallet balances           │
  │  7   View Logs — success.txt and fail.txt            │
  │  8   About — MegaETH info and links                  │
  │  0   Exit                                            │
  ╰──────────────────────────────────────────────────────╯

  Select option:
```

| Option | What it does |
|:------:|-------------|
| `1` | Installs all dependencies from `requirements.txt` via pip |
| `2` | Configure 2Captcha API key, thread count, and RPC endpoint |
| `3` | Add wallet addresses interactively or open `wallet.txt` for editing |
| `4` | View and manage proxy list in `proxy.txt` |
| `5` | **Starts claiming** — solves Turnstile, posts to faucet API, logs results |
| `6` | Checks MegaETH testnet balances for all configured wallets |
| `7` | View claim history — success and failure logs with entry counts |
| `8` | About MegaETH — network specs, features, official links |
| `0` | Exit the application |

### Claim Flow

When you run option **5**, the bot executes this pipeline for each wallet:

```
Solve Turnstile → Submit claim → Verify TX hash → Log result
     ↓                                    ↓
  2Captcha API                    success.txt / fail.txt
```

---

## 📁 Project Structure

```
MegaETH-Faucet/
├── main.py              Entry point — Rich CLI menu and wallet management
├── faucet_module.py     Core claim logic — captcha, threading, proxy rotation
├── balance_module.py    Balance checker — query wallet balances via RPC
├── config.json          Settings (2Captcha key, threads, endpoints)
├── wallet.txt           Wallet addresses, one per line
├── wallets.json         Alternative wallet format (JSON array)
├── proxy.txt            Proxy list for IP rotation (optional)
├── success.txt          Log of successful claims (auto-created)
├── fail.txt             Log of failed attempts (auto-created)
├── requirements.txt     Python dependencies
├── run.bat              Windows one-click launcher
├── about/
│   └── hashtags.txt     Project hashtags
└── README.md            This file
```

---

## ❓ FAQ

<details>
<summary><b>ModuleNotFoundError: No module named 'twocaptcha'</b></summary>

Run option **1** from the menu or manually:
```bash
pip install -r requirements.txt
```
The `twocaptcha` package is the official 2Captcha Python SDK.
</details>

<details>
<summary><b>Error: 2Captcha API key not configured</b></summary>

You need a valid [2Captcha](https://2captcha.com) account. Get your API key from the dashboard and enter it via Settings (option 2). The key is required to solve Cloudflare Turnstile challenges on the faucet page.
</details>

<details>
<summary><b>"Less than X hours have passed" — wallet claimed recently</b></summary>

The MegaETH faucet has a cooldown period per wallet address. The bot detects this and skips the wallet automatically. Wait for the cooldown to expire before claiming again.
</details>

<details>
<summary><b>Proxy connection fails / timeout</b></summary>

- Verify format: `ip:port` (no auth) or `ip:port:user:pass` (with auth)
- The bot rotates proxies automatically — dead proxies are cycled past
- Test manually: `curl -x http://ip:port https://api.myip.com`
- Remove dead proxies from `proxy.txt` for faster processing
</details>

<details>
<summary><b>Can I use this without proxies?</b></summary>

Yes. Leave `proxy.txt` empty or delete it. The bot will use your direct IP for all requests. Proxies are recommended for large wallet batches to avoid rate limiting.
</details>

<details>
<summary><b>How many wallets can I process at once?</b></summary>

No hard limit. Set `threads` in `config.json` to control parallelism (1–20). With 5 threads and proxies, 50+ wallets run smoothly. Each claim requires a separate captcha solve (~15–30 seconds per wallet).
</details>

---

## ⚠️ Disclaimer

This tool is for **educational and testnet purposes only**. MegaETH testnet tokens have no real-world value. The authors are not affiliated with MegaETH. Use at your own risk — the authors are not responsible for any account restrictions or 2Captcha charges.

---

<div align="center">

If this tool helped you claim MegaETH testnet tokens, consider leaving a ⭐

</div>
