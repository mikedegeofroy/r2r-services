from flask import current_app as app, request, jsonify
import os
import openai
from werkzeug.utils import secure_filename

# Set your OpenAI API key here
openai.api_key = 'your_openai_api_key'

# Define a list of tags you want to use
PREDEFINED_TAGS = ['tag1', 'tag2', 'tag3', 'tag4']

@app.route('/upload', methods=['POST'])
def upload_file():
    """
    Endpoint to upload an audio file and get the transcription, translation, and tags.
    ---
    parameters:
      - name: file
        in: formData
        type: file
        required: true
        description: The audio file to be uploaded
    responses:
      200:
        description: Transcription, translation, and tags of the uploaded audio file
        examples:
          application/json: 
            transcription: "Transcribed text"
            translation: "Translated text"
            tags: ["tag1", "tag2"]
      400:
        description: Invalid input or file upload error
      500:
        description: Internal server error
    """
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
            # Transcribe the audio file using OpenAI's new transcription API
            with open(file_path, 'rb') as audio_file:
                response = openai.Audio.create(
                    file=audio_file,
                    model="whisper-1"
                )
                transcription = response['text']

            # Translate the transcription using OpenAI's GPT-4
            translation_prompt = f"Translate the following text to English:\n\n{transcription}"
            translation_response = openai.Completion.create(
                model="text-davinci-003",
                prompt=translation_prompt,
                max_tokens=1000
            )
            translation = translation_response.choices[0].text.strip()

            # Generate tags for the translated text using OpenAI's GPT-4
            # tags_prompt = f"Generate tags for the following text from a predefined list of tags:\n\n{translation}\n\nTags: {', '.join(PREDEFINED_TAGS)}"
            # tags_response = openai.Completion.create(
            #     model="text-davinci-003",
            #     prompt=tags_prompt,
            #     max_tokens=100
            # )
            # tags = [tag.strip() for tag in tags_response.choices[0].text.strip().split(',')]

            return jsonify({
                'transcription': transcription,
                'translation': translation,
                # 'tags': tags
            })
        
        except Exception as e:
            return jsonify({'error': str(e)}), 500
        finally:
            os.remove(file_path)

    return jsonify({'error': 'File upload failed'}), 500
