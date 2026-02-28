#!/usr/bin/env python3
"""
MegaETH Faucet - Rich Interactive Interface
Automated token claiming from MegaETH Testnet Faucet
"""

import os
import sys
import subprocess

from utils import ensure_env
import json
from pathlib import Path

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import box
from rich.text import Text
from rich.style import Style

# Project root
PROJECT_ROOT = Path(__file__).parent
os.chdir(PROJECT_ROOT)

console = Console()

# MegaETH Logo (ASCII Art)
MEGAETH_LOGO = r"""
 __  __                          ______ _______ _    _            ______                   _   
|  \/  |                        |  ____|__   __| |  | |          |  ____|                 | |  
| \  / |   ___    __ _    __ _  | |__     | |  | |__| |  ______  | |__ __ _ _   _  ___ ___| |_ 
| |\/| |  / _ \  / _` |  / _` | |  __|    | |  |  __  | |______| |  __/ _` | | | |/ __/ _ \ __|
| |  | | |  __/ | (_| | | (_| | | |____   | |  | |  | |          | | | (_| | |_| | (_|  __/ |_ 
|_|  |_|  \___|  \__, |  \__,_| |______|  |_|  |_|  |_|          |_|  \__,_|\__,_|\___\___|\__|
                  __/ |                                                                        
                 |___/                                                                         
"""


def load_config():
    """Load configuration from config.json"""
    config_path = PROJECT_ROOT / "config.json"
    default_config = {
        "two_captcha_api_key": "",
        "threads": 5,
        "turnstile_sitekey": "0x4AAAAAABA4JXCaw9E2Py-9",
        "turnstile_page_url": "https://testnet.megaeth.com/",
        "megaeth_api_url": "https://carrot.megaeth.com/claim",
        "rpc_endpoint": "https://carrot.megaeth.com/rpc",
    }
    try:
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                return {**default_config, **json.load(f)}
    except Exception as e:
        console.print(f"[red]Error loading config: {e}[/red]")
    return default_config


def save_config(config):
    """Save configuration to config.json"""
    config_path = PROJECT_ROOT / "config.json"
    try:
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        return True
    except Exception as e:
        console.print(f"[red]Error saving config: {e}[/red]")
        return False


def show_header():
    """Display the main header with logo and info table"""
    console.clear()
    console.print(Panel(Text(MEGAETH_LOGO, style="bold cyan"), 
                       border_style="cyan", box=box.DOUBLE, padding=(0, 1)))
    
    info_table = Table(show_header=False, box=box.ROUNDED, border_style="dim")
    info_table.add_column("", style="cyan")
    info_table.add_column("", style="white")
    info_table.add_row("Project", "MegaETH Faucet Automation")
    info_table.add_row("Network", "MegaETH Testnet (Layer 2)")
    info_table.add_row("Purpose", "Automated testnet token claiming")
    info_table.add_row("Features", "2Captcha, Proxy support, Multi-threading")
    console.print(Panel(info_table, title="[bold]Project Info[/bold]", border_style="blue", padding=(0, 1)))
    console.print()


def install_dependencies():
    """Install all required Python packages"""
    show_header()
    console.print("[bold]Install Dependencies[/bold]\n", style="cyan")
    
    deps = ["requests", "colorama", "twocaptcha", "pytz", "tzlocal", "rich"]
    deps_table = Table(title="Packages to Install", box=box.ROUNDED, border_style="green")
    deps_table.add_column("#", style="dim")
    deps_table.add_column("Package", style="cyan")
    deps_table.add_column("Purpose", style="white")
    deps_table.add_row("1", "requests", "HTTP requests")
    deps_table.add_row("2", "colorama", "Terminal colors")
    deps_table.add_row("3", "twocaptcha", "2Captcha API integration")
    deps_table.add_row("4", "pytz", "Timezone support")
    deps_table.add_row("5", "tzlocal", "Local timezone")
    deps_table.add_row("6", "rich", "Rich terminal UI")
    console.print(deps_table)
    console.print()
    
    if Confirm.ask("Proceed with installation?", default=True):
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Installing packages...", total=None)
            try:
                subprocess.run(
                    [sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "-q"],
                    check=True,
                    capture_output=True,
                )
                progress.update(task, description="[green]Installation complete!")
                console.print("\n[bold green]All dependencies installed successfully![/bold green]")
            except subprocess.CalledProcessError as e:
                progress.update(task, description="[red]Installation failed!")
                console.print(f"\n[bold red]Error: {e}[/bold red]")
    else:
        console.print("[yellow]Installation cancelled.[/yellow]")
    
    Prompt.ask("\nPress Enter to return to menu")


