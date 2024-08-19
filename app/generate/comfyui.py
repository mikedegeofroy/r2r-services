from app.generate import payload
import requests
from app.generate import s3 
import os

# TODO
# When getting status, parse errors & pending

comfyui_url = os.getenv('COMFYUI_URL')
url = '{}/prompt'.format(comfyui_url)

def generate_image(image_url, image_description, color):
  return requests.post(url, json=payload.generate_payload(image_url, image_description, color))

def get_image(filename, subfolder, folder_type):
    params = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    response = requests.get(f"{comfyui_url}/view", params=params)

    return response.content

def get_result(prompt_id):
    url = f"{comfyui_url}/history/{prompt_id}"
    
    try:
        # Send a request to fetch the status
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors

        data = response.json()[prompt_id]
        
        # Check if the prompt is completed successfully
        if data['status']['status_str'] == 'success' and data['status']['completed']:
            # Check if there are output images
            if '1254' in data['outputs']:
                # Extract output image details
                image_details = data['outputs']['1254']['images'][0]
                filename = image_details['filename']
                subfolder = image_details['subfolder']  # Assuming subfolder is available
                folder_type = image_details['type']  # Assuming folder_type is available

                # Get image data
                image_data = get_image(filename, subfolder, folder_type)
                
                # Determine file extension (assuming it's part of filename)
                file_extension = '.' + filename.split('.')[-1]

                # Upload to S3 and get the URL
                image_url = s3.upload(image_data, file_extension)
                return image_url

            else:
                return "No output image available."
        else:
            return "Image processing is not complete or failed."
    
    except requests.RequestException as e:
        return f"An error occurred: {e}"
