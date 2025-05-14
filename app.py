from flask import Flask, render_template, request, send_from_directory
import yt_dlp
import os
import sys

app = Flask(__name__)

# Auto-detect system Downloads folder
def get_download_folder():
    if sys.platform == 'win32':
        return os.path.join(os.environ['USERPROFILE'], 'Downloads')
    else:
        return os.path.join(os.path.expanduser('~'), 'Downloads')

DOWNLOAD_FOLDER = get_download_folder()
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        try:
            # Detect which form was submitted
            if "youtube_url" in request.form:
                url = request.form["youtube_url"]
                format_choice = request.form.get("youtube_format", "mp4")
                return download_youtube(url, format_choice)

            elif "facebook_url" in request.form:
                url = request.form["facebook_url"]
                return download_social(url)

            elif "tiktok_url" in request.form:
                url = request.form["tiktok_url"]
                return download_social(url)

            elif "instagram_url" in request.form:
                url = request.form["instagram_url"]
                return download_social(url)

            else:
                return render_template("index.html", error="Unknown form submitted.")

        except Exception as e:
            return render_template("index.html", error=str(e))

    return render_template("index.html")


def download_youtube(url, format_choice):
    try:
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s')
        }

        if format_choice == "mp4":
            ydl_opts.update({
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/mp4',
                'merge_output_format': 'mp4',
            })
        elif format_choice == "mp3":
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            })

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info_dict)

            # If MP3, change extension
            if format_choice == "mp3":
                filename = os.path.splitext(filename)[0] + ".mp3"

            filename_only = os.path.basename(filename)
            return render_template("index.html", success=True, filename=filename_only, download_folder=DOWNLOAD_FOLDER)

    except Exception as e:
        return render_template("index.html", error=str(e))


def download_social(url):
    try:
        ydl_opts = {
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'format': 'best',
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info_dict)

            filename_only = os.path.basename(filename)
            return render_template("index.html", success=True, filename=filename_only, download_folder=DOWNLOAD_FOLDER)

    except Exception as e:
        return render_template("index.html", error=str(e))


@app.route("/downloads/<filename>")
def download_file(filename):
    return send_from_directory(DOWNLOAD_FOLDER, filename, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)