def settings_menu():
    """Settings configuration menu"""
    show_header()
    console.print("[bold]Settings[/bold]\n", style="cyan")
    
    config = load_config()
    
    settings_table = Table(title="Current Configuration", box=box.ROUNDED, border_style="yellow")
    settings_table.add_column("Setting", style="cyan")
    settings_table.add_column("Value", style="white")
    settings_table.add_column("Description", style="dim")
    settings_table.add_row("2Captcha API Key", config.get("two_captcha_api_key", "")[:20] + "..." if config.get("two_captcha_api_key") else "(not set)", "Required for captcha solving")
    settings_table.add_row("Threads", str(config.get("threads", 5)), "Number of parallel workers")
    settings_table.add_row("RPC Endpoint", config.get("rpc_endpoint", ""), "MegaETH RPC URL")
    console.print(settings_table)
    console.print()
    
    console.print("[bold]Edit settings:[/bold]")
    new_key = Prompt.ask("2Captcha API Key (press Enter to keep current)", default=config.get("two_captcha_api_key", ""))
    if new_key:
        config["two_captcha_api_key"] = new_key
    
    new_threads = IntPrompt.ask("Number of threads (1-20)", default=config.get("threads", 5))
    if 1 <= new_threads <= 20:
        config["threads"] = new_threads
    
    if save_config(config):
        console.print("\n[green]Settings saved successfully![/green]")
    else:
        console.print("\n[red]Failed to save settings.[/red]")
    
    Prompt.ask("\nPress Enter to return to menu")


def add_wallet():
    """Add wallet addresses"""
    show_header()
    console.print("[bold]Add Wallet[/bold]\n", style="cyan")
    
    wallet_table = Table(title="Wallet Configuration", box=box.ROUNDED, border_style="blue")
    wallet_table.add_column("File", style="cyan")
    wallet_table.add_column("Format", style="white")
    wallet_table.add_column("Location", style="dim")
    wallet_table.add_row("wallet.txt", "One address per line", str(PROJECT_ROOT / "wallet.txt"))
    wallet_table.add_row("wallets.json", '{"address": "0x..."}', str(PROJECT_ROOT / "wallets.json"))
    console.print(wallet_table)
    console.print()
    
    console.print("[dim]Enter wallet address (0x...) or press Enter to open file:[/dim]")
    address = Prompt.ask("Wallet address")
    
    if address:
        if address.startswith("0x") and len(address) == 42:
            wallet_file = PROJECT_ROOT / "wallet.txt"
            with open(wallet_file, "a", encoding="utf-8") as f:
                f.write(address + "\n")
            console.print(f"[green]Wallet {address[:10]}... added to wallet.txt[/green]")
        else:
            console.print("[red]Invalid Ethereum address format.[/red]")
    else:
        wallet_file = PROJECT_ROOT / "wallet.txt"
        if not wallet_file.exists():
            wallet_file.touch()
        console.print(f"[yellow]Open {wallet_file} and add addresses (one per line)[/yellow]")
    
    Prompt.ask("\nPress Enter to return to menu")


