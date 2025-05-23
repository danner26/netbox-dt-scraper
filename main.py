import importlib
from manufacturers.config import MANUFACTURERS_DATA # Import the detailed config

# import_dict = {} # We might not need this if we instantiate directly
product_dict = {}

def main():
    print("Starting the main scraper process...")

    for manufacturer_key, config in MANUFACTURERS_DATA.items():
        module_name = config.get("module_name")
        class_name = module_name.capitalize()
        device_urls = config.get("device_info_urls")

        if not all([module_name, class_name, device_urls]):
            print(f"Warning: Missing configuration for {manufacturer_key}. Skipping.")
            continue

        try:
            # Dynamically import the manufacturer's module
            # Assumes manufacturer modules are in the 'manufacturers' package
            module_path = f"manufacturers.{module_name}"
            manufacturer_module = importlib.import_module(module_path)
            print(f"Successfully imported module: {module_path}")

            # Get the class from the imported module
            ScraperClass = getattr(manufacturer_module, class_name)
            print(f"Successfully found class: {class_name} in {module_path}")

            # Instantiate the class
            scraper_instance = ScraperClass(device_info_urls=device_urls, manufacturer_name=manufacturer_key)
            print(f"Successfully instantiated {class_name} for {manufacturer_key}")

            # Call the method on the instance
            product_dict[manufacturer_key] = scraper_instance.get_all_product_urls()
            if product_dict[manufacturer_key]:
                print(f"Retrieved {len(product_dict[manufacturer_key])} product URLs for {manufacturer_key}")
            else:
                print(f"No product URLs retrieved for {manufacturer_key}")

        except ImportError:
            print(f"Error: The module '{module_path}' could not be found or imported.")
        except AttributeError:
            print(f"Error: Class '{class_name}' not found in module '{module_path}'.")
        except TypeError as te:
            # This can happen if the class __init__ signature doesn't match what's passed
            print(f"Error: Could not instantiate class '{class_name}'. Check __init__ arguments: {te}")
        except Exception as e:
            print(f"An unexpected error occurred while processing {manufacturer_key}: {e}")

    print("\n--- All Product URLs ---")
    for manu, products in product_dict.items():
        if products:
            print(f"\n{manu.capitalize()}:")

            for product, data in products.items():
                print(f"  {data['url']}")
        else:
            print(f"\n{manu.capitalize()}: No URLs found.")

    print("\nMain scraper process finished.")

if __name__ == "__main__":
    main()
