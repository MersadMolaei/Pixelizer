import requests
import argparse
import os
import urllib.parse # Import urllib.parse to handle URL parsing

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

def download_image(image_url: str, output_path: str) -> bool:
    """
    Downloads an image from a given URL and saves it to a local file.

    Args:
        image_url: The URL of the image to download.
        output_path: The path where the image should be saved.

    Returns:
        True if the download was successful, False otherwise.
    """
    print(f"Attempting to download image from: {image_url}")
    try:
        # Use stream=True to download the image content in chunks
        response = requests.get(image_url, stream=True)
        response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)

        # Get the directory name from the output path
        output_dir = os.path.dirname(output_path)
        # Create the directory if it doesn't exist
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Created directory: {output_dir}")


        # Write the image content to the file in binary write mode
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)

        print(f"Successfully downloaded image to: {output_path}")
        return True

    except requests.exceptions.RequestException as e:
        print(f"Error downloading image from '{image_url}': {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occurred during download: {e}")
        return False

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

    # Add optional output file argument
    parser.add_argument(
        "--output",
        help="Path and filename to save the pixelized image. Defaults to 'pixelized_image.jpg' in the current directory."
    )


    # Parse the arguments from the command line
    args = parser.parse_args()

    api_key = args.api_key
    image_url = args.url
    file_path = args.file
    output_path = args.output

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

    # Process the result if the API call was successful
    if pixelized_image_url:
        print("\nSuccessfully pixelized image!")
        print(f"Resulting pixelized image URL: {pixelized_image_url}")

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

            print(f"No output path specified. Using default: {output_path}")


        # Download the image
        if download_image(pixelized_image_url, output_path):
            print("Image processing and download complete.")
        else:
            print("Image processing complete, but download failed.")
            exit(1) # Exit with an error code for download failure

    else:
        print("\nFailed to pixelize image.")
        exit(1) # Exit with an error code for API failure
