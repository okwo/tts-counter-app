from flask import Flask, request, send_file, render_template
from flask_cors import CORS
from gtts import gTTS
import tempfile, os, subprocess

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/convert", methods=["POST"])
def convert():
    data = request.get_json()
    text = data.get("text", "")
    speed = float(data.get("speed", 1.0))

    with tempfile.TemporaryDirectory() as tmpdir:
        tts_path = os.path.join(tmpdir, "tts.mp3")
        wav_path = os.path.join(tmpdir, "tts.wav")
        output_path = os.path.join(tmpdir, "output.wav")

        tts = gTTS(text=text, lang="th")
        tts.save(tts_path)

        subprocess.run(["ffmpeg", "-y", "-i", tts_path, wav_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if speed == 1.0:
            os.rename(wav_path, output_path)
        else:
            subprocess.run(["ffmpeg", "-y", "-i", wav_path, "-filter:a", f"atempo={speed}", output_path],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        return send_file(output_path, mimetype="audio/wav")

if __name__ == "__main__":
    app.run()
