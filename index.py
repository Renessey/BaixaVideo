import os
import yt_dlp
import tempfile
from flask import Flask, render_template, request, jsonify, send_file

app = Flask(__name__)

# Armazena o progresso do download
download_progress = {"percent": 0}

def hook(d):
    if d['status'] == 'downloading':
        total = d.get("total_bytes") or d.get("total_bytes_estimate")
        downloaded = d.get("downloaded_bytes", 0)
        if total:
            percent = int(downloaded * 100 / total)
            download_progress["percent"] = percent
    if d['status'] == 'finished':
        download_progress["percent"] = 100

def get_video_info(url):
    ydl_opts = {
        "quiet": True,
        "noplaylist": True,
        "extract_flat": False,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
    
    formats = []
    seen = set()
    for f in info.get("formats", []):
        height = f.get("height")
        if height and height not in seen:
            seen.add(height)
            formats.append({
                "height": height,
                "res": f"{height}p"
            })
    
    formats.sort(key=lambda x: x["height"], reverse=True)
    return {
        "title": info.get("title", "Video"),
        "thumbnail": info.get("thumbnail", ""),
        "formats": formats
    }

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/info", methods=["POST"])
def info():
    try:
        url = request.json.get("url")
        if not url:
            return jsonify({"error": "URL vazia"}), 400
        data = get_video_info(url)
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/progress")
def progress():
    return jsonify(download_progress)

@app.route("/download")
def download():
    download_progress["percent"] = 0
    url = request.args.get("url")
    res = request.args.get("res")
    tipo = request.args.get("tipo")

    temp_dir = tempfile.gettempdir()

    if tipo == "mp3":
        ydl_opts = {
            "ffmpeg_location": "/usr/bin/ffmpeg",  # Localização forçada para Docker/Railway
            "format": "bestaudio/best",
            "outtmpl": os.path.join(temp_dir, "%(title)s.%(ext)s"),
            "progress_hooks": [hook],
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
            "noplaylist": True
        }
    else:
        # Formato que garante vídeo + áudio juntos
        f_str = f"bestvideo[height<={res}][ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"
        ydl_opts = {
            "ffmpeg_location": "/usr/bin/ffmpeg",  # Localização forçada para Docker/Railway
            "format": f_str,
            "outtmpl": os.path.join(temp_dir, "%(title)s.%(ext)s"),
            "progress_hooks": [hook],
            "noplaylist": True,
            "merge_output_format": "mp4"
        }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info_dict)
            
            if tipo == "mp3":
                filename = os.path.splitext(filename)[0] + ".mp3"
            else:
                if not filename.endswith(".mp4"):
                    filename = os.path.splitext(filename)[0] + ".mp4"

        return send_file(filename, as_attachment=True)
    except Exception as e:
        return str(e), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)