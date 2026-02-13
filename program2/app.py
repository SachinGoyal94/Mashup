import streamlit as st
import os
import zipfile
import base64
from dotenv import load_dotenv
import importlib.util
import sys
from mailjet_rest import Client

load_dotenv()

current_dir = os.path.dirname(os.path.abspath(__file__))
script_path = os.path.join(current_dir, '..', 'program1', '102303557.py')

spec = importlib.util.spec_from_file_location("mashup_core", script_path)
mashup_logic = importlib.util.module_from_spec(spec)
sys.modules["mashup_core"] = mashup_logic
spec.loader.exec_module(mashup_logic)


def send_email_mailjet(to_email, subject, body, attachment_path):
    api_key = os.getenv('MJ_APIKEY_PUBLIC')
    api_secret = os.getenv('MJ_APIKEY_PRIVATE')
    sender_email = os.getenv('SENDER_EMAIL')
    sender_name = os.getenv('SENDER_NAME')

    mailjet = Client(auth=(api_key, api_secret), version='v3.1')

    with open(attachment_path, "rb") as f:
        encoded_file = base64.b64encode(f.read()).decode('utf-8')

    data = {
      'Messages': [{
        "From": {"Email": sender_email, "Name": sender_name},
        "To": [{"Email": to_email}],
        "Subject": subject,
        "TextPart": body,
        "Attachments": [{
            "ContentType": "application/zip",
            "Filename": os.path.basename(attachment_path),
            "Base64Content": encoded_file
        }]
      }]
    }

    result = mailjet.send.create(data=data)
    return result.status_code == 200


def create_zip(file_path, zip_name):
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        zipf.write(file_path, os.path.basename(file_path))


def main():
    st.title("YouTube Mashup Creator 🎵")

    singer_name = st.text_input("Artist Name")
    num_videos = st.number_input("Videos count (>10)", min_value=11, value=11)
    duration = st.number_input("Clip duration (>20s)", min_value=21, value=21)
    email_id = st.text_input("Your Email")

    if st.button("Generate"):

        files = mashup_logic.download_videos(singer_name, int(num_videos))
        if not files:
            st.error("Download failed")
            return

        audios = mashup_logic.convert_to_audio(files)
        clips = mashup_logic.cut_audio(audios, int(duration))

        output_file = "mashup.mp3"

        if mashup_logic.merge_audios(clips, output_file):
            zip_file = "mashup.zip"
            create_zip(output_file, zip_file)

            if send_email_mailjet(
                    email_id,
                    "Your Mashup",
                    "Enjoy your mashup!",
                    zip_file):
                st.success("Mashup sent successfully!")

            os.remove(output_file)
            os.remove(zip_file)

        mashup_logic.cleanup_temp_files()


if __name__ == "__main__":
    main()
