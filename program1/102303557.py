import sys
import os
import yt_dlp
from pydub import AudioSegment
import traceback
import subprocess

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

    try:
        ydl_opts_search = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': True,
        }

        search_query = f"ytsearch{num_videos}:{singer_name} songs"

        with yt_dlp.YoutubeDL(ydl_opts_search) as ydl:
            search_results = ydl.extract_info(search_query, download=False)

        if not search_results or 'entries' not in search_results:
            print("Error: No videos found!")
            return []

        videos = search_results['entries']

        if len(videos) < num_videos:
            print(f"Warning: Only found {len(videos)} videos out of {num_videos} requested.")

        downloaded_files = []

        for i, video in enumerate(videos[:num_videos]):
            if not video:
                continue

            try:
                video_url = f"https://www.youtube.com/watch?v={video['id']}"
                temp_filename = f"temp_video_{i}"

                print(f"Downloading video {i+1}/{num_videos}: {video.get('title', 'Unknown')}")

                ydl_opts_download = {
                    'format': 'bestaudio/best',
                    'outtmpl': temp_filename,
                    'quiet': True,
                    'no_warnings': True,
                    'noprogress': True,
                }

                with yt_dlp.YoutubeDL(ydl_opts_download) as ydl:
                    ydl.extract_info(video_url, download=True)

                found = False
                for ext in ['.webm', '.m4a', '.mp4', '.opus', '.mp3', '']:
                    potential_file = temp_filename + ext
                    if os.path.exists(potential_file):
                        downloaded_files.append(potential_file)
                        print(f"Downloaded: {video.get('title', 'Unknown')} ({potential_file})")
                        found = True
                        break

                if not found:
                    for file in os.listdir('.'):
                        if file.startswith(temp_filename):
                            downloaded_files.append(file)
                            print(f"Downloaded: {video.get('title', 'Unknown')} ({file})")
                            found = True
                            break

                if not found:
                    print(f"Warning: Could not locate downloaded file for video {i+1}")

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
            print(f"Converting audio {i+1} to MP3...")
            audio_file = f"temp_audio_{i}.mp3"

            if FFMPEG_PATH and os.path.exists(FFMPEG_PATH):
                cmd = [
                    FFMPEG_PATH, '-i', video_file, '-vn', '-acodec', 'libmp3lame', '-y', audio_file
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0 and os.path.exists(audio_file):
                    audio_files.append(audio_file)
                    print(f"Converted: {audio_file}")
                else:
                    print(f"FFmpeg conversion failed for audio {i+1}")
            else:
                audio = AudioSegment.from_file(video_file)
                audio.export(audio_file, format="mp3")
                audio_files.append(audio_file)
                print(f"Converted: {audio_file}")

        except Exception as e:
            print(f"Conversion error for audio {i+1}: {e}")
            continue

    return audio_files


def cut_audio(audio_files, duration_seconds):
    cut_files = []

    for i, audio_file in enumerate(audio_files):
        try:
            print(f"Cutting first {duration_seconds}s from audio {i+1}...")
            cut_file = f"temp_cut_{i}.mp3"

            if FFMPEG_PATH and os.path.exists(FFMPEG_PATH):
                cmd = [
                    FFMPEG_PATH, '-i', audio_file, '-t', str(duration_seconds),
                    '-acodec', 'copy', '-y', cut_file
                ]
                result = subprocess.run(cmd, capture_output=True, text=True)
                if result.returncode == 0 and os.path.exists(cut_file):
                    cut_files.append(cut_file)
                    print(f"Saved clip: {cut_file}")
                else:
                    print(f"FFmpeg copy failed for audio {i+1}")
            else:
                duration_ms = duration_seconds * 1000
                audio = AudioSegment.from_file(audio_file)
                cut_segment = audio[:duration_ms] if len(audio) >= duration_ms else audio
                cut_segment.export(cut_file, format="mp3")
                cut_files.append(cut_file)
                print(f"Saved clip: {cut_file}")

        except Exception as e:
            print(f"Cutting error for audio {i+1}: {e}")
            continue

    return cut_files


def merge_audios(audio_files, output_filename):
    try:
        print(f"Merging {len(audio_files)} clips...")

        if FFMPEG_PATH and os.path.exists(FFMPEG_PATH):
            list_file = "temp_file_list.txt"
            with open(list_file, 'w', encoding='utf-8') as f:
                for audio_file in audio_files:
                    path = os.path.abspath(audio_file).replace('\\', '/')
                    f.write(f"file '{path}'\n")

            cmd = [
                FFMPEG_PATH, '-f', 'concat', '-safe', '0', '-i', list_file,
                '-c', 'copy', '-y', output_filename
            ]

            result = subprocess.run(cmd, capture_output=True, text=True)

            try: os.remove(list_file)
            except: pass

            if result.returncode == 0 and os.path.exists(output_filename):
                print(f"Created mashup: {output_filename}")
                return True

        combined = AudioSegment.empty()
        for i, f in enumerate(audio_files):
            print(f"Adding clip {i+1}...")
            combined += AudioSegment.from_file(f)

        combined.export(output_filename, format="mp3")
        print(f"Created mashup: {output_filename}")
        return True

    except Exception as e:
        print(f"Merge failed: {e}")
        traceback.print_exc()
        return False


def cleanup_temp_files():
    for file in os.listdir('.'):
        if file.startswith('temp_'):
            try: os.remove(file)
            except: pass

def main():
    if len(sys.argv) != 5:
        print("Usage: python 102303557.py <Singer> <Count> <Duration> <Output.mp3>")
        sys.exit(1)

    singer = sys.argv[1]

    try:
        count = int(sys.argv[2])
        duration = int(sys.argv[3])
    except ValueError:
        print("Error: Count and duration must be numbers.")
        sys.exit(1)

    output = sys.argv[4]

    if count <= 10:
        print("Error: Count must be > 10")
        sys.exit(1)
    if duration <= 20:
        print("Error: Duration must be > 20")
        sys.exit(1)
    if not output.endswith('.mp3'):
        print("Error: Output must be .mp3")
        sys.exit(1)

    print(f"Starting mashup for {singer}...")

    try:
        files = download_videos(singer, count)
        if not files: return

        audios = convert_to_audio(files)
        if not audios:
            cleanup_temp_files()
            return

        clips = cut_audio(audios, duration)
        if not clips:
            cleanup_temp_files()
            return

        if merge_audios(clips, output):
            print("\nDone! Enjoy your mashup.")
        else:
            print("Failed to merge.")

        cleanup_temp_files()

    except KeyboardInterrupt:
        print("\nStopped.")
        cleanup_temp_files()
    except Exception as e:
        print(f"Unexpected error: {e}")
        traceback.print_exc()
        cleanup_temp_files()


if __name__ == "__main__":
    main()