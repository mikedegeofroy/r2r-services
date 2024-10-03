from app.generate import payload
import requests
from app.generate import s3 
import os

# Retrieve the API key from the environment variable
api_key = os.getenv('ENDPOINT_API_KEY')
endpoint_id = os.getenv('ENDPOINT_ID')

headers = {
    "authorization": f"Bearer {api_key}"
}

def generate_image(image_url, image_description, color, background_color, agression, strength):
    url = f"https://api.runpod.ai/v2/{endpoint_id}/run"
    
    return requests.post(url, json=payload.generate_payload(image_url, image_description, color, background_color, agression, strength), headers=headers)

def get_result(request_id):
    url = f"https://api.runpod.ai/v2/{endpoint_id}/status/{request_id}"

    try:
        # Send a GET request to check the status of the image generation
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an exception for HTTP errors

        # Parse the JSON response
        data = response.json()

        # Handle the different statuses
        status = data.get("status")
        
        if status == "IN_QUEUE":
            return {
                "status": "InProgress",
                "url": None  # No URL since it's still processing
            }
        
        elif status == "FAILED":
            return {
                "status": "Failed",
                "url": None  # No URL since the task failed
            }

        elif status == "COMPLETED":
            output = data.get("output", {})
            if output.get("status") == "success":
                # Return the success status and the image URL
                return {
                    "status": "Completed",
                    "url": output.get("message")  # URL of the image
                }
            else:
                return {
                    "status": "Failed",
                    "url": None  # No URL in case of completion with errors
                }

        else:
            return {
                "status": "Unknown",
                "url": None
            }

    except requests.RequestException as e:
        return {
            "status": "Error",
            "url": None,
            "error": str(e)  # Capture the error for debugging/logging
        }
