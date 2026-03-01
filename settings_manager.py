# --- START OF FILE settings_manager.py ---
import json
import os
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from utils import CONFIG_FILE

console = Console()

# Defined Models
MODELS = {
    "1": ("gemini-3.0-flash", "Flash 2.0 (Fastest, High Rate Limits, Free-tier friendly)"),
    "2": ("gemini-2.5-flash", "Flash 1.5 (Stable, Standard Speed)"),
}

DEFAULT_SETTINGS = {
    "GOOGLE_API_KEY": "",
    "CLEANUP_MODE": "Ask",  # Options: Always, Ask, Never
    "AI_MODEL": "gemini-2.0-flash"
}

class SettingsManager:
    def __init__(self):
        self.settings = self.load_settings()

    def load_settings(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    data = json.load(f)
                    # Merge defaults in case new keys were added
                    for k, v in DEFAULT_SETTINGS.items():
                        if k not in data:
                            data[k] = v
                    return data
            except:
                return DEFAULT_SETTINGS.copy()
        return DEFAULT_SETTINGS.copy()

    def save_settings(self):
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.settings, f, indent=4)

    def get(self, key):
        return self.settings.get(key)

    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()

    # --- MENUS ---
    def configure_cleanup(self):
        console.print("\n[bold cyan]Cleanup Configuration[/bold cyan]")
        console.print("When should the program delete raw CSV files after compiling an EPUB?")
        console.print("1. [green]Always[/green] (Delete automatically without asking)")
        console.print("2. [yellow]Ask[/yellow] (Prompt me every time)")
        console.print("3. [red]Never[/red] (Keep files)")
        
        choice = Prompt.ask("Select option", choices=["1", "2", "3"])
        mapping = {"1": "Always", "2": "Ask", "3": "Never"}
        self.set("CLEANUP_MODE", mapping[choice])
        console.print(f"[green]Cleanup mode set to: {mapping[choice]}[/green]")

    def configure_model(self):
        console.print("\n[bold cyan]Select Gemini Model[/bold cyan]")
        for key, (model_id, desc) in MODELS.items():
            color = "green" if "flash" in model_id else "yellow"
            console.print(f"[{key}] [{color}]{model_id}[/{color}]: {desc}")
            
        choice = Prompt.ask("Select Model", choices=list(MODELS.keys()))
        selected_model = MODELS[choice][0]
        self.set("AI_MODEL", selected_model)
        console.print(f"[green]AI Model set to: {selected_model}[/green]")

    def configure_api_key(self):
        current = self.get("GOOGLE_API_KEY")
        if current:
            console.print(f"[dim]Current Key: {current[:5]}...{current[-3:]}[/dim]")
        
        new_key = Prompt.ask("Enter new Google API Key (or press Enter to keep current)", password=True)
        if new_key.strip():
            self.set("GOOGLE_API_KEY", new_key.strip())
            os.environ["GOOGLE_API_KEY"] = new_key.strip()
            console.print("[green]API Key saved![/green]")

    def run_menu(self):
        while True:
            console.clear()
            console.print(Panel.fit("[bold magenta]⚙️  Settings Menu[/bold magenta]"))
            console.print(f"Current Model: [cyan]{self.get('AI_MODEL')}[/cyan]")
            console.print(f"Cleanup Mode:  [cyan]{self.get('CLEANUP_MODE')}[/cyan]")
            console.print(f"API Key Saved: [cyan]{'Yes' if self.get('GOOGLE_API_KEY') else 'No'}[/cyan]\n")

            console.print("[1] 🔑 Set/Update API Key")
            console.print("[2] 🧠 Change AI Model")
            console.print("[3] 🧹 Configure Auto-Cleanup")
            console.print("[0] 🔙 Back to Main Menu")

            choice = Prompt.ask("Select option", choices=["1", "2", "3", "0"])

            if choice == "1": self.configure_api_key()
            elif choice == "2": self.configure_model()
            elif choice == "3": self.configure_cleanup()
            elif choice == "0": break