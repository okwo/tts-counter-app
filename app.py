from flask import Flask, request, send_file, render_template, session, jsonify
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

# ฟังก์ชันปรับเสียงด้วย ffmpeg
def adjust_audio_style(input_path, output_path, style):
    filters = {
        "normal": None,
        "fast": "atempo=1.3",
        "slow": "atempo=0.8",
        "child": "atempo=1.1,asetrate=44100*1.05",
        "deep": "atempo=0.9,asetrate=44100*0.95"
    }
    selected_filter = filters.get(style)

    if selected_filter:
        subprocess.run(["ffmpeg", "-y", "-i", input_path, "-filter:a", selected_filter, output_path],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:
        os.rename(input_path, output_path)

@app.route("/")
def home():
    return render_template("index.html")  # ต้องมี templates/index.html

@app.route("/api/convert", methods=["POST"])
def convert():
    global convert_count, unique_users

    if "user_id" not in session:
        session["user_id"] = str(uuid.uuid4())
        unique_users.add(session["user_id"])

    convert_count += 1

    data = request.get_json()
    text = data.get("text", "")
    style = data.get("style", "normal")  # รับค่าจากหน้าเว็บ

    with tempfile.TemporaryDirectory() as tmpdir:
        tts_path = os.path.join(tmpdir, "tts.mp3")
        wav_path = os.path.join(tmpdir, "tts.wav")
        output_path = os.path.join(tmpdir, "output.wav")

        # สร้างเสียงด้วย gTTS
        tts = gTTS(text=text, lang="th")
        tts.save(tts_path)

        # แปลง mp3 เป็น wav
        subprocess.run(["ffmpeg", "-y", "-i", tts_path, wav_path],
                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # ปรับเสียงตาม style
        adjust_audio_style(wav_path, output_path, style)

        # ส่งเสียงกลับ
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
