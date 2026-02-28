#!/usr/bin/env python3
"""
MegaETH Faucet - Core claim logic
"""

import json
import threading
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from twocaptcha import TwoCaptcha
from rich.console import Console

PROJECT_ROOT = Path(__file__).parent
console = Console()

# Configuration
WALLETS_FILE = PROJECT_ROOT / "wallet.txt"
WALLETS_JSON_FILE = PROJECT_ROOT / "wallets.json"
PROXIES_FILE = PROJECT_ROOT / "proxy.txt"
CONFIG_FILE = PROJECT_ROOT / "config.json"
SUCCESS_FILE = PROJECT_ROOT / "success.txt"
FAIL_FILE = PROJECT_ROOT / "fail.txt"

HEADERS = {
    "Accept": "*/*",
    "Content-Type": "text/plain;charset=UTF-8",
    "Origin": "https://testnet.megaeth.com",
    "Referer": "https://testnet.megaeth.com/",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36",
}


def load_config():
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def read_lines(filepath):
    try:
        if filepath.exists():
            with open(filepath, "r", encoding="utf-8") as f:
                return [line.strip() for line in f if line.strip()]
    except Exception as e:
        console.print(f"[red]Error reading {filepath}: {e}[/red]")
    return []


def read_wallets():
    wallets = read_lines(WALLETS_FILE)
    try:
        if WALLETS_JSON_FILE.exists():
            with open(WALLETS_JSON_FILE, "r", encoding="utf-8") as f:
                wallets_json = json.load(f)
                if isinstance(wallets_json, list):
                    wallets += [e["address"] for e in wallets_json if isinstance(e, dict) and "address" in e]
                elif isinstance(wallets_json, dict) and "address" in wallets_json:
                    wallets.append(wallets_json["address"])
    except Exception as e:
        console.print(f"[yellow]Warning: {WALLETS_JSON_FILE}: {e}[/yellow]")
    return wallets


proxies_list = []
proxy_index = 0
PROXY_LOCK = threading.Lock()


def format_proxy(proxy_str):
    parts = proxy_str.split(":")
    if len(parts) == 4:
        ip, port, user, passwd = parts
        formatted = f"http://{user}:{passwd}@{ip}:{port}"
        return {"http": formatted, "https": formatted}
    elif len(parts) == 2:
        ip, port = parts
        formatted = f"http://{ip}:{port}"
        return {"http": formatted, "https": formatted}
    raise ValueError(f"Invalid proxy format: {proxy_str}")


def get_next_proxy():
    global proxy_index
    with PROXY_LOCK:
        if not proxies_list:
            return None
        proxy = proxies_list[proxy_index % len(proxies_list)]
        proxy_index += 1
        return proxy


def get_current_ip(proxy_str):
    try:
        proxy_dict = format_proxy(proxy_str)
    except ValueError:
        return "Invalid Proxy"
    try:
        r = requests.get("https://api.myip.com", proxies=proxy_dict, timeout=30)
        if r.status_code == 200:
            return r.json().get("ip", "Unknown IP")
    except Exception:
        pass
    return "Unknown IP"


def solve_turnstile(api_key, sitekey, page_url):
    try:
        solver = TwoCaptcha(api_key)
        console.print("[yellow]Requesting Turnstile captcha solution from 2Captcha...[/yellow]")
        result = solver.turnstile(sitekey=sitekey, url=page_url)
        token = result.get("code")
        if token:
            console.print("[green]Turnstile captcha solved successfully.[/green]")
            return token
    except Exception as e:
        console.print(f"[red]Captcha error: {e}[/red]")
    return None


def megaeth_claim(wallet, token, proxy_str, api_url):
    try:
        proxy_dict = format_proxy(proxy_str)
    except ValueError:
        return None
    try:
        response = requests.post(
            api_url,
            json={"addr": wallet, "token": token},
            headers=HEADERS,
            proxies=proxy_dict,
            timeout=60,
        )
        return response.json()
    except Exception as e:
        console.print(f"[red]Claim API error for {wallet}: {e}[/red]")
        return None


def process_wallet(wallet, config, stop_event):
    global proxies_list
    api_key = config.get("two_captcha_api_key", "")
    sitekey = config.get("turnstile_sitekey", "0x4AAAAAABA4JXCaw9E2Py-9")
    page_url = config.get("turnstile_page_url", "https://testnet.megaeth.com/")
    api_url = config.get("megaeth_api_url", "https://carrot.megaeth.com/claim")

    console.print(f"[cyan]Processing wallet: {wallet}[/cyan]")
    max_retries = 3
    attempts = 0
    success_flag = False

    while attempts < max_retries and not success_flag:
        if stop_event.is_set():
            return

        proxy_str = get_next_proxy() if proxies_list else None
        if proxy_str:
            ip = get_current_ip(proxy_str)
            console.print(f"[yellow]Attempt {attempts + 1}: Using proxy IP {ip}[/yellow]")
            proxy_for_claim = proxy_str
        else:
            proxy_for_claim = None
            console.print(f"[yellow]Attempt {attempts + 1}: Direct connection (no proxy)[/yellow]")

        captcha_token = solve_turnstile(api_key, sitekey, page_url)
        if not captcha_token:
            attempts += 1
            continue

        if proxy_for_claim:
            resp = megaeth_claim(wallet, captcha_token, proxy_for_claim, api_url)
        else:
            try:
                response = requests.post(
                    api_url,
                    json={"addr": wallet, "token": captcha_token},
                    headers=HEADERS,
                    timeout=60,
                )
                resp = response.json()
            except Exception as e:
                console.print(f"[red]Claim error: {e}[/red]")
                resp = None

        if resp:
            tx_hash = resp.get("txhash", "")
            message = resp.get("message", "").lower()
            console.print(f"[cyan]Response: https://www.megaexplorer.xyz/tx/{tx_hash}[/cyan]")
            if "less than" in message and "hours have passed" in message:
                console.print(f"[yellow]Wallet {wallet} claimed recently. Skipping.[/yellow]")
                return
            if resp.get("success", False) and tx_hash:
                success_flag = True
            else:
                console.print("[red]Claim not successful, retrying...[/red]")
        else:
            console.print("[red]No response from API, retrying...[/red]")

        attempts += 1

    if success_flag:
        console.print(f"[green]Claim SUCCESS for wallet {wallet}[/green]")
        with open(SUCCESS_FILE, "a", encoding="utf-8") as f:
            f.write(wallet + "\n")
    else:
        console.print(f"[red]Claim FAILED for wallet {wallet}[/red]")
        with open(FAIL_FILE, "a", encoding="utf-8") as f:
            f.write(wallet + "\n")


def run_faucet():
    global proxies_list
    config = load_config()
    proxies_list = read_lines(PROXIES_FILE)
    wallets = read_wallets()

    if not wallets:
        console.print("[red]No wallets found.[/red]")
        return

    stop_event = threading.Event()
    threads = config.get("threads", 5)

    console.print("[cyan]Starting MegaETH Faucet Claim Process...[/cyan]")
    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {
            executor.submit(process_wallet, w, config, stop_event): w
            for w in wallets
        }
        try:
            for future in as_completed(futures):
                future.result()
        except KeyboardInterrupt:
            stop_event.set()
            for f in futures:
                f.cancel()
            raise
