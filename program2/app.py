import streamlit as st
import os
import zipfile
import base64
from dotenv import load_dotenv
import importlib.util
import sys
from mailjet_rest import Client

load_dotenv()

try:
    current_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(current_dir, '..', 'program1', '102303557.py')

    spec = importlib.util.spec_from_file_location("mashup_core", script_path)
    mashup_logic = importlib.util.module_from_spec(spec)
    sys.modules["mashup_core"] = mashup_logic
    spec.loader.exec_module(mashup_logic)
except Exception as e:
    st.error(f"Error loading script: {e}")
    st.stop()

def send_email_mailjet(to_email, subject, body, attachment_path):
    api_key = os.getenv('MJ_APIKEY_PUBLIC')
    api_secret = os.getenv('MJ_APIKEY_PRIVATE')
    sender_email = os.getenv('SENDER_EMAIL')
    sender_name = os.getenv('SENDER_NAME')

    if not all([api_key, api_secret, sender_email]):
        st.error("Missing Mailjet configuration.")
        return False

    mailjet = Client(auth=(api_key, api_secret), version='v3.1')

    with open(attachment_path, "rb") as f:
        encoded_file = base64.b64encode(f.read()).decode('utf-8')

    data = {
      'Messages': [
        {
          "From": {"Email": sender_email, "Name": sender_name},
          "To": [{"Email": to_email, "Name": "User"}],
          "Subject": subject,
          "TextPart": body,
          "Attachments": [
            {
              "ContentType": "application/zip",
              "Filename": os.path.basename(attachment_path),
              "Base64Content": encoded_file
            }
          ]
        }
      ]
    }

    try:
        result = mailjet.send.create(data=data)
        if result.status_code == 200:
            return True
        st.error(f"Mailjet error: {result.json()}")
        return False
    except Exception as e:
        st.error(f"Email failed: {e}")
        return False

def create_zip(file_path, zip_name):
    with zipfile.ZipFile(zip_name, 'w') as zipf:
        zipf.write(file_path, os.path.basename(file_path))

def main():
    st.title("YouTube Mashup Creator 🎵")
    st.markdown("Generate a mashup from your favorite artist.")

    with st.form("mashup_form"):
        singer_name = st.text_input("Artist Name")
        col1, col2 = st.columns(2)
        with col1:
            num_videos = st.number_input("Videos count (>10)", min_value=11, value=11)
        with col2:
            duration = st.number_input("Clip duration (>20s)", min_value=21, value=21)
        email_id = st.text_input("Your Email")
        submitted = st.form_submit_button("Generate")

    if submitted:
        if not singer_name:
            st.error("Singer name is required.")
            return
        if not email_id or "@" not in email_id:
            st.error("Valid email is required.")
            return

        with st.status("Working on it...", expanded=True) as status:
            try:
                st.write("📥 Downloading...")
                files = mashup_logic.download_videos(singer_name, int(num_videos))
                if not files:
                    status.update(label="Failed to download", state="error")
                    return

                st.write("🔄 Converting...")
                audios = mashup_logic.convert_to_audio(files)
                if not audios:
                    status.update(label="Conversion failed", state="error")
                    mashup_logic.cleanup_temp_files()
                    return

                st.write("✂️ Cutting...")
                clips = mashup_logic.cut_audio(audios, int(duration))
                if not clips:
                    status.update(label="Cutting failed", state="error")
                    mashup_logic.cleanup_temp_files()
                    return

                st.write("🧩 Merging...")
                output_file = "mashup.mp3"
                if mashup_logic.merge_audios(clips, output_file):
                    st.write("📦 Zipping...")
                    zip_file = "mashup.zip"
                    create_zip(output_file, zip_file)

                    st.write(f"📧 Sending to {email_id}...")
                    if send_email_mailjet(email_id, "Your Mashup", f"Enjoy your mashup of {singer_name}!", zip_file):
                        st.success("Sent successfully!")
                        status.update(label="Done!", state="complete")
                    else:
                        st.error("Email failed.")
                        status.update(label="Email failed", state="error")

                    if os.path.exists(output_file): os.remove(output_file)
                    if os.path.exists(zip_file): os.remove(zip_file)
                else:
                    st.error("Merge failed.")
                    status.update(label="Failed", state="error")

                mashup_logic.cleanup_temp_files()

            except Exception as e:
                st.error(f"Error: {e}")
                status.update(label="Error", state="error")
                mashup_logic.cleanup_temp_files()

if __name__ == "__main__":
    main()

