import requests
import argparse
import os
import urllib.parse
import sys
from colorama import init, Fore, Style

# --- Initialize Colorama ---
# init(autoreset=True) will automatically reset the color after each print statement
init(autoreset=True)

# --- Configuration ---
# Base URL for the API
API_BASE_URL = "https://api.apilayer.com/face_pixelizer"

# --- API Endpoints ---
URL_ENDPOINT = f"{API_BASE_URL}/url"
UPLOAD_ENDPOINT = f"{API_BASE_URL}/upload"

# Default file name for storing the API key
API_KEY_FILE = "api_key.txt"

# --- Functions to interact with the API ---

def pixelize_image_from_url(api_key: str, image_url: str) -> str | None:
    """
    Calls the API to pixelize faces in an image from a web URL.

    Args:
        api_key: Your API key for authentication.
        image_url: The URL of the image to process.

    Returns:
        The URL of the pixelized image if successful, None otherwise.
    """
    headers = {
        "apikey": api_key
    }
    # The URL endpoint expects the image URL as a query parameter
    params = {
        "url": image_url
    }

    print(f"{Fore.CYAN}Sending request to pixelize image from URL: {image_url}{Style.RESET_ALL}")

    try:
        response = requests.get(URL_ENDPOINT, headers=headers, params=params)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

        result = response.json()
        if "result" in result:
            return result["result"]
        else:
            print(f"{Fore.YELLOW}API response did not contain a 'result' field: {result}{Style.RESET_ALL}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}Error calling API for URL '{image_url}': {e}{Style.RESET_ALL}")
        # Attempt to print API error message if available
        try:
            error_response = e.response.json()
            if "message" in error_response:
                 print(f"{Fore.RED}API Error Message: {error_response['message']}{Style.RESET_ALL}")
        except:
            pass # Ignore if response is not JSON or message is not present
        return None

def pixelize_uploaded_image(api_key: str, file_path: str) -> str | None:
    """
    Calls the API to pixelize faces in an uploaded image file.

    Args:
        api_key: Your API key for authentication.
        file_path: The path to the local image file.

    Returns:
        The URL of the pixelized image if successful, None otherwise.
    """
    headers = {
        "apikey": api_key
    }

    print(f"{Fore.CYAN}Sending request to pixelize uploaded image file: {file_path}{Style.RESET_ALL}")

    try:
        # Open the file in binary read mode
        with open(file_path, 'rb') as f:
            # The upload endpoint expects the file content in the request body
            response = requests.post(UPLOAD_ENDPOINT, headers=headers, data=f)

        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

        result = response.json()
        if "result" in result:
            return result["result"]
        else:
            print(f"{Fore.YELLOW}API response did not contain a 'result' field: {result}{Style.RESET_ALL}")
            return None

    except FileNotFoundError:
        print(f"{Fore.RED}Error: File not found at path '{file_path}'{Style.RESET_ALL}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}Error calling API for file upload '{file_path}': {e}{Style.RESET_ALL}")
        # Attempt to print API error message if available
        try:
            error_response = e.response.json()
            if "message" in error_response:
                 print(f"{Fore.RED}API Error Message: {error_response['message']}{Style.RESET_ALL}")
        except:
            pass # Ignore if response is not JSON or message is not present
        return None
    except Exception as e:
        print(f"{Fore.RED}An unexpected error occurred while processing file '{file_path}': {e}{Style.RESET_ALL}")
        return None

def download_image(image_url: str, output_path: str) -> bool:
    """
    Downloads an image from a given URL and saves it to a local file.

    Args:
        image_url: The URL of the image to download.
        output_path: The path where the image should be saved.

    Returns:
        True if the download was successful, False otherwise.
    """
    print(f"{Fore.CYAN}Attempting to download image from: {image_url}{Style.RESET_ALL}")
    try:
        # Use stream=True to download the image content in chunks
        response = requests.get(image_url, stream=True)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

        # Get the directory name from the output path
        output_dir = os.path.dirname(output_path)
        # Create the directory if it doesn't exist
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"{Fore.CYAN}Created directory: {output_dir}{Style.RESET_ALL}")


        # Write the image content to the file in binary write mode
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"{Fore.GREEN}Successfully downloaded image to: {output_path}{Style.RESET_ALL}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"{Fore.RED}Error downloading image from '{image_url}': {e}{Style.RESET_ALL}")
        return False
    except Exception as e:
        print(f"{Fore.RED}An unexpected error occurred during download: {e}{Style.RESET_ALL}")
        return False

