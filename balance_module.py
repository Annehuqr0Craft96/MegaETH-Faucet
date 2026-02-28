#!/usr/bin/env python3
"""
MegaETH Faucet - Balance checker
"""

import json
from pathlib import Path

import requests
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

PROJECT_ROOT = Path(__file__).parent
console = Console()

CONFIG_FILE = PROJECT_ROOT / "config.json"
WALLETS_FILE = PROJECT_ROOT / "wallet.txt"
WALLETS_JSON_FILE = PROJECT_ROOT / "wallets.json"


def load_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {"rpc_endpoint": "https://carrot.megaeth.com/rpc"}


def read_wallets():
    wallets = []
    if WALLETS_FILE.exists():
        with open(WALLETS_FILE, "r", encoding="utf-8") as f:
            for line in f:
                addr = line.strip()
                if addr and addr.startswith("0x"):
                    wallets.append({"address": addr})
    try:
        if WALLETS_JSON_FILE.exists():
            with open(WALLETS_JSON_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    for item in data:
                        if isinstance(item, dict) and "address" in item:
                            wallets.append(item)
                elif isinstance(data, dict) and "address" in data:
                    wallets.append(data)
    except Exception:
        pass
    return wallets


def get_balance(address, rpc_url):
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getBalance",
        "params": [address, "latest"],
        "id": 1,
    }
    try:
        response = requests.post(rpc_url, json=payload, timeout=30)
        response.raise_for_status()
        result = response.json().get("result")
        if result:
            balance_wei = int(result, 16)
            balance_eth = balance_wei / (10**18)
            return balance_eth
    except Exception as e:
        console.print(f"[red]Error fetching balance for {address}: {e}[/red]")
    return None


def check_balances():
    config = load_config()
    rpc_url = config.get("rpc_endpoint", "https://carrot.megaeth.com/rpc")
    wallets = read_wallets()

    if not wallets:
        console.print("[red]No wallets found. Add wallets first.[/red]")
        return

    table = Table(title="Wallet Balances (MegaETH Testnet)", box=box.ROUNDED, border_style="cyan")
    table.add_column("#", style="dim")
    table.add_column("Address", style="cyan")
    table.add_column("Balance (ETH)", style="green")
    table.add_column("Status", style="white")

    empty_wallets = []
    for i, w in enumerate(wallets, 1):
        addr = w.get("address", "")
        balance = get_balance(addr, rpc_url)
        if balance is None:
            status = "[red]Error[/red]"
        elif balance == 0:
            status = "[yellow]Empty[/yellow]"
            empty_wallets.append(addr)
        else:
            status = "[green]OK[/green]"
        table.add_row(str(i), addr[:16] + "..." + addr[-6:], f"{balance:.6f}" if balance is not None else "N/A", status)

    console.print(table)

    if empty_wallets:
        empty_file = PROJECT_ROOT / "empty.txt"
        with open(empty_file, "w", encoding="utf-8") as f:
            for addr in empty_wallets:
                f.write(addr + "\n")
        console.print(f"\n[yellow]Saved {len(empty_wallets)} empty wallet(s) to empty.txt[/yellow]")
