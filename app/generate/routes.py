from app.generate import generate, comfyui, s3
from flask import request, jsonify
import os
from openai import OpenAI
from werkzeug.utils import secure_filename
from flasgger import swag_from
from urllib.parse import urlparse

from app.generate import generate, comfyui, s3
from flask import request, jsonify
import os
from openai import OpenAI
from werkzeug.utils import secure_filename
from flasgger import swag_from

api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

# Endpoint 1: Upload an image to S3 and get the URL
@generate.route('/upload', methods=['POST'])
@swag_from({
    'tags': ['Upload'],
    'summary': 'Upload an image and get the URL',
    'parameters': [
        {
            'name': 'file',
            'in': 'formData',
            'type': 'file',
            'required': True,
            'description': 'The image file to upload'
        }
    ],
    'responses': {
        '200': {
            'description': 'Returns the URL of the uploaded image',
            'examples': {
                'application/json': {
                    'url': 'https://s3-bucket-url.com/image.jpg'
                }
            }
        },
        '400': {
            'description': 'Invalid input or file upload error'
        },
        '500': {
            'description': 'Internal server error'
        }
    }
})
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join('/tmp', filename)
        file.save(file_path)

        try:
            with open(file_path, 'rb') as image_file:
                _, file_extension = os.path.splitext(file_path)
                url = s3.upload(image_file, file_extension)  # Upload to S3 and get the URL

                return jsonify({
                    "url": url.split('/')[-1]
                }), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            os.remove(file_path)

    return jsonify({'error': 'File upload failed'}), 500

# Endpoint 2: Generate image from uploaded URL
@generate.route('/generate', methods=['POST'])
@swag_from({
    'tags': ['Generation'],
    'summary': 'Generate an image based on the uploaded image URL',
    'parameters': [
        {
            'name': 'url',
            'in': 'body',  # 'json' changed to 'body' to match request payload
            'required': True,
            'schema': {
                'type': 'object',
                'properties': {
                    'url': {
                        'type': 'string',
                        'description': 'The URL of the uploaded image'
                    }
                }
            },
            'description': 'The JSON body containing the URL of the uploaded image'
        },
        {
            'name': 'color',
            'in': 'query',  # Remains in query as it is optional
            'type': 'string',
            'required': True,
            'description': 'The desired color for the transformation'
        },
        {
            'name': 'background_color',
            'in': 'query',  # Remains in query as it is optional
            'type': 'string',
            'required': False,
            'description': 'The background color as a hex string, defaults to None'
        },
        {
            'name': 'agression',
            'in': 'query',  # Remains in query as it is optional
            'type': 'string',
            'required': False,
            'description': 'The background color as a hex string, defaults to None'
        },
        {
            'name': 'strength',
            'in': 'query',  # Remains in query as it is optional
            'type': 'string',
            'required': False,
            'description': 'The background color as a hex string, defaults to None'
        }
    ],
    'consumes': [
        'application/json'
    ],
    'responses': {
        '200': {
            'description': 'Generates an image based on the provided URL and other parameters',
            'examples': {
                'application/json': {
                    'id': 'generated-task-id',
                    'original_image': 'https://s3-bucket-url.com/image.jpg',
                    'description': 'Image transformation details',
                }
            }
        },
        '400': {
            'description': 'Invalid input or URL'
        },
        '500': {
            'description': 'Internal server error'
        }
    }
})
def generate_image():
    data = request.json  # get JSON data from the POST request body
    color = data.get('color')
    background_color = data.get('backgroundColor', None)  # Get the background color
    strength = data.get('strength')
    agression = data.get('agression')
    url = data.get('url')

    if not url:
        return jsonify({'error': 'No image URL provided'}), 400

    try:
        # Generate the description of the image using OpenAI
        description_response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system", "content": "Do not try to find out who the person is, just provide a description of a person using the following format: \n [hair color], [hairstyle], [facial hair], [hair type] \n Where: \n Hair Color options: brown hair, blonde hair, black hair, old hair, white hair, blue hair, etc. \n Hairstyle options: bald, very short hair, short hair, medium hair, long hair \n Facial Hair options: clean shaven, stubble, goatee, beard, moustache, large beard \n Hair Type options: curly hair, wavy hair, normal hair \n Example format: brown hair, short hair, average body, beard, curly hair \n Don't output anything else other than the description in the correct format."
                },
                {
                    "role": "user", 
                    "content": f"[Image URL: {url}]"
                }
            ]
        )
        description = description_response.choices[0].message.content.strip()

        # Use ComfyUI to generate the image based on the description and URL
        response = comfyui.generate_image(url, description, color, background_color, agression, strength)

        return jsonify({
            "id": response.json()["id"],
            "original_image": url,
            "description": description,
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@generate.route('/status', methods=['GET'])
@swag_from({
    'tags': ['Generation'],
    'summary': 'Check the status of a generation task',
    'parameters': [
        {
            'name': 'id',
            'in': 'query',
            'type': 'string',
            'required': True,
            'description': 'The unique identifier for the generation task'
        }
    ],
    'responses': {
        '200': {
            'description': 'Returns the status of the generation task along with the URL to the image if available',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {
                        'type': 'string',
                        'description': 'The unique identifier for the generation task'
                    },
                    'url': {
                        'type': 'string',
                        'description': 'URL to the generated image if available, otherwise empty'
                    },
                    'status': {
                        'type': 'string',
                        'description': 'Status of the generation task',
                        'enum': ['InProgress', 'Completed', 'Failed']
                    }
                },
                'examples': {
                    'application/json': {
                        'id': 'f455d0ae-0bf0-4830-8fd7-1cb2c12b7089',
                        'url': 'https://r2r-comfyui.s3.amazonaws.com/your-image',
                        'status': 'Completed'
                    }
                }
            }
        },
        '400': {
            'description': 'Invalid request parameters'
        },
        '404': {
            'description': 'Prompt ID not found or no image available'
        },
        '500': {
            'description': 'Internal server error'
        }
    }
})
def get_generation_status():
    request_id = request.args.get('id')

    if not request_id:
        return jsonify({
            "error": "Missing 'id' parameter"
        }), 400  # Bad request if the ID is not provided

    try:
        # Get the result from comfyui.get_result
        result = comfyui.get_result(request_id)

        # Return the appropriate response based on the result
        if result["status"] == "Completed":
            parsed_url = urlparse(result["url"])
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
            
            return jsonify({
                "id": request_id,
                "url": base_url,
                "status": "Completed"
            }), 200
        elif result["status"] == "InProgress":
            parsed_url = urlparse(result["url"])
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
            
            return jsonify({
                "id": request_id,
                "url": base_url,  # Still None at this stage
                "status": "InProgress"
            }), 200
        elif result["status"] == "Failed":
            parsed_url = urlparse(result["url"])
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

            return jsonify({
                "id": request_id,
                "url": base_url,
                "status": "Failed"
            }), 200
        else:
            parsed_url = urlparse(result["url"])
            base_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

            return jsonify({
                "id": request_id,
                "status": result["status"],  # Handle unknown or error statuses
                "error": result.get("error", "Unknown error occurred")
            }), 500  # Internal server error for unknown or unhandled statuses

    except Exception as e:
        return jsonify({
            "id": request_id,
            "status": "Error",
            "error": str(e)
        }), 500  # Return an internal server error if something goes wrong
