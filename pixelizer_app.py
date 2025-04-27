import requests
import argparse
import os

# --- Configuration ---
# Base URL for the API
API_BASE_URL = "https://api.apilayer.com/face_pixelizer"

# --- API Endpoints ---
URL_ENDPOINT = f"{API_BASE_URL}/url"
UPLOAD_ENDPOINT = f"{API_BASE_URL}/upload"

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

    print(f"Sending request to pixelize image from URL: {image_url}")

    try:
        response = requests.get(URL_ENDPOINT, headers=headers, params=params)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

        result = response.json()
        if "result" in result:
            return result["result"]
        else:
            print(f"API response did not contain a 'result' field: {result}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Error calling API for URL '{image_url}': {e}")
        # Attempt to print API error message if available
        try:
            error_response = e.response.json()
            if "message" in error_response:
                 print(f"API Error Message: {error_response['message']}")
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

    print(f"Sending request to pixelize uploaded image file: {file_path}")

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
            print(f"API response did not contain a 'result' field: {result}")
            return None

    except FileNotFoundError:
        print(f"Error: File not found at path '{file_path}'")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error calling API for file upload '{file_path}': {e}")
        # Attempt to print API error message if available
        try:
            error_response = e.response.json()
            if "message" in error_response:
                 print(f"API Error Message: {error_response['message']}")
        except:
            pass # Ignore if response is not JSON or message is not present
        return None
    except Exception as e:
        print(f"An unexpected error occurred while processing file '{file_path}': {e}")
        return None


# --- Main application logic ---

if __name__ == "__main__":
    # Set up command-line argument parsing
    parser = argparse.ArgumentParser(
        description="Pixelize faces in an image using the Face Pixelizer API."
    )

    # Add required API key argument
    parser.add_argument(
        "--api-key",
        required=True,
        help="Your API key for the Face Pixelizer API."
    )

    # Add mutually exclusive group for URL or file path
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--url",
        help="URL of the image to pixelize."
    )
    group.add_argument(
        "--file",
        help="Path to the local image file to pixelize."
    )

    # Parse the arguments from the command line
    args = parser.parse_args()

    api_key = args.api_key
    image_url = args.url
    file_path = args.file

    pixelized_image_url = None

    # Determine whether to use URL or file upload endpoint
    if image_url:
        pixelized_image_url = pixelize_image_from_url(api_key, image_url)
    elif file_path:
        # Check if the local file exists before attempting upload
        if os.path.exists(file_path):
            pixelized_image_url = pixelize_uploaded_image(api_key, file_path)
        else:
            print(f"Error: The specified file path does not exist: {file_path}")
            exit(1) # Exit with an error code

    # Print the result
    if pixelized_image_url:
        print("\nSuccessfully pixelized image!")
        print(f"Resulting pixelized image URL: {pixelized_image_url}")
    else:
        print("\nFailed to pixelize image.")
        exit(1) # Exit with an error code
