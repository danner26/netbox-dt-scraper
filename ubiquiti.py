from manufacturers.ubiquiti import MANUFACTURER, DEVICE_INFO_URLS # Assuming you've moved to config.py as per previous advice
import requests
import json

product_urls = []

def fetch_and_parse_json(url):
    """
    Fetches JSON data from a list of URLs and parses it.
    Returns a list of parsed JSON objects.
    """
    parsed_data_list = []

    print(f"\nFetching data from: {url}")
    try:
        response = requests.get(url, timeout=10) # Added timeout
        response.raise_for_status()  # Raises an HTTPError for bad responses (4XX or 5XX)

        # Attempt to parse JSON
        try:
            parsed_data_list = response.json()
            print(f"Successfully fetched and parsed JSON from {url}")
            # You can now work with the 'data' object
            # For example, print a part of it:
            # if isinstance(data, dict) and data.get('pageProps', {}).get('data'):
            # print(f"  Sample data (pageProps.data): {json.dumps(data['pageProps']['data'][:2], indent=2)}") # Print first 2 items if it's a list
            # else:
            # print(f"  Parsed data: {json.dumps(data, indent=2)}") # Or print the whole thing
        except json.JSONDecodeError:
            print(f"Error: Could not decode JSON from {url}. Content might not be valid JSON.")
            print(f"Response text: {response.text[:200]}...") # Print first 200 chars of response

    except requests.exceptions.HTTPError as http_err:
        print(f"HTTP error occurred while fetching {url}: {http_err}")
    except requests.exceptions.ConnectionError as conn_err:
        print(f"Connection error occurred while fetching {url}: {conn_err}")
    except requests.exceptions.Timeout as timeout_err:
        print(f"Timeout error occurred while fetching {url}: {timeout_err}")
    except requests.exceptions.RequestException as req_err:
        print(f"An error occurred while fetching {url}: {req_err}")
    return parsed_data_list

def extract_product_slugs(top_level_categories: dict) -> list:
    product_slugs = []

    if top_level_categories and 'pageProps' in top_level_categories and 'subCategoriesWithProducts' in top_level_categories['pageProps']:
        subcategories = top_level_categories['pageProps']['subCategoriesWithProducts']

        for subcategory in subcategories:
            if 'products' in subcategory and isinstance(subcategory['products'], list):
                for product in subcategory['products']:
                    if 'slug' in product:
                        product_slugs.append(product['slug'])
                    else:
                        print(f"Warning: Product found without a 'slug': {product.get('name', 'N/A')}")
            else:
                print(f"Warning: Subcategory '{subcategory.get('id', 'N/A')}' has no 'products' list or it's not a list.")
    else:
        print("Error: Could not find 'pageProps' or 'subCategoriesWithProducts' in the JSON data.")

    # Print the extracted slugs
    if product_slugs:
        print("\nProduct Slugs Extracted.")
        return product_slugs
    else:
        print("\nNo product slugs were extracted.")

if __name__ == "__main__":
    if DEVICE_INFO_URLS:
        for url in DEVICE_INFO_URLS:
            print(f"Processing URL: {url}")
            category_json_data = fetch_and_parse_json(url)

            if category_json_data:
                product_list = extract_product_slugs(category_json_data)
                print(f"\n--- Successfully fetched data for {product_list} URL(s) ---")

                for product in product_list:
                    product_urls.append(url[:-5] + '/' + product + '.json')
            else:
                print("\nNo data was successfully fetched and parsed.")
    else:
        print("No DEVICE_INFO_URLS found to process.")

    return product_urls