def get_api_key_from_file(file_name: str) -> str | None:
    """
    Reads the API key from the first line of a specified file.

    Args:
        file_name: The name of the file to read the API key from.

    Returns:
        The API key string if found, None otherwise.
    """
    try:
        # Get the directory of the currently executing script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        file_path = os.path.join(script_dir, file_name)

        with open(file_path, 'r') as f:
            api_key = f.readline().strip() # Read the first line and remove leading/trailing whitespace
            if api_key:
                print(f"{Fore.CYAN}API key read from '{file_name}'.{Style.RESET_ALL}")
                return api_key
            else:
                print(f"{Fore.YELLOW}Warning: '{file_name}' is empty. API key not found in file.{Style.RESET_ALL}")
                return None
    except FileNotFoundError:
        print(f"{Fore.YELLOW}Warning: API key file '{file_name}' not found in the script directory. Please provide the API key via --api-key or create this file.{Style.RESET_ALL}")
        return None
    except Exception as e:
        print(f"{Fore.RED}Error reading API key from file '{file_name}': {e}{Style.RESET_ALL}")
        return None


# --- Main application logic ---

if __name__ == "__main__":
    # Set up command-line argument parsing
    # Keep the description simple text for argparse help formatting
    parser = argparse.ArgumentParser(
        description="Pixelize faces in an image using the Face Pixelizer API."
    )

    # Add optional API key argument (no longer required by argparse)
    parser.add_argument(
        "--api-key",
        help=f"{Fore.YELLOW}Your API key for the Face Pixelizer API. If not provided, the script will look for it in '{API_KEY_FILE}'.{Style.RESET_ALL}"
    )

    # Add mutually exclusive group for URL or file path
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--url",
        help=f"{Fore.YELLOW}URL of the image to pixelize. (Required if --file is not used){Style.RESET_ALL}"
    )
    group.add_argument(
        "--file",
        help=f"{Fore.YELLOW}Path to the local image file to pixelize. (Required if --url is not used){Style.RESET_ALL}"
    )

    # Add optional output file argument
    parser.add_argument(
        "--output",
        help=f"{Fore.YELLOW}Path and filename to save the pixelized image. Defaults to 'pixelized_image.jpg' in the current directory.{Style.RESET_ALL}"
    )


    # Parse the arguments from the command line
    args = parser.parse_args()

    api_key = args.api_key
    image_url = args.url
    file_path = args.file
    output_path = args.output

    # If API key was not provided as a command-line argument, try to get it from the file
    if not api_key:
        api_key = get_api_key_from_file(API_KEY_FILE)

    # Check if we have an API key before proceeding
    if not api_key:
        print(f"{Fore.RED}Error: No API key provided via command-line or found in '{API_KEY_FILE}'. Please provide your API key to use the application.{Style.RESET_ALL}")
        exit(1) # Exit if no API key is available

    # Print the developer info after argument parsing but before main logic
    print(f"{Fore.CYAN}Provided By Mersad Molaei{Style.RESET_ALL}")
    print(f"Website: {Fore.GREEN}https://Mersadev.ir{Style.RESET_ALL}")
    print(f"Github: {Fore.BLUE}https://Github.com/MersadMolaei{Style.RESET_ALL}")
    print("-" * 30) # Separator line


    pixelized_image_url = None

    # Determine whether to use URL or file upload endpoint
    if image_url:
        pixelized_image_url = pixelize_image_from_url(api_key, image_url)
    elif file_path:
        # Check if the local file exists before attempting upload
        if os.path.exists(file_path):
            pixelized_image_url = pixelize_uploaded_image(api_key, file_path)
        else:
            print(f"{Fore.RED}Error: The specified file path does not exist: {file_path}{Style.RESET_ALL}")
            exit(1) # Exit with an error code

    # Process the result if the API call was successful
    if pixelized_image_url:
        print(f"\n{Fore.GREEN}Successfully pixelized image!{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Resulting pixelized image URL: {pixelized_image_url}{Style.RESET_ALL}")

        # Determine the output path if not provided
        if not output_path:
            # Try to infer filename from URL, otherwise use a default
            try:
                parsed_url = urllib.parse.urlparse(pixelized_image_url)
                filename = os.path.basename(parsed_url.path)
                if not filename or "." not in filename: # Basic check for a valid filename
                     filename = "pixelized_image.jpg"
                output_path = filename
            except:
                 output_path = "pixelized_image.jpg" # Fallback to default

            print(f"{Fore.YELLOW}No output path specified. Using default: {output_path}{Style.RESET_ALL}")


        # Download the image
        if download_image(pixelized_image_url, output_path):
            print(f"{Fore.GREEN}Image processing and download complete.{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}Image processing complete, but download failed.{Style.RESET_ALL}")
            exit(1) # Exit with an error code for download failure

    else:
        print(f"{Fore.RED}Failed to pixelize image.{Style.RESET_ALL}")
        exit(1) # Exit with an error code for API failure
