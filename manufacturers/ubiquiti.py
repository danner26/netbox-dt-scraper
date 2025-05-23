import requests
import json

# Assuming DEVICE_INFO_URLS and MANUFACTURER will be passed to the class instance
# or handled by the script that instantiates this class.
# from manufacturers.config import MANUFACTURER, DEVICE_INFO_URLS # This line would be removed or handled differently

class Ubiquiti:
    def __init__(self, device_info_urls: list, manufacturer_name: str = "Ubiquiti"):
        """
        Initializes the Ubiquiti.
        :param device_info_urls: A list of URLs to fetch category/device information from.
        :param manufacturer_name: The name of the manufacturer.
        """
        self.device_info_urls = device_info_urls
        self.manufacturer_name = manufacturer_name
        print(f"Initialized {self.manufacturer_name}Scraper with {len(self.device_info_urls)} URLs.")

    def fetch_single_json(self, url: str):
        """
        Fetches JSON data from a single URL and parses it.
        Returns the parsed JSON object (dict or list) or None if an error occurs.
        """
        print(f"\nFetching data from: {url}")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)
            try:
                parsed_data = response.json()
                print(f"Successfully fetched and parsed JSON from {url}")
                return parsed_data
            except json.JSONDecodeError:
                print(f"Error: Could not decode JSON from {url}. Content might not be valid JSON.")
                print(f"Response text (first 200 chars): {response.text[:200]}...")
                return None
        except requests.exceptions.HTTPError as http_err:
            print(f"HTTP error occurred while fetching {url}: {http_err}")
        except requests.exceptions.ConnectionError as conn_err:
            print(f"Connection error occurred while fetching {url}: {conn_err}")
        except requests.exceptions.Timeout as timeout_err:
            print(f"Timeout error occurred while fetching {url}: {timeout_err}")
        except requests.exceptions.RequestException as req_err:
            print(f"An error occurred while fetching {url}: {req_err}")
        return None

    def extract_product_slugs(self, top_level_categories: dict) -> list:
        """
        Extracts product slugs from the given top-level categories JSON structure.
        """
        product_slugs = []
        if not isinstance(top_level_categories, dict):
            print("Error: top_level_categories is not a dictionary.")
            return product_slugs

        if 'pageProps' in top_level_categories and \
           isinstance(top_level_categories['pageProps'], dict) and \
           'subCategoriesWithProducts' in top_level_categories['pageProps'] and \
           isinstance(top_level_categories['pageProps']['subCategoriesWithProducts'], list):

            subcategories = top_level_categories['pageProps']['subCategoriesWithProducts']

            for subcategory in subcategories:
                if isinstance(subcategory, dict) and \
                   'products' in subcategory and \
                   isinstance(subcategory['products'], list):
                    for product in subcategory['products']:
                        if isinstance(product, dict) and 'slug' in product:
                            product_slugs.append(product['slug'])
                        else:
                            product_name = product.get('name', 'N/A') if isinstance(product, dict) else 'N/A'
                            print(f"Warning: Product found without a 'slug' or product is not a dict: {product_name}")
                else:
                    subcategory_id = subcategory.get('id', 'N/A') if isinstance(subcategory, dict) else 'N/A'
                    print(f"Warning: Subcategory '{subcategory_id}' has no 'products' list, or 'products' is not a list, or subcategory is not a dict.")
        else:
            print("Error: Could not find 'pageProps' or 'subCategoriesWithProducts', or they are not of expected types in the JSON data.")

        if product_slugs:
            print(f"\nProduct Slugs Extracted: {len(product_slugs)}")
        else:
            print("\nNo product slugs were extracted.")
        return product_slugs

    def get_all_product_urls(self) -> list:
        """
        Fetches category information, extracts product slugs,
        and constructs full product URLs for the configured manufacturer.
        Uses instance's device_info_urls.
        Returns a list of product URLs.
        """
        generated_product_urls = {}

        if not self.device_info_urls:
            print(f"No DEVICE_INFO_URLS found for {self.manufacturer_name} to process.")
            return generated_product_urls

        for category_url in self.device_info_urls:
            print(f"\nProcessing Category URL for {self.manufacturer_name}: {category_url}")
            category_json_data = self.fetch_single_json(category_url) # Call method using self

            if category_json_data:
                slug_list = self.extract_product_slugs(category_json_data) # Call method using self

                if slug_list:
                    base_url_for_products = category_url
                    if base_url_for_products.endswith(".json"):
                        base_url_for_products = base_url_for_products[:-5]

                    if base_url_for_products.endswith('/'):
                        base_url_for_products = base_url_for_products[:-1]

                    print(f"--- Generating product URLs for {len(slug_list)} slugs from {category_url} ---")
                    for slug in slug_list:
                        clean_slug = slug.lstrip('/')
                        generated_product_urls[slug] = {"url": f"{base_url_for_products}/{clean_slug}.json"}
                else:
                    print(f"No product slugs extracted from {category_url}.")
            else:
                print(f"No data was successfully fetched or parsed from {category_url}.")

        if generated_product_urls:
            print(f"\n--- Total {len(generated_product_urls)} Product URLs Generated for {self.manufacturer_name} ---")
        else:
            print(f"\n--- No Product URLs Were Generated Overall for {self.manufacturer_name} ---")

        return generated_product_urls

    def get_product_data(self, product) -> dict:
        """
        Placeholder for a method to fetch product data from the generated URLs.
        This method can be implemented later as needed.
        """
        print("get_product_data() method is not yet implemented.")
        return {}

# Example of how to use the class if this script is run directly
if __name__ == "__main__":
    # You would typically get these URLs from your config system
    sample_device_urls = [
        "https://techspecs.ui.com/_next/data/EAllru7-KUKtVLnVBqKwQ/unifi/cloud-gateways.json"
        # Add more URLs if needed for testing
    ]

    print("Testing Ubiquiti class...")
    scraper_instance = Ubiquiti(device_info_urls=sample_device_urls, manufacturer_name="Ubiquiti Test")

    product_urls_list = scraper_instance.get_all_product_urls()

    if product_urls_list:
        print("\nList of all generated product URLs from class instance:")
        for p_url in product_urls_list:
            print(p_url)
    else:
        print("\nNo product URLs were generated by the class instance.")
