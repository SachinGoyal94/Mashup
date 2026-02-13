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
    print(f"Searching for videos of '{singer_name}'...")

    common_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'en-us,en;q=0.5',
    }

    try:
        ydl_opts_search = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
            'skip_download': True,
            'nocheckcertificate': True,
            'ignoreerrors': True,
            'logtostderr': False,
            'http_headers': common_headers,
        }

        search_query = f"ytsearch{num_videos}:{singer_name} songs"

        with yt_dlp.YoutubeDL(ydl_opts_search) as ydl:
            search_results = ydl.extract_info(search_query, download=False)

        if not search_results or 'entries' not in search_results:
            print("Error: No videos found!")
            return []

        videos = search_results['entries']

        if len(videos) < num_videos:
             print(f"Warning: Only found {len(videos)} videos.")

        downloaded_files = []

        for i, video in enumerate(videos[:num_videos]):
            if not video:
                continue

            time.sleep(2)

            try:
                video_url = f"https://www.youtube.com/watch?v={video['id']}"
                temp_filename = f"temp_video_{i}"

                print(f"Downloading video {i+1}/{num_videos}: {video.get('title', 'Unknown')}")

                ydl_opts_download = {
                    'format': 'bestaudio/best',
                    'outtmpl': temp_filename + '.%(ext)s',
                    'quiet': True,
                    'no_warnings': True,
                    'nocheckcertificate': True,
                    'ignoreerrors': True,
                    'logtostderr': False,
                    'http_headers': common_headers,
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['android', 'ios'],
                        }
                    }
                }

                # Start of optional cookie usage
                if os.path.exists('cookies.txt'):
                    ydl_opts_download['cookiefile'] = 'cookies.txt'
                # End of optional cookie usage

                with yt_dlp.YoutubeDL(ydl_opts_download) as ydl:
                    ydl.extract_info(video_url, download=True)

                found = False
                for file in os.listdir('.'):
                    if file.startswith(temp_filename) and file.split('.')[-1] in ['webm', 'm4a', 'mp3', 'opus', 'mp4']:
                        downloaded_files.append(file)
                        print(f"Downloaded: {file}")
                        found = True
                        break

                if not found:
                    print(f"Warning: File not found for {video.get('title')}")

            except Exception as e:
                print(f"Error downloading video {i+1}: {e}")
                continue

        return downloaded_files

    except Exception as e:
        print(f"Search failed: {e}")
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

