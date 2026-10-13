import os
import json
import random
import time
import threading
import schedule
import smtplib
import requests
import pandas as pd
import streamlit as st
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from streamlit_calendar import calendar
from streamlit_js_eval import get_geolocation

# App Setup
st.set_page_config(
    page_title="DanceVault", 
    page_icon="🩰", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Styling (Color Palette & Rounded Square Buttons)[cite: 2]
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600&family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Great+Vibes&display=swap');

    .stApp {
        background-color: #F8F3EA;
        color: #0B1957;
        font-family: 'Playfair Display', serif;
    }

    .main-title {
        font-family: 'Cinzel', serif;
        color: #0B1957 !important;
        text-align: center;
        font-weight: 600;
        font-size: 3.5rem;
        margin-bottom: 0;
        padding-top: 1rem;
    }

    .script-subtitle {
        font-family: 'Great Vibes', cursive;
        font-size: 2rem !important;
        color: #FA9EBC;
        text-align: center;
        margin-top: -1.2rem;
        margin-bottom: 3rem;
    }

    h1, h2, h3, h4 {
        font-family: 'Cinzel', serif !important;
        font-weight: 400;
        color: #0B1957 !important;
    }

    .stButton>button {
        background: #FA9EBC !important;
        color: #0B1957 !important;
        border-radius: 10px !important;
        border: 1px solid #FFDBD1 !important;
        font-family: 'Cinzel', serif !important;
        font-weight: 600;
        font-size: 1rem;
        padding: 0.6rem 2rem !important;
        width: 100%;
        margin-top: 0.5rem;
    }

    .card {
        background-color: #FFFFFF;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(11,25,87,0.05);
        border: 1px solid #FFDBD1;
        margin-bottom: 1rem;
    }
    
    .card-accent {
        border-left: 5px solid #FA9EBC;
    }
    </style>
""", unsafe_allow_html=True)

# File Paths
DATA_DIR = "./local_dance_vault"
VAULT_FILE = "./vault_database.json"
USER_FILE = "./users_database.json"
os.makedirs(DATA_DIR, exist_ok=True)


def load_db(filepath, default):
    if os.path.exists(filepath):
        with open(filepath, "r") as f:
            return json.load(f)
    return default


def save_db(data, filepath):
    with open(filepath, "w") as f:
        json.dump(data, f, indent=4)


def delete_vault_item(item_id, items):
    clean_items = []
    for item in items:
        if item.get("id") == item_id:
            if "path" in item and os.path.exists(item["path"]):
                try:
                    os.remove(item["path"])
                except OSError:
                    pass
        else:
            clean_items.append(item)
    return clean_items


def delete_account(email):
    vault_items = load_db(VAULT_FILE, [])
    retained_items = []
    for item in vault_items:
        if item.get("user") == email:
            if "path" in item and os.path.exists(item["path"]):
                try:
                    os.remove(item["path"])
                except OSError:
                    pass
        else:
            retained_items.append(item)
    save_db(retained_items, VAULT_FILE)

    users = load_db(USER_FILE, {})
    if email in users:
        del users[email]
        save_db(users, USER_FILE)


def send_email(to_email, payload, action="verification"):
    try:
        smtp_email = st.secrets["smtp"]["email"]
        smtp_pass = st.secrets["smtp"]["password"]
        
        subjects = {
            "verification": "DanceVault - Security Code",
            "password reset": "DanceVault - Password Reset Code",
            "welcome": "Welcome to DanceVault",
            "reminder": "DanceVault Daily Journal Reminder"
        }

        messages = {
            "verification": f"Your verification code is: {payload}",
            "password reset": f"Your reset code is: {payload}",
            "welcome": f"Hello {payload},\n\nYour account is now active!",
            "reminder": "Don't forget to log your daily dance reflections today!"
        }

        msg = MIMEMultipart()
        msg['From'] = f"DanceVault <{smtp_email}>"
        msg['To'] = to_email
        msg['Subject'] = subjects.get(action, "DanceVault Notification")
        msg.attach(MIMEText(messages.get(action, str(payload)), 'plain'))
        
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(smtp_email, smtp_pass)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Email delivery error: {e}")
        return False


def get_zip_coords(zipcode):
    try:
        url = f"https://nominatim.openstreetmap.org/search?postalcode={zipcode}&country=USA&format=json&addressdetails=1"
        res = requests.get(url, headers={"User-Agent": "DanceVault/1.0"}, timeout=5).json()
        if res:
            addr = res[0].get("address", {})
            city = addr.get("city") or addr.get("town") or addr.get("village") or "Local Area"
            return float(res[0]["lat"]), float(res[0]["lon"]), city, addr.get("state", "US")
    except Exception:
        pass
    return None, None, None, None


def reverse_geocode(lat, lon):
    try:
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&addressdetails=1"
        res = requests.get(url, headers={"User-Agent": "DanceVault/1.0"}, timeout=5).json()
        if res:
            addr = res.get("address", {})
            city = addr.get("city") or addr.get("town") or addr.get("village") or "Local Area"
            return city, addr.get("state", "US"), addr.get("postcode", "Local")
    except Exception:
        pass
    return "Detected Area", "US", "Local"


# Scheduler Task
def send_daily_reminders():
    users = load_db(USER_FILE, {})
    for email, profile in users.items():
        if profile.get("email_reminders", True) and profile.get("verified", False):
            send_email(email, "", action="reminder")


def start_scheduler():
    schedule.every().day.at("20:00").do(send_daily_reminders)
    while True:
        schedule.run_pending()
        time.sleep(60)


if "scheduler_running" not in st.session_state:
    st.session_state.scheduler_running = True
    threading.Thread(target=start_scheduler, daemon=True).start()

# Constant Collections
DANCE_STYLES = [
    "Afrobeat", "Acro Dance", "Bachata", "Ballet", "Ballroom", "Belly Dance", 
    "Bharatanatyam", "Bhangra", "Breakdancing", "Capoeira", "Cha-Cha", "Contemporary", 
    "Dancehall", "Flamenco", "Hip Hop", "House Dance", "Jazz", "K-Pop", "Krumping", 
    "Latin Dance", "Locking", "Merengue", "Modern", "Popping", "Salsa", "Samba", 
    "Tango", "Tap", "Vogue", "Waltz", "Other"
]

AVATARS = ["🩰", "💃", "🕺", "🧘", "🧠", "🎭", "✨"]

MOTIVATIONAL_QUOTES = [
    ("Dance is the hidden language of the soul.", "Martha Graham"),
    ("Great dancers are great because of their passion, not technique.", "Martha Graham"),
    ("To dance is to be out of yourself. Larger, more beautiful, more powerful.", "Agnes de Mille"),
    ("Dance enables you to find yourself and lose yourself at the same time.", "Bob Fosse"),
    ("Movement never lies. It tells the state of the soul.", "Martha Graham"),
    ("Every day brings a chance to kick off your shoes and dance.", "Oprah Winfrey"),
    ("There are shortcuts to happiness, and dancing is one of them.", "Vicki Baum"),
    ("Practice makes you good, persistence makes you great.", "Dance Vault"),
]

# State Management Initialization
defaults = {
    "logged_in": False,
    "user_email": "",
    "auth_page": "login",
    "verification_code": "",
    "pending_user": {},
    "active_section": "studio",
    "breathing_active": False,
    "selected_clinic": None,
    "quote_index": 0,
    "saved_quotes": []
}

for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# Auth Flow
if not st.session_state.logged_in:
    st.markdown('<h1 class="main-title">DanceVault</h1>', unsafe_allow_html=True)
    st.markdown('<div class="script-subtitle">Dance. Track. Breathe. Stretch. Repeat.</div>', unsafe_allow_html=True)
    
    users = load_db(USER_FILE, {})
    _, center_col, _ = st.columns([1, 1.2, 1])

    with center_col:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        
        if st.session_state.auth_page == "login":
            st.markdown("<h3 style='text-align: center;'>Welcome Back</h3>", unsafe_allow_html=True)
            email = st.text_input("Vault ID (Email)", key="l_email")
            password = st.text_input("Access Key", type="password", key="l_pass")
            
            if st.button("Sign In"):
                if email in users:
                    if not users[email].get("verified", True):
                        st.error("Please verify your email address.")
                    elif users[email]["password"] == password:
                        st.session_state.logged_in = True
                        st.session_state.user_email = email
                        st.rerun()
                    else:
                        st.error("Incorrect password.")
                else:
                    st.error("Account not found.")

            if st.button("Forgot Key?"):
                st.session_state.auth_page = "reset_request"
                st.rerun()

            st.caption("New here?")
            if st.button("Sign Up"):
                st.session_state.auth_page = "signup"
                st.rerun()

        elif st.session_state.auth_page == "signup":
            st.markdown("<h3 style='text-align: center;'>Create Account</h3>", unsafe_allow_html=True)
            new_email = st.text_input("Email", key="s_email")
            new_pass = st.text_input("Password", type="password", key="s_pass")
            name = st.text_input("Name", key="s_name")
            style = st.selectbox("Primary Style", DANCE_STYLES)
            reminders = st.checkbox("Daily email reminders", value=True)

            if st.button("SEND VERIFICATION CODE"):
                if new_email and new_pass and name:
                    if new_email in users:
                        st.error("Email already registered.")
                    else:
                        code = str(random.randint(100000, 999999))
                        st.session_state.verification_code = code
                        st.session_state.pending_user = {
                            "email": new_email, "password": new_pass, "preferred_name": name,
                            "dance_style": style, "verified": False, "avatar": "🩰",
                            "email_reminders": reminders
                        }
                        if send_email(new_email, code, "verification"):
                            st.session_state.auth_page = "verify_signup"
                            st.rerun()
                else:
                    st.error("Please complete all fields.")

            if st.button("Back"):
                st.session_state.auth_page = "login"
                st.rerun()

        elif st.session_state.auth_page == "verify_signup":
            st.markdown("<h3 style='text-align: center;'>Verify Email</h3>", unsafe_allow_html=True)
            v_code = st.text_input("6-Digit Code")
            
            if st.button("VERIFY & LOGIN"):
                if v_code.strip() == st.session_state.verification_code:
                    pending = st.session_state.pending_user
                    pending["verified"] = True
                    users[pending["email"]] = pending
                    save_db(users, USER_FILE)
                    
                    send_email(pending["email"], pending["preferred_name"], action="welcome")
                    st.session_state.logged_in = True
                    st.session_state.user_email = pending["email"]
                    st.rerun()
                else:
                    st.error("Invalid code.")

        elif st.session_state.auth_page == "reset_request":
            st.markdown("<h3 style='text-align: center;'>Reset Password</h3>", unsafe_allow_html=True)
            r_email = st.text_input("Email")
            
            if st.button("SEND CODE"):
                if r_email in users:
                    code = str(random.randint(100000, 999999))
                    st.session_state.verification_code = code
                    st.session_state.user_email = r_email
                    if send_email(r_email, code, "password reset"):
                        st.session_state.auth_page = "reset_verify"
                        st.rerun()
                else:
                    st.error("Email not found.")

        elif st.session_state.auth_page == "reset_verify":
            st.markdown("<h3 style='text-align: center;'>Enter New Password</h3>", unsafe_allow_html=True)
            code = st.text_input("Code")
            new_pass = st.text_input("New Password", type="password")

            if st.button("UPDATE PASSWORD"):
                if code.strip() == st.session_state.verification_code:
                    users[st.session_state.user_email]["password"] = new_pass
                    save_db(users, USER_FILE)
                    st.success("Updated! You can now log in.")
                    st.session_state.auth_page = "login"
                    st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# Load Dashboard Data
users = load_db(USER_FILE, {})
user_profile = users.get(st.session_state.user_email, {})
vault_items = load_db(VAULT_FILE, [])

st.markdown('<h1 class="main-title">DanceVault</h1>', unsafe_allow_html=True)
st.markdown(
    f"<div class='script-subtitle'>Welcome, {user_profile.get('preferred_name', 'Dancer')} {user_profile.get('avatar', '🩰')}</div>", 
    unsafe_allow_html=True
)

# Sidebar
with st.sidebar:
    st.markdown(f"### Settings")
    st.caption(f"Account: {st.session_state.user_email}")
    
    with st.expander("Edit Profile"):
        avatar = st.selectbox("Avatar", AVATARS, index=AVATARS.index(user_profile.get("avatar", "🩰")) if user_profile.get("avatar") in AVATARS else 0)
        name = st.text_input("Name", value=user_profile.get("preferred_name", ""))
        style = st.selectbox("Style", DANCE_STYLES, index=DANCE_STYLES.index(user_profile.get("dance_style", "Other")) if user_profile.get("dance_style") in DANCE_STYLES else 0)
        reminders = st.checkbox("Reminders", value=user_profile.get("email_reminders", True))
        
        if st.button("Save Profile"):
            user_profile.update({"avatar": avatar, "preferred_name": name, "dance_style": style, "email_reminders": reminders})
            users[st.session_state.user_email] = user_profile
            save_db(users, USER_FILE)
            st.toast("Profile saved.")
            st.rerun()

    st.divider()
    if st.button("Sign Out"):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.auth_page = "login"
        st.rerun()

    if st.button("Delete Account"):
        delete_account(st.session_state.user_email)
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.auth_page = "login"
        st.rerun()

# Section Nav
cols = st.columns(4)
nav_items = [
    ("STUDIO", "studio", cols[0]),
    ("BRAIN STUDIO", "stress", cols[1]),
    ("RECOVER CLINIC", "pain", cols[2]),
    ("HELP", "how_to", cols[3])
]

for label, key, col in nav_items:
    with col:
        if st.button(label):
            st.session_state.active_section = key

st.markdown("<br>", unsafe_allow_html=True)

# Main Navigation Router
if st.session_state.active_section == "studio":
    st.markdown("<h2>Rehearsal Studio</h2>", unsafe_allow_html=True)
    
    with st.expander("Upload Rehearsal File"):
        c1, c2 = st.columns(2)
        title = c1.text_input("Title")
        date = c1.date_input("Date", datetime.now())
        media = c2.file_uploader("Media File", type=["mp4", "mov", "mp3"])

        if st.button("Save Entry"):
            if title and media:
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                ext = media.name.split(".")[-1]
                path = os.path.join(DATA_DIR, f"{ts}.{ext}")
                with open(path, "wb") as f:
                    f.write(media.getbuffer())

                vault_items.append({
                    "id": ts, "type": "choreo", "date": str(date),
                    "piece": title, "path": path, "file_type": ext,
                    "user": st.session_state.user_email
                })
                save_db(vault_items, VAULT_FILE)
                st.toast("Saved!")
                st.rerun()

    user_rehearsals = [x for x in vault_items if x.get("type") == "choreo" and x.get("user") == st.session_state.user_email]
    events = [{"id": x["id"], "title": f"{x['piece']}", "start": x["date"]} for x in user_rehearsals]
    
    cal_res = calendar(events=events, options={"headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth"}})
    
    selected_item = None
    if cal_res.get("eventClick"):
        eid = cal_res["eventClick"]["event"]["id"]
        selected_item = next((x for x in user_rehearsals if x["id"] == eid), None)

    if selected_item:
        st.markdown(f"### {selected_item['piece']}")
        if selected_item['file_type'] in ['mp4', 'mov']:
            st.video(selected_item['path'])
        else:
            st.audio(selected_item['path'])

        if st.button("Delete"):
            vault_items = delete_vault_item(selected_item['id'], vault_items)
            save_db(vault_items, VAULT_FILE)
            st.rerun()

elif st.session_state.active_section == "stress":
    st.markdown("<h2>Brain Studio</h2>", unsafe_allow_html=True)
    t1, t2, t3 = st.tabs(["Reflections", "Quotes", "Breathing"])

    with t1:
        strain = st.slider("Mental Strain", 1, 10, 5)
        notes = st.text_area("Notes")
        if st.button("Save Journal"):
            vault_items.append({
                "id": str(datetime.now().timestamp()), "type": "stress", 
                "date": str(datetime.now().date()), "stress_level": strain, 
                "notes": notes, "user": st.session_state.user_email
            })
            save_db(vault_items, VAULT_FILE)
            st.toast("Saved!")

    with t2:
        q_text, q_author = MOTIVATIONAL_QUOTES[st.session_state.quote_index % len(MOTIVATIONAL_QUOTES)]
        st.markdown(f"""
            <div class="card card-accent" style="text-align: center;">
                <h3>"{q_text}"</h3>
                <p>— {q_author}</p>
            </div>
        """, unsafe_allow_html=True)
        
        c1, c2, c3 = st.columns([1, 1, 1])
        if c1.button("Prev Quote"):
            st.session_state.quote_index -= 1
            st.rerun()
        if c2.button("Save Quote"):
            st.session_state.saved_quotes.append((q_text, q_author))
            st.toast("Saved!")
        if c3.button("Next Quote"):
            st.session_state.quote_index += 1
            st.rerun()

    with t3:
        st.caption("Guided 4-4-4-4 Box Breathing")
        if not st.session_state.breathing_active:
            if st.button("Start Session"):
                st.session_state.breathing_active = True
                st.rerun()
        else:
            if st.button("Stop"):
                st.session_state.breathing_active = False
                st.rerun()

elif st.session_state.active_section == "pain":
    st.markdown("<h2>Recover Clinic</h2>", unsafe_allow_html=True)
    
    rec_tab1, rec_tab2 = st.tabs(["Recovery Guides", "Clinic Map"])

    with rec_tab1:
        RAW_BASE = "https://raw.githubusercontent.com/aditireddybollampally-ui/dance-neuro/main"
        
        recovery_guides = {
            "Plantar Fascia (Foot)": {
                "mechanism": "High impact stamping stress, hard studio floors, and repetitive arch loading.",
                "img": f"{RAW_BASE}/4eb93dc5-a2c3-4676-929e-2d488976471f.jpeg",
                "myofascial": "Roll a frozen water bottle under the arch for 3-5 minutes daily.",
                "contrast": "Apply ice for 10-15 minutes immediately after rehearsals.",
                "posture": "Use cushioned arch support slides or orthopedic insoles between rehearsals.",
                "prevention": "Perform calf Eccentric Heel Drops off a step."
            },
            "Achilles / Calf": {
                "mechanism": "Repetitive jumps, releve overload, and sudden landing impacts.",
                "img": f"{RAW_BASE}/Agent%20Image%20-%20Design%20a%20clean%20vertical%20step-by-step%20wellness%20infographic%20matching%20the%20layout_%20typogra.png",
                "myofascial": "Use a high-density foam roller along the gastrocnemius.",
                "contrast": "Apply moist heat before class and ice post-practice.",
                "posture": "Wear supportive sneakers with a slight heel drop during non-dance hours.",
                "prevention": "Focus on controlled plié depth during landings."
            },
            "Lower Back": {
                "mechanism": "Postural holding strain and core fatigue.",
                "img": f"{RAW_BASE}/Agent%20Image%20-%20Design%20a%20clean%20vertical%20step-by-step%20wellness%20infographic%20matching%20the%20layout_%20typogra%20(1).png",
                "myofascial": "Place a soft massage ball under the gluteus medius.",
                "contrast": "Use gentle heating pads for 15 minutes before bedtime.",
                "posture": "Ensure non-dance footwear has adequate shock absorption.",
                "prevention": "Engage deep core activation during back cambré."
            }
        }

        selected_area = st.selectbox("Select Area of Tension:", list(recovery_guides.keys()))
        if selected_area:
            info = recovery_guides[selected_area]
            st.divider()
            st.markdown(f"### Focus: {selected_area}")
            st.caption(f"Context: {info['mechanism']}")
            
            col_img, col_tips = st.columns([1, 1])
            with col_img:
                st.image(info["img"], use_container_width=True)
            with col_tips:
                st.markdown(f"""
                    <div class="card card-accent">
                        <p><b>Myofascial Release:</b><br>{info['myofascial']}</p>
                        <p><b>Heat & Ice:</b><br>{info['contrast']}</p>
                        <p><b>Footwear & Posture:</b><br>{info['posture']}</p>
                        <p><b>Prevention:</b><br>{info['prevention']}</p>
                    </div>
                """, unsafe_allow_html=True)

    with rec_tab2:
        input_zip = st.text_input("Override Zipcode:", placeholder="e.g. 10003, 76201, 90210")
        lat, lon, city, state = None, None, "Detected Area", "US"

        if input_zip.strip():
            z_lat, z_lon, z_city, z_state = get_zip_coords(input_zip.strip())
            if z_lat and z_lon:
                lat, lon, city, state = z_lat, z_lon, z_city, z_state
                st.success(f"Centered on zipcode {input_zip.strip()} ({city}, {state})")

        if lat is None or lon is None:
            user_loc = get_geolocation()
            if isinstance(user_loc, dict) and "coords" in user_loc and user_loc["coords"]:
                lat = user_loc["coords"]["latitude"]
                lon = user_loc["coords"]["longitude"]
                city, state, _ = reverse_geocode(lat, lon)
            else:
                lat, lon, city, state = 40.7380, -73.9800, "New York", "NY"
                st.info("Location services unavailable. Showing default view (type a zipcode above to change location).")

        clinics = [
            {"label": str(i + 1), "lat": lat + (i * 0.003 - 0.006), "lon": lon + (i * 0.003 - 0.006), 
             "name": f"{city} Somatic Care Center #{i+1}", "phone": "(555) 019-2831"} 
            for i in range(5)
        ]
        
        df_clinics = pd.DataFrame(clinics)
        st.map(df_clinics, latitude="lat", longitude="lon", zoom=12, size=50)

        st.markdown("#### Select Clinic for Details:")
        c_cols = st.columns(len(clinics))
        for idx, clinic in enumerate(clinics):
            if c_cols[idx].button(f"{clinic['label']}"):
                st.session_state.selected_clinic = clinic

        if st.session_state.selected_clinic:
            c = st.session_state.selected_clinic
            st.markdown(f"""
                <div class="card card-accent">
                    <h4>{c['name']}</h4>
                    <p><b>Phone:</b> {c['phone']}</p>
                    <p>Specialized physical therapy and somatic performance recovery.</p>
                </div>
            """, unsafe_allow_html=True)

elif st.session_state.active_section == "how_to":
    st.markdown("<h2>User Guide</h2>", unsafe_allow_html=True)
    st.markdown("""
    * Studio: Store and track video and audio rehearsals.
    * Brain Studio: Track mental strain, save quotes, and practice guided breathing.
    * Recover Clinic: Find recovery stretching guides and sports medicine clinics.
    
    Need help? Reach us at dancevaultneuroapp@gmail.com
    """)
