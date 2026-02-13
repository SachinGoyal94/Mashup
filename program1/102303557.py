import sys
import os
import yt_dlp
from pydub import AudioSegment
import traceback
import subprocess
import time

FFMPEG_PATH = None

try:
    import imageio_ffmpeg
    FFMPEG_PATH = imageio_ffmpeg.get_ffmpeg_exe()
    os.environ["IMAGEIO_FFMPEG_EXE"] = FFMPEG_PATH

    if os.path.exists(FFMPEG_PATH):
        AudioSegment.converter = FFMPEG_PATH
        AudioSegment.ffmpeg = FFMPEG_PATH
except ImportError:
    pass


def download_videos(singer_name, num_videos):
    try:
        ydl_opts_search = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'skip_download': True,
            'extractor_args': {
                'youtube': {
                    'player_client': ['android', 'web']
                }
            }
        }

        search_query = f"ytsearch{num_videos}:{singer_name} songs"

        with yt_dlp.YoutubeDL(ydl_opts_search) as ydl:
            search_results = ydl.extract_info(search_query, download=False)

        if not search_results or 'entries' not in search_results:
            return []

        videos = search_results['entries']
        downloaded_files = []

        for i, video in enumerate(videos[:num_videos]):
            if not video:
                continue

            time.sleep(2)

            video_url = f"https://www.youtube.com/watch?v={video['id']}"
            temp_filename = f"temp_video_{i}"

            ydl_opts_download = {
                'format': 'bestaudio[ext=m4a]/bestaudio[ext=webm]/bestaudio/best',
                'outtmpl': temp_filename + '.%(ext)s',
                'quiet': True,
                'no_warnings': True,
                'noprogress': True,
                'retries': 10,
                'fragment_retries': 10,
                'skip_unavailable_fragments': True,
                'nocheckcertificate': True,
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0'
                },
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android', 'web', 'ios']
                    }
                }
            }

            with yt_dlp.YoutubeDL(ydl_opts_download) as ydl:
                ydl.extract_info(video_url, download=True)

            for file in os.listdir('.'):
                if file.startswith(temp_filename):
                    downloaded_files.append(file)
                    break

        return downloaded_files

    except:
        return []


def convert_to_audio(video_files):
    audio_files = []

    for i, video_file in enumerate(video_files):
        try:
            audio_file = f"temp_audio_{i}.mp3"

            cmd = [
                FFMPEG_PATH,
                '-i', video_file,
                '-vn',
                '-acodec', 'libmp3lame',
                '-y',
                audio_file
            ]

            subprocess.run(cmd, capture_output=True)

            if os.path.exists(audio_file):
                audio_files.append(audio_file)

        except:
            pass

    return audio_files


def cut_audio(audio_files, duration_seconds):
    cut_files = []

    for i, audio_file in enumerate(audio_files):
        try:
            cut_file = f"temp_cut_{i}.mp3"

            cmd = [
                FFMPEG_PATH,
                '-i', audio_file,
                '-t', str(duration_seconds),
                '-acodec', 'copy',
                '-y',
                cut_file
            ]

            subprocess.run(cmd, capture_output=True)

            if os.path.exists(cut_file):
                cut_files.append(cut_file)

        except:
            pass

    return cut_files


def merge_audios(audio_files, output_filename):
    try:
        list_file = "temp_file_list.txt"

        with open(list_file, 'w', encoding='utf-8') as f:
            for audio_file in audio_files:
                path = os.path.abspath(audio_file).replace('\\', '/')
                f.write(f"file '{path}'\n")

        cmd = [
            FFMPEG_PATH,
            '-f', 'concat',
            '-safe', '0',
            '-i', list_file,
            '-c', 'copy',
            '-y',
            output_filename
        ]

        subprocess.run(cmd, capture_output=True)
        os.remove(list_file)

        return os.path.exists(output_filename)

    except:
        return False


def cleanup_temp_files():
    for file in os.listdir('.'):
        if file.startswith('temp_'):
            try:
                os.remove(file)
            except:
                pass

