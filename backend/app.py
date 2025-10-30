from flask import Flask, request, jsonify, send_file
import requests
import io
import os

app = Flask(__name__)

ADMIN_PASSWORD = "mysecret123"
DOWNLOAD_COUNT_FILE = "downloads.txt"

if not os.path.exists(DOWNLOAD_COUNT_FILE):
    with open(DOWNLOAD_COUNT_FILE, "w") as f:
        f.write("0")

def read_count():
    with open(DOWNLOAD_COUNT_FILE, "r") as f:
        return int(f.read().strip() or 0)

def write_count(count):
    with open(DOWNLOAD_COUNT_FILE, "w") as f:
        f.write(str(count))

@app.route("/")
def home():
    return jsonify({"message": "Snap Downloader API active!"})

@app.route("/download", methods=["POST"])
def download_video():
    data = request.get_json()
    snap_url = data.get("url")
    if not snap_url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        video = requests.get(snap_url, stream=True)
        video.raise_for_status()

        count = read_count() + 1
        write_count(count)

        return send_file(
            io.BytesIO(video.content),
            mimetype="video/mp4",
            as_attachment=True,
            download_name="snap_video.mp4",
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/admin/login", methods=["POST"])
def admin_login():
    data = request.get_json()
    password = data.get("password")
    if password == ADMIN_PASSWORD:
        return jsonify({"success": True})
    return jsonify({"success": False}), 401

@app.route("/admin/stats", methods=["GET"])
def admin_stats():
    password = request.args.get("password")
    if password != ADMIN_PASSWORD:
        return jsonify({"error": "Unauthorized"}), 401
    count = read_count()
    return jsonify({"downloads": count})

@app.route("/admin/reset", methods=["POST"])
def reset_stats():
    data = request.get_json()
    password = data.get("password")
    if password != ADMIN_PASSWORD:
        return jsonify({"error": "Unauthorized"}), 401
    write_count(0)
    return jsonify({"success": True, "message": "Stats reset."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
