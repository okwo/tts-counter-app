from flask import Flask, render_template, request, jsonify
import json
import os

app = Flask(__name__)
COUNTER_FILE = "counter.json"

# โหลดข้อมูล counter หรือสร้างใหม่ถ้าไม่มี
if not os.path.exists(COUNTER_FILE):
    with open(COUNTER_FILE, "w") as f:
        json.dump({"unique_ips": [], "convert_count": 0}, f)

def load_counters():
    with open(COUNTER_FILE, "r") as f:
        return json.load(f)

def save_counters(data):
    with open(COUNTER_FILE, "w") as f:
        json.dump(data, f)

@app.route("/")
def index():
    data = load_counters()
    return render_template("index.html", users=len(data["unique_ips"]), converts=data["convert_count"])

@app.route("/convert", methods=["POST"])
def convert():
    user_ip = request.remote_addr
    data = load_counters()

    if user_ip not in data["unique_ips"]:
        data["unique_ips"].append(user_ip)
    data["convert_count"] += 1
    save_counters(data)

    # ส่งกลับค่าแบบ JSON
    return jsonify(success=True)

@app.route("/counter")
def counter():
    data = load_counters()
    return jsonify(users=len(data["unique_ips"]), converts=data["convert_count"])

if __name__ == "__main__":
    app.run(debug=True)
