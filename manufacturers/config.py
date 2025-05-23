# Example configuration
MANUFACTURERS_DATA = {
    "ubiquiti": {
        "module_name": "ubiquiti", # Corresponds to ubiquiti.py
        "device_info_urls": [
            "https://techspecs.ui.com/_next/data/EAllru7-KUKtVLnVBqKwQ/unifi/cloud-gateways.json"
        ],
        "data_points": [
            {
                "output_key": "title", # The key name in the final parsed dictionary
                "type": "direct_path", # Type of data extraction
                "path": ["title"],     # Path relative to product_json_data['pageProps']['product']
                "transform": None,     # Optional transformation function
                "default": None        # Optional default value if path not found
            },
            {
                "output_key": "short_description",
                "type": "direct_path",
                "path": ["shortDescription"],
                "transform": None,
                "default": None
            },
            {
                "output_key": "product_name", # Example: UDM-SE
                "type": "direct_path",
                "path": ["name"],
                "transform": None,
                "default": None
            },
            {
                "output_key": "weight",
                "type": "technical_spec", # Custom type for technical specifications
                "spec_slug": "weight",    # The slug to look for (e.g., "weight", "dimensions")
                "transform": "weight_transform", # Transformation function name
                "default": None
            },
            {
                "output_key": "u_height",
                "type": "technical_spec", # Custom type for technical specifications
                "spec_slug": "form-factor",    # The slug to look for (e.g., "weight", "dimensions")
                "transform": "u_height_transform", # Transformation function name
                "default": None
            }
        ]
    },
}

# You can still have a simple list of manufacturer keys if needed elsewhere
MANUFACTURERS = list(MANUFACTURERS_DATA.keys())
