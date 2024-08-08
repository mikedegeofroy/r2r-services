from app.generate import generate, comfyui, s3
from flask import request, jsonify
import os
from openai import OpenAI
from werkzeug.utils import secure_filename
from flasgger import swag_from

# TODO
# fix the returns in /status, make sure to handle errors

api_key = os.getenv('OPENAI_API_KEY')
client = OpenAI(api_key=api_key)

@generate.route('/upload', methods=['POST'])
@swag_from({
    'tags': ['Generation'],
    'summary': 'Upload an image for transformation',
    'parameters': [
        {
            'name': 'file',
            'in': 'formData',
            'type': 'file',
            'required': True,
            'description': 'The image file to be transformed'
        }
    ],
    'responses': {
        '200': {
            'description': 'Generates a avatar for the image of the user',
            'examples': {
                'application/json': {
                    'src': 'url to the image',
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
def generator_upload_file():
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
                url = s3.upload(image_file, file_extension)

                description_response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system", "content": "Do not try to find out who the person is, just provide a description of a person using the following format: \n [hair color], [hairstyle], [body type], [facial hair], [hair type] \n Where: \n Hair Color options: brown hair, blonde hair, black hair, old hair, white hair, blue hair, etc. \n Hairstyle options: bald, very short hair, short hair, medium hair, long hair \n Body Type options: skinny body, average body, athletic body, fat body \n Facial Hair options: clean shaven, stubble, goatee, beard, moustache, large beard \n Hair Type options: curly hair, wavy hair, normal hair \n Example format: brown hair, short hair, average body, beard, curly hair \n Don't output anything else other than the description in the correct format."
                        },
                        {
                            "role": "user", 
                            "content": [ 
                              {
                                "type": "image_url",
                                "image_url": {
                                  "url": url
                                }
                              }
                            ]
                        }
                    ]
                )
                description = description_response.choices[0].message.content.strip()

                response = comfyui.generate_image(url, description)

                return jsonify({
                    "prompt_id": response.json()['prompt_id'],
                    "original_image": url,
                    "descripion": description,
                })
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            os.remove(file_path)

    return jsonify({'error': 'File upload failed'}), 500

@generate.route('/status', methods=['GET'])
@swag_from({
    'tags': ['Generation'],
    'summary': 'Check the status of a generation task',
    'parameters': [
        {
            'name': 'prompt_id',
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
                    'prompt_id': {
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
                        'prompt_id': 'f455d0ae-0bf0-4830-8fd7-1cb2c12b7089',
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
    prompt_id = request.args.get('prompt_id')

    try:
        url = comfyui.get_result(prompt_id)

        return jsonify({
            "prompt_id": prompt_id,
            "url": url,
            "status": "Done"
        })
    except:
        return jsonify({
            "prompt_id": prompt_id,
            "status": "InProgress"
        })
