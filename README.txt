🌐 RainTrigger — Automatically Refresh Rainmeter When Bluetooth Headphones Are Connected

If your Rainmeter visualizer stops working after reconnecting your Bluetooth headphones — RainTrigger will fix that automatically!

━━━━━━━━━━━━━━━━━━━ 📦 SETUP ━━━━━━━━━━━━━━━━━━━

1. 🔍 Find the MAC address of your Bluetooth headphones.

     📌 In PowerShell, run the following command:
	
	```PowerShell
	Get-PnpDevice | Where-Object { $_.FriendlyName -like "*part of device name*" }
	```

     ▶ Example for JBL:

	```PowerShell
	Get-PnpDevice | Where-Object { $_.FriendlyName -like "*JBL*" }
	```

    💡 Look for an address in the format AA:BB:CC:DD:EE:FF.

2. 🛠 Insert the MAC address(es) into the `raintrigger_config.json` file located next to the executable:

    ```json
    {
      "mac_addresses": [
        "AA:BB:CC:DD:EE:FF",
        "11:22:33:44:55:66"
      ],
      "autostart": true
    }
    ```

3. ▶ Launch `RainTrigger.exe`

RainTrigger will run silently in the background and automatically refresh Rainmeter when your Bluetooth device connects.

━━━━━━━━━━━━━━━━━━━ 📝 NOTES ━━━━━━━━━━━━━━━━━━━

• The code is fully open-source.  
• The app does not interfere with system processes.  
• All configuration changes are stored in `raintrigger_config.json`.  
• With autostart enabled, RainTrigger will launch automatically with Windows.
