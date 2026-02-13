# Program 1 - YouTube Mashup CLI

Command line tool to create audio mashups from YouTube videos.

## Features

- Download N videos (N > 10) for any artist from YouTube
- Convert all videos to MP3 audio
- Trim first Y seconds (Y > 20) from each track
- Merge all clips into a single output file
- Automatic cleanup of temporary files

## Installation

```powershell
cd program1
pip install -r requirements.txt
```

## Dependencies

- yt-dlp - YouTube video downloading
- pydub - Audio processing
- imageio-ffmpeg - FFmpeg binaries
- audioop-lts - Audio operations support

## Usage

```powershell
python 102303557.py <SingerName> <NumberOfVideos> <AudioDuration> <OutputFileName>
```

### Parameters

| Parameter | Description | Requirement |
|-----------|-------------|-------------|
| SingerName | Artist name (quote if spaces) | Non-empty string |
| NumberOfVideos | Number of videos to download | Integer > 10 |
| AudioDuration | Seconds to keep from each clip | Integer > 20 |
| OutputFileName | Output file name | Must end with .mp3 |

### Examples

```powershell
python 102303557.py "Sharry Maan" 12 25 mashup.mp3
python 102303557.py "Arijit Singh" 15 30 output.mp3
```

## How It Works

1. **Search** - Finds videos on YouTube for the given artist
2. **Download** - Downloads audio from each video using yt-dlp
3. **Convert** - Converts downloaded files to MP3 using FFmpeg
4. **Trim** - Cuts first N seconds from each audio file
5. **Merge** - Concatenates all clips into final output
6. **Cleanup** - Removes all temporary files

## Error Handling

The program validates inputs and shows appropriate messages:

| Error | Message |
|-------|---------|
| Wrong argument count | Error: Incorrect number of parameters! |
| Videos ≤ 10 | NumberOfVideos must be greater than 10! |
| Duration ≤ 20 | AudioDuration must be greater than 20 seconds! |
| Wrong extension | OutputFileName must end with .mp3! |

## Troubleshooting

**FFmpeg not found:**
Reinstall dependencies - imageio-ffmpeg includes bundled FFmpeg binaries.

**No videos found:**
Check internet connection and verify artist name spelling.

**Download errors:**
Some videos may be restricted. The program continues with available videos.