def run_faucet():
    """Execute the faucet claim process"""
    show_header()
    console.print("[bold]Run Faucet[/bold]\n", style="cyan")
    
    # Save config for faucet module
    config = load_config()
    config_path = PROJECT_ROOT / "config.json"
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)
    
    if not config.get("two_captcha_api_key"):
        console.print("[red]Error: 2Captcha API key not configured. Go to Settings first.[/red]")
        Prompt.ask("\nPress Enter to return to menu")
        return
    
    wallet_file = PROJECT_ROOT / "wallet.txt"
    if not wallet_file.exists() or not wallet_file.read_text().strip():
        console.print("[red]Error: No wallets found. Add wallets first.[/red]")
        Prompt.ask("\nPress Enter to return to menu")
        return
    
    console.print("[yellow]Starting faucet claim process...[/yellow]")
    console.print("[dim]Press Ctrl+C to stop[/dim]\n")
    
    try:
        import faucet_module
        faucet_module.run_faucet()
    except ImportError:
        console.print("[red]Faucet module not found. Ensure faucet_module.py exists.[/red]")
    except KeyboardInterrupt:
        console.print("\n[yellow]Process interrupted by user.[/yellow]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
    
    Prompt.ask("\nPress Enter to return to menu")


def check_balance():
    """Check wallet balances"""
    show_header()
    console.print("[bold]Check Balance[/bold]\n", style="cyan")
    
    try:
        import balance_module
        balance_module.check_balances()
    except ImportError:
        console.print("[red]Balance module not found. Ensure balance_module.py exists.[/red]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
    
    Prompt.ask("\nPress Enter to return to menu")


def view_logs():
    """View success and failure logs"""
    show_header()
    console.print("[bold]View Logs[/bold]\n", style="cyan")
    
    logs_table = Table(title="Log Files", box=box.ROUNDED, border_style="magenta")
    logs_table.add_column("File", style="cyan")
    logs_table.add_column("Purpose", style="white")
    logs_table.add_column("Status", style="green")
    
    success_file = PROJECT_ROOT / "success.txt"
    fail_file = PROJECT_ROOT / "fail.txt"
    
    for path, purpose in [(success_file, "Successful claims"), (fail_file, "Failed attempts")]:
        exists = path.exists()
        lines = len(path.read_text().splitlines()) if exists else 0
        status = f"{lines} entries" if exists else "Empty/Not found"
        logs_table.add_row(path.name, purpose, status)
    
    console.print(logs_table)
    console.print()
    
    choice = Prompt.ask("View [s]uccess or [f]ail logs? (s/f/Enter to skip)", default="")
    
    if choice.lower() == "s" and success_file.exists():
        console.print(Panel(success_file.read_text(encoding="utf-8") or "(empty)", title="success.txt", border_style="green"))
    elif choice.lower() == "f" and fail_file.exists():
        console.print(Panel(fail_file.read_text(encoding="utf-8") or "(empty)", title="fail.txt", border_style="red"))
    
    Prompt.ask("\nPress Enter to return to menu")


def about_menu():
    """About MegaETH and the project"""
    show_header()
    console.print("[bold]About MegaETH Faucet[/bold]\n", style="cyan")
    
    about_table = Table(title="MegaETH Overview", box=box.ROUNDED, border_style="cyan")
    about_table.add_column("Property", style="cyan")
    about_table.add_column("Description", style="white")
    about_table.add_row("Type", "Ethereum Layer 2 scaling solution")
    about_table.add_row("Throughput", "100,000+ TPS (transactions per second)")
    about_table.add_row("Latency", "Sub-millisecond, real-time blockchain")
    about_table.add_row("EVM", "Fully compatible with Ethereum Virtual Machine")
    about_table.add_row("Testnet", "Tokens have no real-world value")
    console.print(about_table)
    console.print()
    
    features_table = Table(title="Script Features", box=box.ROUNDED, border_style="green")
    features_table.add_column("Feature", style="cyan")
    features_table.add_column("Description", style="white")
    features_table.add_row("2Captcha", "Automatic Turnstile captcha solving")
    features_table.add_row("Proxies", "Supports ip:port and ip:port:user:pass")
    features_table.add_row("Multi-threaded", "Concurrent wallet processing")
    features_table.add_row("Wallets", "wallet.txt + wallets.json support")
    features_table.add_row("Logging", "success.txt and fail.txt")
    console.print(features_table)
    console.print()
    
    console.print(Panel(
        "Official: https://megaeth.org\nDocs: https://docs.megaeth.com\nTestnet: https://testnet.megaeth.com",
        title="Links",
        border_style="blue"
    ))
    
    Prompt.ask("\nPress Enter to return to menu")


def proxy_config():
    """Proxy configuration help"""
    show_header()
    console.print("[bold]Proxy Configuration[/bold]\n", style="cyan")
    
    proxy_table = Table(title="Proxy Format", box=box.ROUNDED, border_style="yellow")
    proxy_table.add_column("Format", style="cyan")
    proxy_table.add_column("Example", style="white")
    proxy_table.add_row("Without auth", "192.168.1.100:8080")
    proxy_table.add_row("With auth", "31.56.139.207:6276:username:password")
    console.print(proxy_table)
    console.print()
    
    proxy_file = PROJECT_ROOT / "proxy.txt"
    if not proxy_file.exists():
        proxy_file.touch()
    
    console.print(f"[dim]Edit {proxy_file} - one proxy per line[/dim]")
    if proxy_file.exists():
        content = proxy_file.read_text(encoding="utf-8")
        if content.strip():
            console.print(Panel(content, title="Current proxy.txt", border_style="dim"))
        else:
            console.print("[yellow]proxy.txt is empty. Add proxies for rotation.[/yellow]")
    
    Prompt.ask("\nPress Enter to return to menu")


@ensure_env
def main_menu():
    """Display main menu and handle selection"""
    while True:
        show_header()
        
        menu_table = Table(show_header=False, box=box.DOUBLE_EDGE, border_style="bright_blue", title="[bold]Main Menu[/bold]")
        menu_table.add_column("Key", style="bold cyan", width=4)
        menu_table.add_column("Action", style="white")
        menu_table.add_column("Description", style="dim")
        menu_table.add_row("1", "Install Dependencies", "Install required Python packages")
        menu_table.add_row("2", "Settings", "Configure 2Captcha API key, threads, RPC")
        menu_table.add_row("3", "Add Wallet", "Add wallet addresses (wallet.txt)")
        menu_table.add_row("4", "Proxy Config", "Configure proxies (proxy.txt)")
        menu_table.add_row("5", "Run Faucet", "Start automated token claiming")
        menu_table.add_row("6", "Check Balance", "Check wallet balances on MegaETH")
        menu_table.add_row("7", "View Logs", "View success.txt and fail.txt")
        menu_table.add_row("8", "About", "About MegaETH and this project")
        menu_table.add_row("0", "Exit", "Exit the application")
        console.print(menu_table)
        console.print()
        
        choice = Prompt.ask("Select option", default="1")
        
        actions = {
            "1": install_dependencies,
            "2": settings_menu,
            "3": add_wallet,
            "4": proxy_config,
            "5": run_faucet,
            "6": check_balance,
            "7": view_logs,
            "8": about_menu,
        }
        
        if choice == "0":
            console.print("\n[cyan]Goodbye![/cyan]")
            break
        
        if choice in actions:
            actions[choice]()
        else:
            console.print("[red]Invalid option.[/red]")
            Prompt.ask("Press Enter to continue")


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        console.print("\n[cyan]Exiting...[/cyan]")
