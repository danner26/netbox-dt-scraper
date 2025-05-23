# Example configuration
MANUFACTURERS_DATA = {
    "ubiquiti": {
        "module_name": "ubiquiti", # Corresponds to ubiquiti.py
        "device_info_urls": [
            "https://techspecs.ui.com/_next/data/EAllru7-KUKtVLnVBqKwQ/unifi/cloud-gateways.json"        ]
    },
}

# You can still have a simple list of manufacturer keys if needed elsewhere
MANUFACTURERS = list(MANUFACTURERS_DATA.keys())
