from flask import Flask, request, render_template, jsonify, url_for
from tts_voice import tts_order_voice
import edge_tts
import anyio
import os, uuid

app = Flask(__name__)
app.config['SERVER_NAME'] = 'luvvoice.com'
language_dict = tts_order_voice

async def text_to_speech_edge(text, language_code):
    voice = language_dict[language_code]
    communicate = edge_tts.Communicate(text, voice)
    filename=str(uuid.uuid4()) + ".mp3"
    static_dir=os.path.join(app.root_path,'static')
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
    tmp_path = os.path.join(static_dir,filename)

    await communicate.save(tmp_path)

    return "语音合成完成：{}".format(text), filename 
# 注意我返回的是文件名而不是完整路径，以便于下面生成URL


@app.route('/', methods=['GET', 'POST'])
@app.route('/text_to_speech', methods=['GET', 'POST'])
def text_to_speech():
    if request.method == 'POST':
        data = request.form
        text = data['text']
        language_code = data['language_code']
        result_text, result_filename = anyio.run(text_to_speech_edge, text, language_code)
        result_audio_url = url_for('static', filename=result_filename, _external=True, _scheme='https')
        # Return as JSON
        return jsonify({
            'result_text': result_text,
            'result_audio_url': result_audio_url
        })

    else:
        return render_template('text_to_speech.html', languages=language_dict.keys())

if __name__ == "__main__":
    app.run(host='luvvoice.com', port=8000e)
