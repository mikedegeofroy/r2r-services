from app.generate import payload
import requests
import os

api_key = os.getenv('ENDPOINT_API_KEY')
endpoint_id = os.getenv('ENDPOINT_ID')

headers = {
    "authorization": f"Bearer {api_key}"
}


def generate_image(image_url,
                   image_description,
                   color,
                   background_color,
                   agression,
                   strength,
                   upscale,
                   is_male):
    url = f"https://api.runpod.ai/v2/{endpoint_id}/run"

    json = payload.generate_payload(
        image_url,
        image_description,
        color,
        background_color,
        agression,
        strength,
        upscale,
        is_male)

    return requests.post(url, json=json, headers=headers)


def get_result(request_id):
    url = f"https://api.runpod.ai/v2/{endpoint_id}/status/{request_id}"

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()

        data = response.json()

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
                return {
                    "status": "Completed",
                    "url": output.get("message")
                }
            else:
                return {
                    "status": "Failed",
                    "url": None
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
            "error": str(e)
        }
