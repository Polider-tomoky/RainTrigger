import asyncio
import json
import os
import subprocess
import sys
import threading
from pathlib import Path

import customtkinter as ctk
import pystray
from pystray import MenuItem as item
from PIL import Image, ImageDraw
from bleak import BleakScanner

CONFIG_FILE = "raintrigger_config.json"
ICON_FILE = "icon.ico"

# Загрузка и сохранение конфигурации
def load_config():
    if not os.path.exists(CONFIG_FILE):
        config = {"mac_addresses": [], "autostart": False}
        save_config(config)
    else:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
    return config

def save_config(config):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4)

# Обновление Rainmeter
def refresh_rainmeter():
    try:
        subprocess.call([
            r"C:\Program Files\Rainmeter\Rainmeter.exe",
            "!RefreshApp"
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

# Автозагрузка
def add_to_startup():
    startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')
    script_path = Path(sys.argv[0]).resolve()
    shortcut_path = os.path.join(startup_folder, "RainTrigger.bat")
    with open(shortcut_path, "w", encoding="utf-8") as f:
        f.write(f'start /min "" "{script_path}"')

def remove_from_startup():
    startup_folder = os.path.join(os.getenv('APPDATA'), 'Microsoft\\Windows\\Start Menu\\Programs\\Startup')
    shortcut_path = os.path.join(startup_folder, "RainTrigger.bat")
    if os.path.exists(shortcut_path):
        os.remove(shortcut_path)

# Мониторинг Bluetooth
async def monitor_devices():
    config = load_config()
    target_addresses = set(addr.upper() for addr in config.get("mac_addresses", []))
    last_connected = None

    while True:
        devices = await BleakScanner.discover(timeout=3.0)
        connected = any(device.address.upper() in target_addresses for device in devices)

        if last_connected is None:
            last_connected = connected
        elif connected and not last_connected:
            refresh_rainmeter()
            last_connected = connected
        elif not connected and last_connected:
            last_connected = connected

        await asyncio.sleep(5)

def start_monitor():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(monitor_devices())

# GUI окно
def create_control_panel():
    config = load_config()

    def toggle_autostart():
        if autostart_var.get() == 1:
            add_to_startup()
            config["autostart"] = True
        else:
            remove_from_startup()
            config["autostart"] = False
        save_config(config)

    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")

    window = ctk.CTk()
    window.title("RainTrigger")
    window.geometry("300x200")
    window.resizable(False, False)

    ctk.CTkLabel(window, text="RainTrigger", font=("Segoe UI", 20)).pack(pady=(20, 10))

    autostart_var = ctk.IntVar(value=1 if config.get("autostart") else 0)
    ctk.CTkCheckBox(window, text="Run at startup",
                    variable=autostart_var, command=toggle_autostart).pack(pady=10)

    ctk.CTkButton(window, text="Exit", command=window.destroy).pack(pady=(10, 20))

    window.mainloop()

# Трей
def load_icon():
    if os.path.exists(ICON_FILE):
        return Image.open(ICON_FILE)
    else:
        image = Image.new("RGB", (64, 64), "black")
        draw = ImageDraw.Draw(image)
        draw.rectangle((8, 8, 56, 56), outline="white", width=4)
        draw.line((8, 32, 56, 32), fill="white", width=4)
        return image

def setup_tray():
    def quit_program(icon, item):
        icon.stop()
        os._exit(0)

    def open_settings(icon, item):
        threading.Thread(target=create_control_panel).start()

    tray_menu = pystray.Menu(
        item("Settings", open_settings),
        item("Exit", quit_program)
    )

    icon = pystray.Icon("RainTrigger", load_icon(), "RainTrigger", tray_menu)
    icon.run()

# Запуск
if __name__ == "__main__":
    refresh_rainmeter()

    threading.Thread(target=start_monitor, daemon=True).start()
    threading.Thread(target=setup_tray, daemon=False).start()
