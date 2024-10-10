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
    # url = f"https://m9kpme5jn02zeb-8000.proxy.runpod.net/run"
    
    json = payload.generate_payload(image_url, image_description, color, background_color, agression, strength)
    
    print(json)
    
    return requests.post(url, json=json, headers=headers)

def get_result(request_id):
    url = f"https://api.runpod.ai/v2/{endpoint_id}/status/{request_id}"
    # url = f"https://m9kpme5jn02zeb-8000.proxy.runpod.net/status/{request_id}"

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
                "status": "InQueue",
            }
        elif status == "IN_PROGRESS":
            return {
                "status": "InProgress",
            }
        
        elif status == "FAILED":
            return {
                "status": "Failed",
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
