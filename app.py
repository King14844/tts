from flask import Flask, request, jsonify
import base64
import azure.cognitiveservices.speech as speechsdk

app = Flask(__name__)

subscription_key = "3c4121fca5c9472db7c84fc3e4442c0f"
region = "eastus"
speech_config = speechsdk.SpeechConfig(subscription=subscription_key, region=region)
speech_config.speech_synthesis_voice_name = "en-US-JennyNeural"
speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)

def generate_speech(text):
    return speech_synthesizer.speak_text(text)

def generate_viseme_data(text):
    viseme_data = []

    def viseme_cb(evt):
        viseme_data.append({
            "audio_offset": int(evt.audio_offset / 10000),
            "viseme_id": evt.viseme_id
        })

    speech_synthesizer.viseme_received.connect(viseme_cb)
    result = generate_speech(text)
    
    audio_stream = base64.b64encode(result.audio_data).decode('utf-8')

    return audio_stream, viseme_data

@app.route('/synthesize', methods=['POST'])
def synthesize_text():
    if request.method == 'POST':
        data = request.json
        text = data.get('text', '')
        if text:
            audio_stream, viseme_data = generate_viseme_data(text)
            return jsonify({"audio_data": audio_stream, "viseme_data": viseme_data})
        else:
            return jsonify({"error": "Text not provided"}), 400
    else:
        return jsonify({"error": "Invalid method"}), 405

if __name__ == '__main__':
    app.run()
