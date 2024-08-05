from flask import request, jsonify, Blueprint
import os
from openai import OpenAI
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from flasgger import swag_from
import base64
from app.generate import generate

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=api_key)
PREDEFINED_TAGS = ['feat', 'bug']

@generate.route('/upload', methods=['POST'])
@swag_from({
    'tags': ['Avatar'],
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
                b64image = base64.b64encode(image_file.read()).decode('utf-8');
                description_response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "system", "content": "Please provide a description of a person using the following format: \n [hair color], [hairstyle], [body type], [facial hair], [hair type] \n Where: \n Hair Color options: brown hair, blonde hair, black hair, old hair, white hair, blue hair, etc. \n Hairstyle options: bald, very short hair, short hair, medium hair, long hair \n Body Type options: skinny body, average body, athletic body, fat body \n Facial Hair options: clean shaven, stubble, goatee, beard, moustache, large beard \n Hair Type options: curly hair, wavy hair, normal hair \n Example format: brown hair, short hair, average body, beard, curly hair"
                        },
                        {
                            "role": "user", 
                            "content": [ 
                              {
                                "type": "image_url",
                                "image_url": {
                                  "url": f"data:image/jpeg;base64,{b64image}"
                                }
                              }
                            ]
                        }
                    ]
                )
                description = description_response.choices[0].message.content.strip()

            return jsonify({
                'src': description,
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            os.remove(file_path)

    return jsonify({'error': 'File upload failed'}), 500
