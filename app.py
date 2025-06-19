from flask import Flask, request, send_file, render_template, session, jsonify, Response
from flask_cors import CORS
from flask_session import Session
from gtts import gTTS
import tempfile, os, subprocess, uuid

app = Flask(__name__)
CORS(app)

# เปิดใช้งาน session
app.secret_key = "your_secret_key"
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# ตัวแปรนับจำนวน
unique_users = set()
convert_count = 0

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/convert", methods=["POST"])
def convert():
    global convert_count, unique_users

    # ตรวจสอบว่าเป็นผู้ใช้ใหม่หรือไม่
    if "user_id" not in session:
        session["user_id"] = str(uuid.uuid4())
        unique_users.add(session["user_id"])

    convert_count += 1

    data = request.get_json()
    text = data.get("text", "")
    speed = float(data.get("speed", 1.0))

    with tempfile.TemporaryDirectory() as tmpdir:
        tts_path = os.path.join(tmpdir, "tts.mp3")
        wav_path = os.path.join(tmpdir, "tts.wav")
        output_path = os.path.join(tmpdir, "output.wav")

        tts = gTTS(text=text, lang="th")
        tts.save(tts_path)

        subprocess.run(["ffmpeg", "-y", "-i", tts_path, wav_path],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if speed == 1.0:
            os.rename(wav_path, output_path)
        else:
            subprocess.run(["ffmpeg", "-y", "-i", wav_path, "-filter:a", f"atempo={speed}", output_path],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # สร้าง response และตั้ง header แบบ manual
        response = send_file(output_path, mimetype="audio/wav",
                             as_attachment=False,
                             download_name="output.wav")
        response.headers["X-Convert-Count"] = str(convert_count)
        response.headers["X-User-Count"] = str(len(unique_users))
        return response

@app.route("/api/stats", methods=["GET"])
def get_stats():
    return jsonify({
        "convert_count": convert_count,
        "user_count": len(unique_users)
    })

if __name__ == "__main__":
    app.run(debug=True)
