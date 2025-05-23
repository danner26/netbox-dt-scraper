import importlib

from manufacturers.config import MANUFACTURERS
# import ubiquiti # Import the ubiquiti module

def main():
    print("Starting the main scraper process...")

    for manufacturer in MANUFACTURERS:
        try:
            test = importlib.import_module(f"manufacturers.{manufacturer}")
            print(f"Successfully imported {manufacturer}")
        except ImportError:
            print(f"Error: The module '{manufacturer}' could not be found.")

    print(test.product_urls)
    # # Get product URLs from the Ubiquiti module
    # print("\nFetching Ubiquiti product URLs...")
    # ubiquiti_product_urls = ubiquiti.get_all_product_urls()

    # if ubiquiti_product_urls:
    #     print("\n--- Successfully retrieved Ubiquiti product URLs ---")
    #     for url in ubiquiti_product_urls:
    #         print(url)
    #     # Here you can add further processing for these URLs,
    #     # like fetching data for each individual product.
    # else:
    #     print("\nNo product URLs were retrieved from Ubiquiti.")

    # You can add calls to other manufacturer modules here in the future
    # For example:
    # cisco_product_urls = cisco.get_all_product_urls()
    # ...

    print("\nMain scraper process finished.")

if __name__ == "__main__":
    main()
