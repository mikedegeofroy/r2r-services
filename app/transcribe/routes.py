from app.transcribe import transcribe
from flask import request, jsonify, Blueprint
import os
from openai import OpenAI
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from flasgger import swag_from

load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')

client = OpenAI(api_key=api_key)
PREDEFINED_TAGS = ['feat', 'bug']

@transcribe.route('/upload', methods=['POST'])
@swag_from({
    'tags': ['Transcribe'],
    'summary': 'Upload an audio file for transcription',
    'parameters': [
        {
            'name': 'file',
            'in': 'formData',
            'type': 'file',
            'required': True,
            'description': 'The audio file to be uploaded'
        }
    ],
    'responses': {
        '200': {
            'description': 'Transcription, translation, and tags of the uploaded audio file',
            'examples': {
                'application/json': {
                    'transcription': "Transcribed text",
                    'translation': "Translated text",
                    'tags': ["tag1", "tag2"]
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
def transcribe_upload_file():
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
            with open(file_path, 'rb') as audio_file:
                response = client.audio.transcriptions.create(file=audio_file, model="whisper-1")
                transcription = response.text

            translation_prompt = f"Translate the following text to Russian:\n\n{transcription}"
            translation_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a translator. You're translating feedback from a game based in the 90s."},
                    {"role": "user", "content": translation_prompt}
                ]
            )
            translation = translation_response.choices[0].message.content.strip()

            tags_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": f"Generate tags for the following text from a predefined list of tags:\n\n\n\nTags: {', '.join(PREDEFINED_TAGS)}. Do not output anything else than a comma separated list of tags."},
                    {"role": "user", "content": translation}
                ]
            )
            tags = [tag.strip() for tag in tags_response.choices[0].message.content.strip().split(',')]

            return jsonify({
                'transcription': transcription,
                'translation': translation,
                'tags': tags
            })

        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            os.remove(file_path)

    return jsonify({'error': 'File upload failed'}), 500
