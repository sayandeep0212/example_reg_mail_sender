import streamlit as st
import json
import smtplib
import ssl
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

# --- PAGE CONFIGURATION ---
st.set_page_config(page_title="GameLiminals Email Manager", page_icon="🎮", layout="wide")

# --- SOCIAL LINKS (Hardcoded) ---
SOCIAL_LINKS = {
    "GitHub": "https://github.com/gameliminals",
    "Discord": "https://discord.com/invite/5hZsZmcC",
    "Instagram": "https://www.instagram.com/gameliminals?igsh=b2V3NzRidDd3OHF6",
    "LinkedIn": "https://www.linkedin.com/company/gameliminals/",
    "Youtube": "https://www.youtube.com/@GameLiminals",
    "Facebook": "https://www.facebook.com/gameliminals"
}

# --- HELPER FUNCTIONS ---
def load_image(filename, content_id):
    """Reads an image and prepares it for embedding."""
    try:
        with open(filename, 'rb') as f:
            img_data = f.read()
            img = MIMEImage(img_data)
            img.add_header('Content-ID', f'<{content_id}>')
            return img
    except FileNotFoundError:
        return None

def create_email_html(student_name, reg_id, whatsapp_link):
    links_html = " | ".join([f'<a href="{url}" style="color: #2E7D32; text-decoration: none;">{platform}</a>' 
                             for platform, url in SOCIAL_LINKS.items()])

    return f"""
    <html>
      <body style="font-family: Arial, sans-serif; color: #333;">
        <div style="max-width: 600px; margin: auto; border: 1px solid #ddd; padding: 20px; border-radius: 10px;">
            
            <table width="100%" style="border-bottom: 2px solid #2E7D32; padding-bottom: 10px; margin-bottom: 20px;">
                <tr>
                    <td align="left" width="50%">
                        <img src="cid:unilogo" alt="Adamas University" style="height: 60px; max-width: 150px;">
                    </td>
                    <td align="right" width="50%">
                        <img src="cid:clublogo" alt="GameLiminals" style="height: 60px; max-width: 150px;">
                    </td>
                </tr>
            </table>

            <h2 style="color: #2E7D32;">Welcome to GameLiminals! 🎮</h2>
            <p>Dear <b>{student_name}</b>,</p>
            <p>Congratulations! Your registration for the <b>Adamas University Game Development Club, GameLiminals</b> has been approved.</p>
            
            <div style="background-color: #f1f8e9; padding: 15px; border-left: 5px solid #558b2f; margin: 20px 0;">
                <p style="margin: 0;"><b>Registration ID:</b> <span style="font-family: monospace; font-size: 1.2em;">{reg_id}</span></p>
            </div>

            <p>We are excited to see you in our upcoming sessions!</p>

            <div style="text-align: center; margin: 30px 0;">
                <p style="font-size: 1.1em; font-weight: bold; margin-bottom: 15px;">
                    Follow our WhatsApp channel for more upcoming updates:
                </p>
                <a href="{whatsapp_link}" style="background-color: #25D366; color: white; padding: 12px 24px; text-decoration: none; border-radius: 25px; font-weight: bold; font-size: 16px; display: inline-block; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
                    Join WhatsApp Channel 📱
                </a>
            </div>
            <hr style="border: 0; border-top: 1px solid #eee; margin: 20px 0;">
            <p style="font-size: 0.9em;"><b>Connect with us:</b><br>{links_html}</p>
            <p style="font-size: 0.8em; color: #777;">Best Regards,<br><b>GameLiminals Team</b></p>
        </div>
      </body>
    </html>
    """

# --- MAIN APP UI ---
st.title("🎮 GameLiminals Email Manager")
st.write("Send approval emails to students with 'Pending' status.")

# Sidebar for Configuration
with st.sidebar:
    st.header("🔑 Configuration")
    sender_email = st.text_input("Sender Email", value="adamasgamingclub@gmail.com")
    sender_password = st.text_input("App Password", type="password", help="Use your Google App Password")
    whatsapp_link = st.text_input("WhatsApp Channel Link", value="https://whatsapp.com/channel/0029VbC1LwzJkK7Fn1REM332")
    
    st.header("🖼️ Images")
    st.info("Ensure 'logo.png' and 'au_logo.jpg' are in the same folder as this script.")

# Main Section
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("1. Upload Student Data")
    uploaded_file = st.file_uploader("Upload JSON File", type="json")

if uploaded_file and sender_password and whatsapp_link:
    students = json.load(uploaded_file)
    
    # Filter Students: Only keep those with Status == "pending"
    pending_students = [s for s in students if s.get("Status", "").strip().lower() == "pending"]
    
    with col2:
        st.subheader("2. Review & Send")
        st.metric("Total Students in File", len(students))
        st.metric("Students to Email (Pending Status)", len(pending_students))
        
        # Preview Section
        with st.expander("Preview Email Template"):
            preview_html = create_email_html("John Doe", "GL-2026-001", whatsapp_link)
            st.components.v1.html(preview_html, height=600, scrolling=True)

    # Send Button
    if st.button("🚀 Send Emails to Pending Students", type="primary"):
        if len(pending_students) == 0:
            st.warning("No students found with 'Pending' status.")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()
            success_count = 0
            
            # Connect to SMTP
            context = ssl.create_default_context()
            try:
                server = smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context)
                server.login(sender_email, sender_password)
                
                for i, student in enumerate(pending_students):
                    name = student.get("Full Name", "Student")
                    email = student.get("Email")
                    reg_id = student.get("Application ID", "N/A")
                    
                    if email:
                        msg = MIMEMultipart("related")
                        msg["Subject"] = "Congratulations! Welcome to GameLiminals 🎮"
                        msg["From"] = sender_email
                        msg["To"] = email
                        
                        html_part = MIMEText(create_email_html(name, reg_id, whatsapp_link), "html")
                        msg.attach(html_part)
                        
                        # Attach Images
                        club_img = load_image("logo.png", "clublogo")
                        uni_img = load_image("au_logo.jpg", "unilogo")
                        if club_img: msg.attach(club_img)
                        if uni_img: msg.attach(uni_img)
                        
                        server.sendmail(sender_email, email, msg.as_string())
                        success_count += 1
                    
                    # Update Progress
                    progress = (i + 1) / len(pending_students)
                    progress_bar.progress(progress)
                    status_text.text(f"Sending to: {name}...")
                
                server.quit()
                st.success(f"🎉 Successfully sent {success_count} emails!")
                st.balloons()
                
            except Exception as e:
                st.error(f"Error sending emails: {e}")

elif not uploaded_file:
    st.info("👈 Please upload the JSON file to begin.")
