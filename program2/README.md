# Program 2 - YouTube Mashup Web App

Streamlit web application for creating audio mashups with email delivery.

## Features

- Web-based interface for mashup generation
- Uses the same core logic as the CLI tool
- Sends completed mashup as ZIP file via email
- Powered by Mailjet for email delivery

## Installation

```powershell
cd program2
pip install -r requirements.txt
```

## Dependencies

- streamlit - Web framework
- yt-dlp - YouTube video downloading
- pydub - Audio processing
- imageio-ffmpeg - FFmpeg binaries
- audioop-lts - Audio operations support
- mailjet-rest - Email sending via Mailjet
- python-dotenv - Environment variable loading

## Environment Setup

Create a `.env` file in the Mashup root folder with your Mailjet credentials:

```
SENDER_NAME=Your Name
SENDER_EMAIL=your-verified-email@example.com
MJ_APIKEY_PUBLIC=your-mailjet-public-api-key
MJ_APIKEY_PRIVATE=your-mailjet-private-api-key
```

You can copy `sample .env` from the root folder as a template.

### Getting Mailjet Credentials

1. Sign up at [Mailjet](https://www.mailjet.com/)
2. Verify your sender email address
3. Go to API Key Management to get your public and private keys

## Running the App

```powershell
cd program2
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

## Usage

1. Enter the artist name
2. Set number of videos (minimum 11)
3. Set clip duration in seconds (minimum 21)
4. Enter your email address
5. Click Generate
6. Wait for processing to complete
7. Check your email for the mashup ZIP file

## How It Works

1. Uses core functions from `program1/102303557.py`
2. Downloads and processes videos through the web interface
3. Creates a ZIP file with the final mashup
4. Sends the ZIP to the provided email address via Mailjet
5. Cleans up all temporary files

## Troubleshooting

**Missing Mailjet configuration:**
Ensure all environment variables are set in the `.env` file.

**Email not received:**
Check spam folder. Verify sender email is verified in Mailjet.

**Processing timeout:**
Large numbers of videos may take several minutes. Be patient.

**Error loading script:**
Ensure program1/102303557.py exists and has no syntax errors.

