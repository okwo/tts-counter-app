from flask import Flask, request, render_template, jsonify, session, url_for
import os, uuid

app = Flask(__name__)
app.secret_key = 'secret_key'

unique_users = set()
total_converts = 0

@app.route('/', methods=['GET', 'POST'])
def index():
    global total_converts
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())
    unique_users.add(session['user_id'])

    audio_url = None
    if request.method == 'POST':
        text = request.form.get('text', '').strip()
        speed = request.form.get('speed', '1')

        if text:
            total_converts += 1

            # 🔧 แทรกรหัสแปลงข้อความเป็นเสียงจริงที่นี่
            # ผลลัพธ์ควรคืนไฟล์ mp3 ใน static เช่น:
            audio_filename = 'sample.mp3'
            audio_url = url_for('static', filename=audio_filename)

    if request.is_json or request.method == 'POST':
        return jsonify({
            'users': len(unique_users),
            'converts': total_converts,
            'audio_url': audio_url
        })

    return render_template(
        'index.html',
        users=len(unique_users),
        converts=total_converts
    )

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
