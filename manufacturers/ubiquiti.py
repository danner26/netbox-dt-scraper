import requests
import re
import json

# Assuming DEVICE_INFO_URLS and MANUFACTURER will be passed to the class instance
# or handled by the script that instantiates this class.
# from manufacturers.config import MANUFACTURER, DEVICE_INFO_URLS # This line would be removed or handled differently

class Ubiquiti:
    def __init__(self, device_info_urls: list, data_points: list, manufacturer_name: str = "Ubiquiti"):
        """
        Initializes the Ubiquiti.
        :param device_info_urls: A list of URLs to fetch category/device information from.
        :param manufacturer_name: The name of the manufacturer.
        """
        self.device_info_urls = device_info_urls
        self.manufacturer_name = manufacturer_name
        self.data_points = data_points
        print(f"Initialized {self.manufacturer_name}Scraper with {len(self.device_info_urls)} URLs.")

    def fetch_single_json(self, url: str):
        """
        Fetches JSON data from a single URL and parses it.
        Returns the parsed JSON object (dict or list) or None if an error occurs.
        """
        print(f"\nFetching data from: {url}")
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
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
            return None
        except requests.exceptions.ConnectionError as conn_err:
            print(f"Connection error occurred while fetching {url}: {conn_err}")
            return None
        except requests.exceptions.Timeout as timeout_err:
            print(f"Timeout error occurred while fetching {url}: {timeout_err}")
            return None
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

    def _get_value_from_path(self, source_dict: dict, path: list, default=None):
        """Helper to safely get a value from a nested dictionary using a list of keys."""
        current = source_dict
        for key in path:
            if isinstance(current, dict) and key in current:
                current = current[key]
            elif isinstance(current, list) and isinstance(key, int) and 0 <= key < len(current):
                current = current[key] # Access list element by index
            else:
                return default
        return current

    def _transform(self, transform_func, value):
        """
        Applies a transformation function to a value.
        :param transform_func: The transformation function to apply.
        :param value: The value to transform.
        :return: The transformed value.
        """
        print(f"Applying transformation function: {transform_func} to value: {value}")
        if transform_func == "weight_transform": # Use '==' for string comparison
            # Example transformation function for weight
            if isinstance(value, str):
                split_value = value.split()
                # Assuming the value is a string like "5 kg (10.9 lb)"
                try:
                    weight_kg = float(split_value[0])  # Extract the numeric part
                    # Ensure there are enough parts for lbs, and handle potential missing 'lb'
                    weight_lbs_str = "0"
                    for part in split_value:
                        if 'lb' in part:
                            weight_lbs_str = part.replace('(', '').replace('lb', '').replace(')', '').strip()
                            break
                    weight_lbs = float(weight_lbs_str)
                    return {"kg": weight_kg, "lbs": weight_lbs}
                except (ValueError, IndexError) as e:
                    print(f"Warning: Could not convert weight value '{value}': {e}")
                    return value # Return original value or a specific error indicator
        elif transform_func == "u_height_transform": # Use '==' for string comparison
            if isinstance(value, str):
                # Try to find a pattern like "1U", "2U", etc., possibly within parentheses
                match = re.search(r'(\d+)\s*U', value, re.IGNORECASE) # Case-insensitive search for "U"
                if match:
                    try:
                        u_height = int(match.group(1))
                        print(f"Transformed U height value: {u_height} from '{value}'")
                        return u_height
                    except ValueError:
                        print(f"Warning: Could not convert extracted U height '{match.group(1)}' to int from '{value}'.")
                        return 0 # Default to 0 if conversion fails after match
                else:
                    # If no "XU" pattern is found, assume it's not standard rack U height (e.g., "Compact Desktop")
                    print(f"No U height pattern found in '{value}'. Assuming 0U.")
                    return 0 # Default to 0 if no U pattern
            else:
                # If the value isn't a string, it's unlikely to be a U height description
                print(f"Value '{value}' is not a string. Assuming 0U for U height.")
                return 0 # Default to 0 if not a string

        # If no specific transformation matches, return the original value
        print(f"No specific transformation for '{transform_func}'. Returning original value: {value}")
        return value

    def parse_product_data(self, data_to_populate: dict, product_json_data: dict) -> dict:
        """
        Parses product_json_data based on self.data_points and populates data_to_populate.
        :param data_to_populate: The dictionary to add parsed data to (e.g., {'url': '...'}).
        :param product_json_data: The JSON data for a single product.
        :return: The populated data_to_populate dictionary.
        """
        if not product_json_data or not isinstance(product_json_data, dict):
            print("Warning: product_json_data is empty or not a dictionary for parsing.")
            return data_to_populate

        # Base path for most product information
        product_info_root = self._get_value_from_path(product_json_data, ['pageProps', 'product'])
        if not product_info_root or not isinstance(product_info_root, dict):
            print("Warning: 'pageProps.product' path not found or not a dict in product_json_data.")
            return data_to_populate

        for dp_config in self.data_points:
            output_key = dp_config.get("output_key")
            transform = dp_config.get("transform") # Optional transformation function
            dp_type = dp_config.get("type", "direct_path") # Default to direct_path
            default_value = dp_config.get("default") # Will be None if not specified

            if not output_key:
                print(f"Warning: Skipping data point due to missing 'output_key': {dp_config}")
                continue

            value_to_assign = default_value # Initialize with default

            if dp_type == "direct_path":
                path = dp_config.get("path")
                if path and isinstance(path, list):
                    value_to_assign = self._get_value_from_path(product_info_root, path, default_value)
                else:
                    print(f"Warning: Skipping direct_path for '{output_key}' due to missing/invalid 'path'.")

            elif dp_type == "technical_spec":
                spec_slug_to_find = dp_config.get("spec_slug")
                if spec_slug_to_find:
                    item_found = False
                    tech_spec_node = self._get_value_from_path(product_info_root, ["technicalSpecification"])

                    if isinstance(tech_spec_node, dict):
                        sections = self._get_value_from_path(tech_spec_node, ["sections"], [])
                        for section in sections:
                            if item_found: break
                            if not isinstance(section, dict): continue

                            # Ensure the section is of the correct type if necessary, e.g., by checking section.get("__typename")
                            # For now, we assume all sections in the list are relevant or structured similarly.

                            features = self._get_value_from_path(section, ["features"], [])
                            for feature_item in features:
                                if not isinstance(feature_item, dict): continue

                                # feature_item is like:
                                # { "__typename": "SpecificationEntitySectionFeatureEntryText",
                                #   "value": "5 kg (10.9 lb)",
                                #   "feature": { "__typename": "SpecificationSectionFeature", "slug": "weight" } }

                                inner_feature_details = self._get_value_from_path(feature_item, ["feature"])
                                if isinstance(inner_feature_details, dict) and \
                                   self._get_value_from_path(inner_feature_details, ["slug"]) == spec_slug_to_find:
                                    # The actual value is in feature_item['value']
                                    value_to_assign = self._get_value_from_path(feature_item, ["value"], default_value)
                                    item_found = True
                                    break # Found the specific feature, break from features loop

                    if not item_found:
                        # This message can be noisy if specs are often missing, consider logging level or removing
                        # print(f"Info: Technical spec with slug '{spec_slug_to_find}' not found for '{output_key}'. Using default.")
                        pass # value_to_assign remains default_value
                else:
                    print(f"Warning: Skipping technical_spec for '{output_key}' due to missing 'spec_slug'.")

            else:
                print(f"Warning: Unknown data point type '{dp_type}' for '{output_key}'.")

            if transform is not None:
                try:
                    value_to_assign = self._transform(transform, value_to_assign)
                except Exception as e:
                    print(f"Error applying transform function for '{output_key}': {e}")

            data_to_populate[output_key] = value_to_assign

        return data_to_populate

    def get_product_data(self, product_info: tuple) -> dict:
        """
        Fetches product JSON, then parses it to populate product details.
        :param product_info: A tuple (slug, details_dict), e.g., ('udr', {'url': '...'}).
        :return: The details_dict populated with parsed data.
        """
        if not isinstance(product_info, tuple) or len(product_info) != 2:
            print("Error: Invalid product_info format. Expected a tuple of (slug, dict).")
            return {} # Or raise an error

        slug, product_details_dict = product_info # product_details_dict is like {'url': '...'}

        if not isinstance(product_details_dict, dict) or 'url' not in product_details_dict:
            print(f"Error: Invalid product_details_dict for slug '{slug}'. 'url' key missing or not a dict.")
            return product_details_dict # Return as is, or an empty dict

        product_url = product_details_dict['url']
        print(f"\nFetching product data for slug '{slug}' from URL: {product_url}")

        product_json_data = self.fetch_single_json(product_url)

        if product_json_data:
            print(f"Successfully retrieved JSON for product: {slug}. Now parsing...")
            # Pass product_details_dict to be populated
            populated_details = self.parse_product_data(product_details_dict, product_json_data)
            return populated_details
        else:
            print(f"Failed to retrieve or parse JSON data for product: {slug}")
            # Return the original dict (with just URL) if fetching/parsing failed,
            # so it still has the URL and other pre-existing keys.
            return product_details_dict

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
