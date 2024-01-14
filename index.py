from flask import Flask, request, render_template, Response
from tts_voice import tts_order_voice
import edge_tts
import anyio
import os
import uuid
import logging

app = Flask(__name__)
language_dict = tts_order_voice

async def text_to_speech_edge(text, language_code):
    try:
        voice = language_dict[language_code]
        communicate = edge_tts.Communicate(text, voice)
        tmp_path = os.path.join('/tmp', str(uuid.uuid4()) + '.mp3')
        await communicate.save(tmp_path)
        return '语音合成完成：{}'.format(text), tmp_path
    except Exception as e:
        logging.error(f'Error occurred in text_to_speech_edge: {e}')
        raise

@app.route('/', methods=['GET', 'POST'])
@app.route('/text_to_speech', methods=['GET', 'POST'])
def text_to_speech():
    if request.method == 'POST':
        data = request.form
        text = data['text']
        language_code = data['language_code']
        try:
            result_text, result_path = anyio.run(text_to_speech_edge, text, language_code)
        except Exception as e:
            logging.error(f'Error occurred in route text_to_speech: {e}')
            raise

        with open(result_path, 'rb') as audio: 
            audio_file = audio.read() 

        # Remove the file after reading
        os.remove(result_path)
        
        return Response(audio_file, mimetype="audio/mpeg")
    else:
        return render_template('text_to_speech.html', languages=language_dict.keys())

if __name__ == "__main__":
    app.run(debug=True)
