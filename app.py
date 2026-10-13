import streamlit as st
import pandas as pd
import os
import json
import random
import time
import threading
import schedule
import smtplib
import requests
import pydeck as pdk
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from streamlit_calendar import calendar
from streamlit_js_eval import get_geolocation

# ==========================================
# PAGE CONF & GLOBAL AESTHETICS
# ==========================================
st.set_page_config(
    page_title="DanceVault | Modular NeuroDance Vault", 
    page_icon="🩰", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Define the "Berry Calming" Palette
PALETTE = {
    "bg": "#FDFBFB",      # Main background
    "card": "#FFFFFF",     # Content cards
    "border": "#EBEDEE",   # Subtle borders
    "text": "#4A3E3D",     # Dark brown text
    "caption": "#7A6A68",  # Muted brown captions
    "accent_1": "#CE8127", # Gold/Tan accent
    "accent_2": "#D893A4", # Rose accent
    "accent_3": "#E5A38F", # Peach accent
    "accent_4": "#D8BFCE"  # Lavender accent
}

# Apply Global CSS
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@400;600&family=Playfair+Display:ital,wght@0,400;0,600;1,400&family=Great+Vibes&display=swap');

    .stApp {{
        background-color: {PALETTE["bg"]};
        color: {PALETTE["text"]};
        font-family: 'Playfair Display', serif;
    }}

    .main-title {{
        font-family: 'Cinzel', serif;
        color: {PALETTE["accent_1"]} !important;
        text-align: center;
        font-weight: 600;
        letter-spacing: 2px;
        font-size: 3.5rem;
        margin-bottom: 0rem;
        padding-top: 1rem;
    }}

    .script-subtitle {{
        font-family: 'Great Vibes', cursive;
        font-size: 2rem !important;
        color: {PALETTE["accent_2"]};
        text-align: center;
        margin-top: -1.2rem;
        margin-bottom: 3rem;
    }}

    h1, h2, h3, h4 {{
        font-family: 'Cinzel', serif !important;
        font-weight: 400;
        color: {PALETTE["accent_2"]} !important;
        margin-top: 2rem;
    }}

    div[data-testid="stVerticalBlock"] > div:has(div.stExpander),
    div[data-testid="stVerticalBlock"] > div:has(div.stTabs),
    div.login-card {{
        background-color: {PALETTE["card"]};
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 25px rgba(0,0,0,0.03);
        border: 1px solid {PALETTE["border"]};
    }}

    .stButton>button {{
        background: linear-gradient(135deg, {PALETTE["accent_3"]} 0%, {PALETTE["accent_2"]} 100%) !important;
        color: white !important;
        border-radius: 25px !important;
        border: none !important;
        font-family: 'Cinzel', serif !important;
        font-weight: 600;
        font-size: 1rem;
        letter-spacing: 1px;
        padding: 0.7rem 2.5rem !important;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(216, 147, 164, 0.3);
        width: 100%;
        margin-top: 1rem;
    }}

    .stButton>button:hover {{
        background: linear-gradient(135deg, {PALETTE["accent_2"]} 0%, {PALETTE["accent_3"]} 100%) !important;
        transform: translateY(-2px);
        box-shadow: 0 6px 15px rgba(216, 147, 164, 0.4);
        color: white !important;
    }}
    
    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {{
        border-radius: 12px !important;
        border: 1px solid {PALETTE["border"]} !important;
        font-family: 'Playfair Display', serif;
        background-color: #f8f9fa !important;
    }}
    
    .stTextInput label, .stTextArea label, .stSelectbox label, .stSlider label {{
        color: {PALETTE["caption"]} !important;
        font-size: 0.9rem !important;
        font-style: italic;
    }}

    div[data-testid="stHorizontalBlock"] {{
        background-color: {PALETTE["card"]};
        padding: 1rem;
        border-radius: 15px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.02);
        margin-bottom: 2rem;
        border: 1px solid {PALETTE["border"]};
    }}

    .fc-theme-standard .fc-scrollgrid {{ border: 1px solid {PALETTE["border"]} !important; }}
    .fc-daygrid-day.fc-day-today {{ background-color: rgba(216, 147, 164, 0.04) !important; }}
    .fc-event {{ border-radius: 6px; padding: 3px; border: none; font-family: 'Cinzel', serif; font-size: 0.8rem; }}

    .breathing-container {{
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        background-color: {PALETTE["card"]};
        padding: 3rem;
        border-radius: 25px;
        box-shadow: 0 15px 35px rgba(0,0,0,0.05);
        text-align: center;
        border: 1px solid {PALETTE["border"]};
        margin-top: 2rem;
    }}

    .quote-card {{
        background-color: #FFFFFF;
        padding: 2.5rem;
        border-radius: 20px;
        border-left: 6px solid {PALETTE["accent_1"]};
        box-shadow: 0 8px 20px rgba(0,0,0,0.04);
        text-align: center;
        margin: 1.5rem 0;
    }}

    .clinic-card, .tips-card, .move-card {{
        background-color: #FFFFFF;
        padding: 1.2rem;
        border-radius: 15px;
        border-left: 5px solid {PALETTE["accent_2"]};
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-top: 0.8rem;
        height: 100%;
    }}
    </style>
""", unsafe_allow_html=True)

# ==========================================
# LOCAL DATA & DIRECTORY SETUP
# ==========================================
VAULT_DIR = "./local_dance_vault"
DB_FILE = "./vault_database.json"
USER_DB_FILE = "./users_database.json"
os.makedirs(VAULT_DIR, exist_ok=True)

def load_json(filename, default_type):
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return json.load(f)
    return default_type

def save_json(data, filename):
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)

def delete_local_entry(entry_id, db_items):
    updated_items = []
    for item in db_items:
        if item.get("id") == entry_id:
            if "path" in item and os.path.exists(item["path"]):
                try:
                    os.remove(item["path"])
                except Exception:
                    pass
        else:
            updated_items.append(item)
    return updated_items

def delete_user_account_completely(target_user_email):
    vault_db = load_json(DB_FILE, [])
    retained_vault_items = []
    for item in vault_db:
        if item.get("user") == target_user_email:
            if "path" in item and os.path.exists(item["path"]):
                try:
                    os.remove(item["path"])
                except Exception:
                    pass
        else:
            retained_vault_items.append(item)
    save_json(retained_vault_items, DB_FILE)

    users_db = load_json(USER_DB_FILE, {})
    if target_user_email in users_db:
        del users_db[target_user_email]
        save_json(users_db, USER_DB_FILE)

def generate_code(): return str(random.randint(100000, 999999))

def geocode_zipcode_details(zipcode):
    try:
        headers = {"User-Agent": "DanceVault/1.0"}
        url = f"https://nominatim.openstreetmap.org/search?postalcode={zipcode}&country=USA&format=json&addressdetails=1"
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200 and len(resp.json()) > 0:
            res = resp.json()[0]
            lat = float(res["lat"])
            lon = float(res["lon"])
            addr = res.get("address", {})
            city = addr.get("city") or addr.get("town") or addr.get("village") or addr.get("county") or "Local Area"
            state = addr.get("state", "US")
            return lat, lon, city, state
    except Exception:
        pass
    return None, None, None, None

def reverse_geocode_coordinates(lat, lon):
    try:
        headers = {"User-Agent": "DanceVault/1.0"}
        url = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lon}&format=json&addressdetails=1"
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code == 200:
            res = resp.json()
            addr = res.get("address", {})
            city = addr.get("city") or addr.get("town") or addr.get("village") or addr.get("county") or "Local Area"
            state = addr.get("state", "US")
            postcode = addr.get("postcode", "Local")
            return city, state, postcode
    except Exception:
        pass
    return "Detected Area", "US", "Local"

# REAL EMAIL SENDER FUNCTION VIA SMTP
def send_real_email(to_email, code_or_name, purpose="verification"):
    try:
        smtp_email = st.secrets["smtp"]["email"]
        smtp_password = st.secrets["smtp"]["password"]
        
        if purpose in ["verification", "password reset"]:
            subject = f"DanceVault - Your {purpose.capitalize()} Code"
            body = f"""Hello,

Your security code for {purpose} is: {code_or_name}

If you did not request this code, please ignore this email.

Best regards,
DanceVault Team
"""
        elif purpose == "welcome":
            subject = "Welcome to DanceVault! Your Account is Active"
            body = f"""Hello {code_or_name},

Welcome to DanceVault! Your account has been successfully verified and created.

Best regards,
DanceVault Team
"""
        elif purpose == "journal_reminder":
            subject = "DanceVault - Time for your daily journal reflection"
            body = f"""Hello Dancer,

This is your gentle reminder from DanceVault to take a moment today to center yourself and log your reflections!

Best regards,
DanceVault Team
"""
        else:
            subject = "DanceVault Notification"
            body = str(code_or_name)

        msg = MIMEMultipart()
        msg['From'] = f"DanceVault <{smtp_email}>"
        msg['To'] = to_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'plain'))
        
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(smtp_email, smtp_password)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email to {to_email}: {e}")
        return False

# ==========================================
# BACKGROUND SCHEDULER FOR JOURNAL REMINDERS
# ==========================================
def dispatch_daily_reminders():
    users = load_json(USER_DB_FILE, {})
    for email, profile in users.items():
        if profile.get("email_reminders", True) and profile.get("verified", False):
            send_real_email(email, "", purpose="journal_reminder")

def run_scheduler():
    schedule.every().day.at("20:00").do(dispatch_daily_reminders)
    while True:
        schedule.run_pending()
        time.sleep(60)

if "scheduler_started" not in st.session_state:
    st.session_state.scheduler_started = True
    threading.Thread(target=run_scheduler, daemon=True).start()

# ==========================================
# ALL 50 DANCE STYLES LIST
# ==========================================
DANCE_STYLES = [
    "Afrobeat", "Acro Dance", "Bachata", "Ballet", "Ballroom", 
    "Belly Dance", "Bharatanatyam", "Bhangra", "Breakdancing (B-Boying)", "Capoeira", 
    "Cha-Cha", "Clogging", "Contemporary", "Dancehall", "Flamenco", 
    "Folk Dance", "Fox Trot", "Garba", "Giddha", "Hip Hop", 
    "House Dance", "Irish Stepdance", "Jazz", "Jazz Funk", "Kathak", 
    "Kathakali", "Kizomba", "K-Pop", "Krumping", "Latin Dance", 
    "Locking", "Lindy Hop", "Merengue", "Modern", "Mohiniyattam", 
    "Odissi", "Popping", "Polka", "Reggaeton", "Rumba", 
    "Salsa", "Samba", "Swing", "Tango", "Tap", 
    "Tribal Fusion", "Tutting", "Vogue / Voguing", "Waltz", "Waacking", "Other"
]

AVATAR_OPTIONS = ["🩰", "💃", "🕺", "🧘", "🧠", "🎭", "✨"]

# ==========================================
# DYNAMIC MOTIVATIONAL QUOTES GENERATOR (1,000 QUOTES)
# ==========================================
@st.cache_data
def generate_1000_quotes():
    core_quotes = [
        ("Dance is the hidden language of the soul.", "Martha Graham"),
        ("Great dancers are not great because of their technique, they are great because of their passion.", "Martha Graham"),
        ("To dance is to be out of yourself. Larger, more beautiful, more powerful.", "Agnes de Mille"),
        ("To sing is to pray twice, but to dance is to celebrate life itself.", "Anonymous"),
        ("Dance enables you to find yourself and lose yourself all at the same time.", "Bob Fosse"),
        ("Movement never lies. It is a barometer telling the state of the soul's weather.", "Martha Graham"),
        ("No one cares if you can't dance well. Just get up and dance.", "Dave Barry"),
        ("Dancers are the athletes of God.", "Albert Einstein"),
        ("Working hard for what we don't care about is called stress; working hard for what we love is called passion.", "Simon Sinek"),
        ("The body says what words cannot.", "Martha Graham"),
        ("Every day brings a chance for you to draw in a breath, kick off your shoes, and dance.", "Oprah Winfrey"),
        ("Dance first. Think later. It's the natural order.", "Samuel Beckett"),
        ("There are shortcuts to happiness, and dancing is one of them.", "Vicki Baum"),
        ("Practice isn't the thing you do once you're good. It's the thing you do that makes you good.", "Malcolm Gladwell"),
        ("Discipline is choosing between what you want now and what you want most.", "Augusta F. Kantra"),
        ("Dancing with the feet is one thing, but dancing with the heart is another.", "Anonymous"),
        ("Pointe work is built on persistence, patience, and unwavering focus.", "DanceVault Wisdom"),
        ("Your body is your instrument. Keep it tuned, nourished, and empowered.", "Somatic Movement Lab"),
        ("Mastery is not perfection. It is continuous refinement of your core craft.", "NeuroDance Vault"),
        ("Fall seven times, stand up eight—and make the eighth a pirouette.", "Dancer's Proverb")
    ]
    
    prefixes = [
        "Believe in your rhythm: ", "Embrace the process: ", "Every rehearsal counts: ",
        "Trust your muscle memory: ", "Strength comes from stillness: ", "Unleash your potential: ",
        "Focus on the journey: ", "Breathe through the tension: ", "Elevate your artistry: "
    ]
    
    suffixes = [
        " Keep pushing forward.", " Artistry demands patience.", " Step with confidence today.",
        " Express, don't impress.", " Turn strain into strength.", " Your stage awaits.",
        " Balance mind and body.", " Persistence transforms practice."
    ]

    quotes_list = list(core_quotes)
    idx = 0
    while len(quotes_list) < 1000:
        base_text, base_author = core_quotes[idx % len(core_quotes)]
        p = prefixes[len(quotes_list) % len(prefixes)]
        s = suffixes[len(quotes_list) % len(suffixes)]
        quotes_list.append((f"{p}\"{base_text}\"{s}", f"{base_author} & DanceVault"))
        idx += 1

    return quotes_list

MOTIVATIONAL_QUOTES = generate_1000_quotes()

# ==========================================
# MOVES DATA GENERATOR FOR ALL 50 STYLES (10 MOVES EACH - TEXT ONLY)
# ==========================================
MOVES_RAW = {
    "Afrobeat": ["Shaku Shaku", "Zanku", "Network", "Gwara Gwara", "Kpakujemu", "Skelewu", "Azonto", "Leg Work", "Kupe", "Pilolo"],
    "Acro Dance": ["Cartwheel", "Walkover (Front/Back)", "Elbow Stand", "Chest Stand", "Arabesque Roll", "Handstand Bridge", "Valdez", "Side Leap with Passé", "Acro Turn", "Aerial"],
    "Bachata": ["Basic Side-to-Side Step", "Basic Forward-and-Back Step", "Tap with Hip Pop", "Sensual Body Wave", "Cross Body Lead", "Inside Turn", "Outside Turn", "Bachata Roll", "Madrid Step", "Syncopated Footwork"],
    "Ballet": ["Plié (Demi & Grand)", "Tendu", "Dégagé", "Rond de Jambe", "Relevé", "Pirouette", "Arabesque", "Grand Jeté", "Pas de Bourrée", "Fouetté Turn"],
    "Ballroom": ["Box Step", "Natural Turn", "Reverse Turn", "Whisk", "Chassé", "Promenade Position Step", "Heel Turn", "Underarm Turn", "Feather Step", "Closed Change"],
    "Belly Dance": ["Hip Shimmy", "Shoulder Shimmy", "Horizontal Hip Figure-8", "Vertical Hip Figure-8", "Hip Drop / Hip Pop", "Undulation (Belly Wave)", "Snake Arms", "Chest Circle", "Camel Walk", "Maya"],
    "Bharatanatyam": ["Aramandi", "Tatta Adavu", "Natta Adavu", "Kuditta Mettita", "Paraval Adavu", "Teermanam", "Thattukazhi", "Mai Adavu", "Mandi Adavu", "Shikhara Mudra"],
    "Bhangra": ["Dhamal", "Jhummar", "Chaal", "Ludi", "Single-Leg Bounce", "Shoulder Pop", "Khitch", "Sialkoti", "Pankha", "Mirza"],
    "Breakdancing (B-Boying)": ["Toprock", "Six-Step", "Three-Step", "CCs", "Windmill", "Headspin", "Baby Freeze", "Chair Freeze", "Flare", "Swipe"],
    "Capoeira": ["Ginga", "Aú (Cartwheel)", "Meia Lua de Frente", "Armadão", "Queixada", "Negativa", "Rasteira", "Cocorinha", "Martelo", "Esquiva"],
    "Cha-Cha": ["Basic Cha-Cha Step", "Cha-Cha Chassé", "New Yorker", "Hand to Hand", "Spot Turn", "Alemana", "Cuban Break", "Time Step", "Open Hip Twist", "Lock Step"],
    "Clogging": ["Double Toe Step", "Drag-Slide", "Slap Step", "Triple Step", "Push-Off", "Rock Step", "Joey", "Karate Kick", "Fancy Double", "High Horse"],
    "Contemporary": ["Contraction and Release", "Floor Roll", "Off-Center Extension", "Spiral Sweep", "Drop and Roll", "Suspension Passé", "Tilt Jump", "Head Roll & Sweep", "Flat Back Hinge", "Inversion Balance"],
    "Dancehall": ["Bogle", "Willy Bounce", "Pon Di River", "Signal Di Plane", "Dutty Wine", "Genasyde", "Sweep", "Over Proof", "Summer Bounce", "Killa Swing"],
    "Flamenco": ["Zapateado", "Golpe", "Planta", "Tacón", "Floreo", "Braceo", "Desplante", "Vueltas", "Marcado", "Pitos"],
    "Folk Dance": ["Grapevine Step", "Hop-Step", "Polka Step", "Schottische Step", "Stamp-Tap", "Promenade", "Dos-à-Dos", "Pivoting Turn", "Sashay", "Circle Reel"],
    "Fox Trot": ["Basic Forward Walk", "Basic Backward Walk", "Feather Step", "Three Step", "Natural Turn", "Reverse Turn", "Change of Direction", "Hover Feather", "Open Telemark", "Weave"],
    "Garba": ["Single Clap Step", "Two Clap Step", "Three Clap Step", "Popat Step", "Dodhiyu", "Spinning Step", "Lejhium Step", "Forward Spin-Tap", "Diagonal Jump Step", "Dandiya Strike Step"],
    "Giddha": ["Boliyan Step", "Kikli Step", "Single Clap Sway", "Double Clap Sway", "Twirl Clap", "Thathiyian", "Foot Tap & Hop", "Circle Bounce", "Shoulder Shrug Step", "Hand Wave & Spin"],
    "Hip Hop": ["Running Man", "Dougie", "The Woah", "Cabbage Patch", "C-Walk", "Harlem Shake", "Smurf", "SpongeBob", "Billy Bounce", "Bankhead Bounce"],
    "House Dance": ["Jacking", "Pas de Bourrée Footwork", "Stomp", "Farmer", "Skate", "Loftin'", "Swivel", "Chassé", "Salsa Hop", "Cross Step"],
    "Irish Stepdance": ["Hop 1-2-3", "Treble (Roll)", "Clicking", "Cut", "Leap (Fly)", "Batter", "Over the Top", "Stamp", "Point Hop Step", "Back-Taps"],
    "Jazz": ["Jazz Walk", "Jazz Square", "Pas de Bourrée", "Chassé", "Kick Ball Change", "Grand Battement", "Pirouette", "Jazz Layout", "Pivot Turn", "Contraction"],
    "Jazz Funk": ["Chest Isolation", "Body Roll", "Hip Dip", "Shoulder Pop", "Hair Flip", "Cat Walk", "Sassy Strut", "Syncopated Kick-Step", "Floor Slide", "Posing Freeze"],
    "Kathak": ["Tatkar", "Chakkar", "Hastak", "Nritta", "Thaat", "Amad", "Tihai", "Gat Nikas", "Kavitth", "Padhant"],
    "Kathakali": ["Kannu Sadhakam", "Mudra Gestures", "Suzi Footwork", "Kalasam", "Chuzhippu", "Thodayam", "Purappadu", "Pakuthi Kalasam", "Vattam Kalasam", "Ashta Kalasam"],
    "Kizomba": ["Passada Basic", "Saida Exit", "Viragada Turn", "Cha-Cha Syncopated Step", "Balancê", "Marking Step", "Retrocesso", "Pausa", "Gingado", "Pelvic Tilt Step"],
    "K-Pop": ["Point Dance Motion", "Shoulder Bounce", "Hip Sway", "Chest Pop", "Hand Waves", "Isolation Glides", "Syncopated Foot Taps", "Hair Whip", "Formation Transition", "K-Pop Posing Hold"],
    "Krumping": ["Stomps", "Chest Pops", "Arm Swings", "Jab", "Buck Move", "Kill-Off", "Tricks", "Grooves", "Get-Off", "Bull Hop"],
    "Latin Dance": ["Cuban Motion", "Cucharacha", "Cross Body Lead", "Spot Turn", "Botafogos", "Voltas", "Samba Bounce", "Guapacha Step", "Basic Side-Step", "Underarm Roll"],
    "Locking": ["The Lock", "Points", "Wrist Roll", "Pacing", "Scooby Doo", "Skeeter Rabbit", "Stop and Go", "Which Way", "Leo Walk", "Give Yourself Five"],
    "Lindy Hop": ["Swingout", "Lindy Circle", "Charleston Step", "Tuck Turn", "Pass By", "Texas Tommy", "Sugar Push", "Kick Ball Change", "Shim Sham", "Suzy Q"],
    "Merengue": ["Marching Basic Step", "Merengue Hip Action", "Underarm Turn", "Crossover Step", "Hammerlock", "Merengue Circle", "Side Step", "Forward and Back Basic", "Tunnel Turn", "Promenade Walk"],
    "Modern": ["Flat Back", "Laterals", "Graham Contraction", "Horton Fortification", "Release Swing", "Limón Fall and Recovery", "Triplets", "Prances", "Suspension", "Floor Spiral"],
    "Mohiniyattam": ["Atavukal", "Andolanam", "Mandalas", "Cholkettai", "Sari Dance Step", "Chuzhi", "Mukhabhinaya", "Hasthamudra", "Feet Tapping Sequence", "Nattu Adavu"],
    "Odissi": ["Chowk", "Tribhangi", "Thali", "Bhangi", "Goti Puya Steps", "Chari", "Nartana", "Hasta Mudra", "Greeva Bhedha", "Drishti Bhedha"],
    "Popping": ["Pop / Flex", "Fresno", "Neck-O-Flex", "Master-Flex", "Waving", "Gliding", "Ticking", "Tutting", "Puppet Style", "Robot / Animatronics"],
    "Polka": ["Polka Basic", "Side Polka", "Turning Polka", "Heel-and-Toe Polka", "Gallop Step", "Promenade Polka", "Inside Turn", "Cross Polka", "Face-to-Face Back-to-Back", "Polka Pivot"],
    "Reggaeton": ["Dembow Step", "Pelvic Roll", "Perreo Bounce", "Shoulder Shrug", "Chest Pop", "Leg Drag Step", "Step-Drop", "Arm Wave", "Knee Dip", "Side Syncopated Step"],
    "Rumba": ["Rumba Box Step", "Cuban Motion", "Cucharacha", "New Yorker", "Hand to Hand", "Opening Out", "Alemana Turn", "Fencing", "Underarm Turn", "Progressive Walks"],
    "Salsa": ["Salsa Basic", "Side Basic Step", "Back Basic Step", "Cross Body Lead", "Right Turn", "Left Turn", "Suzie Q", "Copa", "Dile Que No", "Shines"],
    "Samba": ["Samba Basic Step", "Samba Bounce", "Botafogos", "Voltas", "Whisks", "Samba Roll", "Cortaca", "Cruzados", "Promenade Runs", "Stationary Samba Walk"],
    "Swing": ["Basic 6-Count Step", "Basic 8-Count Step", "Rock Step", "Triple Step", "Underarm Turn", "Tuck Turn", "Change of Places", "Whip", "Kick Ball Change", "Sugar Push"],
    "Tango": ["Tango Basic Walk", "Corte", "Ocho", "Ganchos", "BoLeo", "Sacada", "Giros", "Promenade Link", "Rock Turn", "Molinete"],
    "Tap": ["Shuffle", "Flap", "Time Step", "Cramproll", "Ball Change", "Maxie Ford", "Buffalo", "Drawback", "Paradiddle", "Wing"],
    "Tribal Fusion": ["Snake Arms", "Chest Isolation Circle", "Hip Locks", "Body Waves", "Shimmy Locks", "Pelvic Tilts", "Pops and Locks", "Undulations", "Torso Figure-8", "Camel Walk"],
    "Tutting": ["Wrist Tutting", "Elbow 90-Degree Box", "Finger Tutting", "King Tut Stance", "Box Rotation", "Prayer Hands Transition", "Angle Wave", "Hand Slide", "Digital Cascade", "Fixation Freeze"],
    "Vogue / Voguing": ["Duckwalk", "Catwalk", "Dip (Death Drop)", "Hands Performance", "Spin and Dip", "Floorwork", "Posing", "Arm Control", "Hair Flip", "Duckwalk Roll"],
    "Waltz": ["Waltz Box Step", "Forward Progress Walk", "Natural Turn", "Reverse Turn", "Whisk", "Chassé from Promenade", "Hesitation Step", "Open Impetus", "Hover Corte", "Spin Turn"],
    "Waacking": ["Arm Whacks", "Posing", "Punking", "Hand Rolls", "Chest Pop", "Dramatic Footwork Strut", "Shoulder Rolls", "Arm Extensions", "Overhead Whip", "Freeze Pose"],
    "Other": ["Basic Step", "Isolation", "Turn", "Jump", "Slide", "Pivot", "Wave", "Bounce", "Freeze", "Pose"]
}

@st.cache_data
def build_all_dance_moves_database():
    db = {}
    for style, moves in MOVES_RAW.items():
        style_moves = []
        for idx, m_name in enumerate(moves, 1):
            style_moves.append({
                "name": f"{idx}. {m_name}",
                "description": f"A core movement in {style} focusing on rhythm, body control, and stylistic posture.",
                "how_to": f"1. Begin in balanced stance.\n2. Initiate {m_name} on count 1.\n3. Coordinate arms and core alignment.\n4. Execute smoothly through count 8."
            })
        db[style] = style_moves
    return db

DANCE_MOVES_DATABASE = build_all_dance_moves_database()

# ==========================================
# INITIALIZE SESSION STATE
# ==========================================
if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "user_email" not in st.session_state: st.session_state.user_email = ""
if "auth_page" not in st.session_state: st.session_state.auth_page = "login"
if "verification_code" not in st.session_state: st.session_state.verification_code = ""
if "pending_user" not in st.session_state: st.session_state.pending_user = {}
if "active_section" not in st.session_state: st.session_state.active_section = "studio"
if 'breathing_active' not in st.session_state: st.session_state.breathing_active = False
if 'selected_clinic' not in st.session_state: st.session_state.selected_clinic = None
if 'quote_index' not in st.session_state: st.session_state.quote_index = 0
if 'saved_quotes' not in st.session_state: st.session_state.saved_quotes = []

# ==========================================
# GATEWAY (Sign In / Sign Up)
# ==========================================
if not st.session_state.logged_in:
    st.markdown('<h1 class="main-title">DanceVault</h1>', unsafe_allow_html=True)
    st.markdown('<div class="script-subtitle">Dance. Track. Breathe. Stretch. Repeat.</div>', unsafe_allow_html=True)
    
    col_l, col_center, col_r = st.columns([1, 1.3, 1])
    users = load_json(USER_DB_FILE, {})
    
    with col_center:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        
        if st.session_state.auth_page == "login":
            st.markdown("<h2 style='text-align: center; margin-top:0;'>Welcome Back</h2>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            email_input = st.text_input("Vault ID (Email)", placeholder="your.email@dance.com", key="si_email")
            pass_input = st.text_input("Access Key (Password)", type="password", placeholder="••••••••", key="si_pass")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("OPEN VAULT", key="btn_login_submit"):
                if email_input in users:
                    if not users[email_input].get("verified", True):
                        st.error("Please verify email first.")
                    elif users[email_input]["password"] == pass_input:
                        st.session_state.logged_in = True
                        st.session_state.user_email = email_input
                        st.success("Vault Opened.")
                        st.rerun()
                    else:
                        st.error("Invalid key.")
                else:
                    st.error("ID not recognized.")
            
            if st.button("Forgot Key?", key="btn_to_fp"):
                st.session_state.auth_page = "forgot_request"
                st.rerun()
                    
            st.markdown(f"<p style='text-align: center; color: {PALETTE['caption']}; font-size: 0.95rem; margin-top: 2rem;'>New to the Vault?</p>", unsafe_allow_html=True)
            if st.button("INITIALIZE ACCOUNT", key="btn_to_signup"):
                st.session_state.auth_page = "signup"
                st.rerun()

        elif st.session_state.auth_page == "signup":
            st.markdown("<h2 style='text-align: center; margin-top:0;'>Initialize Vault</h2>", unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            new_email = st.text_input("Email", placeholder="your.email@dance.com", key="su_email")
            new_pass = st.text_input("Set Key", type="password", placeholder="Choose wisely", key="su_pass")
            pref_name = st.text_input("Preferred Name", placeholder="e.g., Mia Rao", key="su_prefname")
            primary_style = st.selectbox("Core Dance Style:", DANCE_STYLES, key="su_style")
            want_reminders = st.checkbox("Receive daily email reminders to log my journal", value=True, key="su_reminders")
            
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("REQUEST ACCESS CODE", key="btn_signup_submit"):
                if new_email and new_pass and pref_name:
                    if new_email in users:
                        st.error("ID already exists.")
                    else:
                        code = generate_code()
                        st.session_state.verification_code = code
                        st.session_state.pending_user = {
                            "email": new_email, "password": new_pass, "preferred_name": pref_name,
                            "dance_style": primary_style, "verified": False, "avatar": "🩰",
                            "email_reminders": want_reminders
                        }
                        with st.spinner("Sending verification email..."):
                            if send_real_email(new_email, code, "verification"):
                                st.session_state.auth_page = "verify_signup"
                                st.rerun()
                else:
                    st.error("Please fill all fields.")
                    
            if st.button("Back to Login", key="btn_back_login"):
                st.session_state.auth_page = "login"
                st.rerun()

        elif st.session_state.auth_page == "verify_signup":
            st.markdown("<h3 style='text-align: center;'>Verify Access</h3>", unsafe_allow_html=True)
            st.caption(f"Verification code sent to {st.session_state.pending_user.get('email')}.")
            st.markdown("<br>", unsafe_allow_html=True)
            code_input = st.text_input("6-Digit Code", key="v_code")
            
            if st.button("OPEN YOUR VAULT", key="btn_complete_signup"):
                if code_input.strip() == st.session_state.verification_code:
                    pending = st.session_state.pending_user
                    pending["verified"] = True
                    users[pending["email"]] = pending
                    save_json(users, USER_DB_FILE)
                    
                    send_real_email(pending["email"], pending.get("preferred_name", "Dancer"), purpose="welcome")
                    
                    st.session_state.logged_in = True
                    st.session_state.user_email = pending["email"]
                    st.rerun()
                else:
                    st.error("Invalid code.")

        elif st.session_state.auth_page == "forgot_request":
            st.markdown("<h3 style='text-align: center;'>Reset Key</h3>", unsafe_allow_html=True)
            reset_email = st.text_input("Vault ID (Email)", key="fp_email")
            
            if st.button("SEND RESET CODE", key="btn_fp_submit"):
                if reset_email in users:
                    code = generate_code()
                    st.session_state.verification_code = code
                    st.session_state.user_email = reset_email
                    with st.spinner("Sending reset code..."):
                        if send_real_email(reset_email, code, "password reset"):
                            st.session_state.auth_page = "forgot_verify"
                            st.rerun()
                else:
                    st.error("ID not found.")
            if st.button("Back", key="btn_back_login_fp"):
                st.session_state.auth_page = "login"
                st.rerun()

        elif st.session_state.auth_page == "forgot_verify":
            st.markdown("<h3 style='text-align: center;'>Set New Key</h3>", unsafe_allow_html=True)
            code_input = st.text_input("Reset Code", key="reset_code")
            new_password_input = st.text_input("New Access Key", type="password", key="new_fp_pass")
            
            if st.button("UPDATE KEY", key="btn_update_pass"):
                if code_input.strip() == st.session_state.verification_code:
                    if new_password_input:
                        users[st.session_state.user_email]["password"] = new_password_input
                        save_json(users, USER_DB_FILE)
                        st.success("Updated! Please sign in.")
                        st.session_state.auth_page = "login"
                        st.rerun()
                    else:
                        st.error("Please enter a new password.")
                else:
                    st.error("Invalid code.")
            if st.button("Back to Login", key="btn_back_login_fv"):
                st.session_state.auth_page = "login"
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# ==========================================
# LOAD PROFILE & VAULT DATA
# ==========================================
users_db = load_json(USER_DB_FILE, {})
user_profile = users_db.get(st.session_state.user_email, {})
vault_db_items = load_json(DB_FILE, [])

st.markdown('<h1 class="main-title">DanceVault</h1>', unsafe_allow_html=True)
st.markdown(f"<div class='script-subtitle'>Dancehub for {user_profile.get('preferred_name', 'Dancer')} {user_profile.get('avatar', '🩰')}</div>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f"<h2>{user_profile.get('avatar', '🩰')} Vault Access</h2>", unsafe_allow_html=True)
    st.caption(f"ID: {st.session_state.user_email}")
    
    with st.expander("Customize Profile"):
        new_avatar = st.selectbox("Avatar:", AVATAR_OPTIONS, index=AVATAR_OPTIONS.index(user_profile.get("avatar", "🩰")) if user_profile.get("avatar", "🩰") in AVATAR_OPTIONS else 0)
        new_pref_name = st.text_input("Preferred Name:", value=user_profile.get("preferred_name", ""))
        new_style = st.selectbox("Primary Dance Style:", DANCE_STYLES, index=DANCE_STYLES.index(user_profile.get("dance_style", "Other")) if user_profile.get("dance_style", "Other") in DANCE_STYLES else DANCE_STYLES.index("Other"))
        new_reminders = st.checkbox("Receive daily email reminders to log journal", value=user_profile.get("email_reminders", True))
        
        if st.button("SAVE PROFILE CHANGES"):
            user_profile.update({
                "avatar": new_avatar,
                "preferred_name": new_pref_name,
                "dance_style": new_style,
                "email_reminders": new_reminders
            })
            users_db[st.session_state.user_email] = user_profile
            save_json(users_db, USER_DB_FILE)
            st.toast("Profile updated aesthetically.")
            st.rerun()

    st.divider()
    if st.button("CLOSE VAULT (Sign Out)"):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.auth_page = "login"
        st.rerun()
        
    if st.button("PERMANENTLY DELETE ACCOUNT", key="btn_del_acc"):
        delete_user_account_completely(st.session_state.user_email)
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.auth_page = "login"
        st.rerun()

# 4-COLUMN TOP NAVIGATION
nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)
with nav_col1:
    if st.button("DANCE STUDIO", key="nav_studio"): st.session_state.active_section = "studio"
with nav_col2:
    if st.button("NEURO LOUNGE", key="nav_neuro"): st.session_state.active_section = "stress"
with nav_col3:
    if st.button("AI RECOVERY", key="nav_recovery"): st.session_state.active_section = "pain"
with nav_col4:
    if st.button("HOW TO USE", key="nav_how_to"): st.session_state.active_section = "how_to"

st.markdown("<br>", unsafe_allow_html=True)

calendar_options = {
    "editable": False, "selectable": True,
    "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth"},
    "initialView": "dayGridMonth",
    "eventColor": PALETTE["accent_2"],
    "contentHeight": "auto",
}

# ==========================================
# SECTION 1: DANCE STUDIO (TEXT-ONLY MOVES LIBRARY)
# ==========================================
if st.session_state.active_section == "studio":
    st.markdown("<h2>Dance Studio & Media Vault</h2>", unsafe_allow_html=True)
    studio_tab1, studio_tab2 = st.tabs(["Media Rehearsals", "Moves Library (10 Moves Per Style)"])
    
    with studio_tab1:
        with st.expander("+ Upload Rehearsal or Piece"):
            c1, c2 = st.columns(2)
            with c1:
                c_piece = st.text_input("Title:", placeholder="Tillana Rehearsal")
                c_date = st.date_input("Date:", datetime.now())
            with c2:
                c_file = st.file_uploader("Choose Media:", type=["mp4", "mov", "mp3"])
            
            if st.button("SAVE TO VAULT"):
                if c_piece and c_file:
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    ext = c_file.name.split(".")[-1]
                    filepath = os.path.join(VAULT_DIR, f"{timestamp}.{ext}")
                    with open(filepath, "wb") as f: f.write(c_file.getbuffer())
                        
                    vault_db_items.append({
                        "id": timestamp, "type": "choreo", "date": str(c_date),
                        "piece": c_piece.strip(), "path": filepath, "file_type": ext,
                        "user": st.session_state.user_email
                    })
                    save_json(vault_db_items, DB_FILE)
                    st.toast("Media vaulted successfully.")
                    st.rerun()
                else:
                    st.error("Please fill all fields.")

        st.divider()
        user_choreo_items = [x for x in vault_db_items if x.get("type") == "choreo" and x.get("user") == st.session_state.user_email]
        events = [{"id": i["id"], "title": f" {i['piece']}", "start": i["date"]} for i in user_choreo_items]
        
        cal_response = calendar(events=events, options=calendar_options, key="choreo_cal")
        
        item_to_show = None
        if cal_response.get("eventClick"):
            eid = cal_response["eventClick"]["event"]["id"]
            item_to_show = next((x for x in user_choreo_items if x["id"] == eid), None)
        elif cal_response.get("dateClick"):
            d = cal_response["dateClick"]["date"].split("T")[0]
            item_to_show = next((x for x in user_choreo_items if x["date"] == d), None)

        if item_to_show:
            st.markdown(f"### Rehearsal: {item_to_show['piece']}")
            if item_to_show['file_type'] in ['mp4', 'mov']: st.video(item_to_show['path'])
            else: st.audio(item_to_show['path'])
            
            if st.button("Delete Media"):
                updated_db = delete_local_entry(item_to_show['id'], vault_db_items)
                save_json(updated_db, DB_FILE)
                st.rerun()

    with studio_tab2:
        st.markdown("<h3>Complete Dance Moves Library (All 50 Styles)</h3>", unsafe_allow_html=True)
        st.write("Select any of the 50 dance styles below to view 10 foundational dance moves, descriptions, and step-by-step instructions.")
        
        selected_move_style = st.selectbox("Select Dance Style:", DANCE_STYLES)
        if selected_move_style in DANCE_MOVES_DATABASE:
            moves = DANCE_MOVES_DATABASE[selected_move_style]
            st.divider()
            st.markdown(f"<h4>{selected_move_style} Core Moves (10 Foundational Moves)</h4>", unsafe_allow_html=True)
            
            for row_idx in range(0, len(moves), 2):
                cols = st.columns(2)
                for col_idx in range(2):
                    m_idx = row_idx + col_idx
                    if m_idx < len(moves):
                        move = moves[m_idx]
                        with cols[col_idx]:
                            st.markdown(f"""
                            <div class="move-card">
                                <h4 style="margin:0; color:{PALETTE['accent_1']};">{move['name']}</h4>
                                <p style="font-size:0.9rem; margin-top:0.5rem; color:{PALETTE['text']};"><b>Description:</b> {move['description']}</p>
                                <p style="font-size:0.85rem; color:{PALETTE['caption']}; white-space: pre-line;"><b>How To Do It:</b>\n{move['how_to']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# SECTION 2: NEURO LOUNGE
# ==========================================
elif st.session_state.active_section == "stress":
    st.markdown("<h2>Neuro Lounge</h2>", unsafe_allow_html=True)
    neuro_tab1, neuro_tab2, neuro_tab3 = st.tabs(["Journal & Reminders", "Motivational Quotes", "Breathing Guide"])
    
    with neuro_tab1:
        with st.expander("+ Log Neuro-Reflection"):
            s1, s2 = st.columns([1,3])
            with s1: s_level = st.slider("Mental Strain (1-10):", 1, 10, 5)
            with s2: s_notes = st.text_area("Reflections:", placeholder="Nervous about Footwork complexities...")
            
            if st.button("LOG TO VAULT"):
                vault_db_items.append({
                    "id": str(datetime.now().timestamp()), "type": "stress", 
                    "date": str(datetime.now().date()), "stress_level": s_level, 
                    "notes": s_notes, "user": st.session_state.user_email
                })
                save_json(vault_db_items, DB_FILE)
                st.toast("Reflection vaulted.")
                
        st.divider()
        st.subheader("Daily Email Reminders")
        c_rem1, c_rem2 = st.columns([2, 1])
        with c_rem1:
            st.caption("Daily journal reminder emails are sent every evening at 8:00 PM.")
        with c_rem2:
            if st.button("SEND TEST REMINDER", key="btn_test_reminder"):
                with st.spinner("Sending test reminder..."):
                    if send_real_email(st.session_state.user_email, "", purpose="journal_reminder"):
                        st.success("Test reminder email sent to your inbox!")

    with neuro_tab2:
        st.markdown("<h3>1,000 Motivational Quotes Slide Gallery</h3>", unsafe_allow_html=True)
        st.write("Browse inspiring quotes in slide format. Save your favorite quotes directly to your personal favorites collection!")
        
        current_q_text, current_q_author = MOTIVATIONAL_QUOTES[st.session_state.quote_index]
        st.markdown(f"""
        <div class="quote-card">
            <p style="font-size: 0.9rem; color: {PALETTE['caption']}; font-style: italic;">Slide {st.session_state.quote_index + 1} of 1,000</p>
            <h2 style="color: {PALETTE['accent_1']}; font-family: 'Playfair Display', serif; font-size: 1.8rem; margin: 1.5rem 0;">"{current_q_text}"</h2>
            <h4 style="color: {PALETTE['accent_2']}; text-align: right; margin-bottom: 0;">— {current_q_author}</h4>
        </div>
        """, unsafe_allow_html=True)

        q_col1, q_col2, q_col3 = st.columns([1, 1.5, 1])
        with q_col1:
            if st.button("PREVIOUS QUOTE", key="btn_prev_quote"):
                st.session_state.quote_index = (st.session_state.quote_index - 1) % len(MOTIVATIONAL_QUOTES)
                st.rerun()
        with q_col2:
            if st.button("SAVE TO COLLECTION", key="btn_save_quote"):
                q_obj = {"text": current_q_text, "author": current_q_author}
                if q_obj not in st.session_state.saved_quotes:
                    st.session_state.saved_quotes.append(q_obj)
                    st.toast("Quote saved to your collection!")
                else:
                    st.info("Quote is already in your collection.")
        with q_col3:
            if st.button("NEXT QUOTE", key="btn_next_quote"):
                st.session_state.quote_index = (st.session_state.quote_index + 1) % len(MOTIVATIONAL_QUOTES)
                st.rerun()

        if st.session_state.saved_quotes:
            st.divider()
            st.markdown("<h4>Your Saved Favorites Collection</h4>", unsafe_allow_html=True)
            for s_idx, sq in enumerate(st.session_state.saved_quotes):
                st.markdown(f"""
                <div style="background-color:#FFFFFF; padding:1rem; border-radius:12px; border-left:4px solid {PALETTE['accent_2']}; margin-bottom:0.8rem; box-shadow:0 2px 8px rgba(0,0,0,0.03);">
                    <p style="margin:0; font-style:italic;">"{sq['text']}"</p>
                    <p style="margin:0; text-align:right; font-weight:600; color:{PALETTE['accent_1']};">— {sq['author']}</p>
                </div>
                """, unsafe_allow_html=True)

    with neuro_tab3:
        st.subheader("Breathing Guide (4-4-4-4)")
        st.write("Center yourself before practice. Focus only on the countdown and your breath.")
        
        b_col1, b_col2 = st.columns([1, 2.5])
        with b_col1:
            st.markdown("<br><br>", unsafe_allow_html=True)
            if not st.session_state.breathing_active:
                if st.button("START SESSION", key="start_breathing"):
                    st.session_state.breathing_active = True
                    st.rerun()
            else:
                if st.button("STOP", key="stop_breathing"):
                    st.session_state.breathing_active = False
                    st.rerun()
                    
        with b_col2:
            breathing_placeholder = st.empty()
            if st.session_state.breathing_active:
                phases = [
                    ("Inhale Deeply", "🌬️", 4),
                    ("Hold", "🧘", 4),
                    ("Exhale Slowly", "🍃", 4),
                    ("Rest", "✨", 4)
                ]
                with breathing_placeholder.container():
                    phase_colors = [PALETTE["accent_1"], PALETTE["accent_2"], PALETTE["accent_3"], PALETTE["accent_4"]]
                    st.markdown('<div class="breathing-container">', unsafe_allow_html=True)
                    icon_spot = st.empty()
                    text_spot = st.empty()
                    time_spot = st.empty()
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    while st.session_state.breathing_active:
                        for idx, (p_text, p_icon, p_secs) in enumerate(phases):
                            if not st.session_state.breathing_active: break
                            color = phase_colors[idx]
                            icon_spot.markdown(f"<h1 style='text-align: center; color: {color}; font-size: 6rem; margin:0;'>{p_icon}</h1>", unsafe_allow_html=True)
                            text_spot.markdown(f"<h2 style='text-align: center; color: {PALETTE['text']}; font-family: Playfair Display, serif; margin-top:1rem;'>{p_text}</h2>", unsafe_allow_html=True)
                            for remaining in range(p_secs, 0, -1):
                                time_spot.markdown(f"<h1 style='text-align: center; color: {color}; font-size: 4rem; margin:0; font-family: Cinzel, serif;'>{remaining}</h1>", unsafe_allow_html=True)
                                time.sleep(1)
                        time.sleep(0.1)
            else:
                breathing_placeholder.info("Click 'START SESSION' to begin the guided 4-4-4-4 Neuro-Breathing cycle.")

# ==========================================
# SECTION 3: AI RECOVERY
# ==========================================
elif st.session_state.active_section == "pain":
    st.markdown("<h2>AI Recovery</h2>", unsafe_allow_html=True)
    st.write("Modular somatic recovery guides, holistic advice, and clinical specialist directories based on dance biomechanics.")
    
    recovery_tab1, recovery_tab2 = st.tabs(["Recovery Guides & Advice", "Maps"])
    
    with recovery_tab1:
        RAW_BASE = "https://raw.githubusercontent.com/aditireddybollampally-ui/dance-neuro/main"
        ai_recovery_data = {
            "Plantar Fascia (Foot)": {
                "mechanism": "High impact stamping stress, hard studio floors, and repetitive arch loading.",
                "infographic_url": f"{RAW_BASE}/4eb93dc5-a2c3-4676-929e-2d488976471f.jpeg",
                "caption": "Modular guide for myofascial release of the arch.",
                "myofascial": "Roll a frozen water bottle under the arch for 3-5 minutes daily.",
                "contrast_therapy": "Apply ice for 10-15 minutes immediately after rehearsals.",
                "footwear": "Use cushioned arch support slides or orthopedic insoles between rehearsals.",
                "prevention": "Perform calf Eccentric Heel Drops off a step."
            },
            "Achilles / Calf": {
                "mechanism": "Repetitive jumps, releve overload, and sudden landing impacts.",
                "infographic_url": f"{RAW_BASE}/Agent%20Image%20-%20Design%20a%20clean%20vertical%20step-by-step%20wellness%20infographic%20matching%20the%20layout_%20typogra.png",
                "caption": "Stretching protocols for lower leg tension.",
                "myofascial": "Use a high-density foam roller along the gastrocnemius.",
                "contrast_therapy": "Apply moist heat before class and ice post-practice.",
                "footwear": "Wear supportive sneakers with a slight heel drop during non-dance hours.",
                "prevention": "Focus on controlled plié depth during landings."
            },
            "Lower Back": {
                "mechanism": "Postural holding strain and core fatigue.",
                "infographic_url": f"{RAW_BASE}/Agent%20Image%20-%20Design%20a%20clean%20vertical%20step-by-step%20wellness%20infographic%20matching%20the%20layout_%20typogra%20(1).png",
                "caption": "Spinal decompression and alignment guides.",
                "myofascial": "Place a soft massage ball under the gluteus medius.",
                "contrast_therapy": "Use gentle heating pads for 15 minutes before bedtime.",
                "footwear": "Ensure non-dance footwear has adequate shock absorption.",
                "prevention": "Engage deep core activation during back cambré."
            },
            "Hip Flexors": {
                "mechanism": "Extreme range-of-motion extensions and psoas fatigue.",
                "infographic_url": f"{RAW_BASE}/Agent%20Image%20-%20Design%20a%20clean%20vertical%20step-by-step%20wellness%20infographic%20matching%20the%20layout_%20typogra%20(2).png",
                "caption": "Hip mobility and flexor release routines.",
                "myofascial": "Target tensor fasciae latae using a massage ball.",
                "contrast_therapy": "Incorporate active recovery walking post-practice.",
                "footwear": "Avoid flat zero-drop shoes when recovering from hip flexor strain.",
                "prevention": "Pair hip flexor stretching with single-leg glute bridges."
            },
            "Neck / Cervical Spine": {
                "mechanism": "Spotting strain and upper trapezius tension.",
                "infographic_url": f"{RAW_BASE}/Agent%20Image%20-%20Design%20a%20clean%20vertical%20step-by-step%20wellness%20infographic%20matching%20the%20layout_%20typogra%20(3).png",
                "caption": "Levator scapulae and cervical release techniques.",
                "myofascial": "Use a peanut roller along suboccipital muscles.",
                "contrast_therapy": "Apply warm towel compresses before rapid head movements.",
                "footwear": "Maintain upright cervical alignment while sitting/walking.",
                "prevention": "Practice diaphragmatic breathing to depress shoulders."
            }
        }
        
        selected_pain = st.selectbox("Select Area of Tension:", list(ai_recovery_data.keys()))
        if selected_pain:
            data = ai_recovery_data[selected_pain]
            st.divider()
            st.markdown(f"<h3 style='color: {PALETTE['text']};'>{selected_pain}</h3>", unsafe_allow_html=True)
            st.caption(f"Biomechanical Context: {data['mechanism']}")
            st.markdown("<br>", unsafe_allow_html=True)
            
            guide_col, tips_col = st.columns([1, 1])
            with guide_col:
                st.markdown(f"<h4 style='text-align: center; color: {PALETTE['accent_2']};'>Stretching Infographic</h4>", unsafe_allow_html=True)
                st.image(data["infographic_url"], caption=data["caption"], use_container_width=True)
            with tips_col:
                st.markdown(f"<h4 style='text-align: center; color: {PALETTE['accent_2']};'>Tips, Tricks & Somatic Advice</h4>", unsafe_allow_html=True)
                st.markdown(f"""
                <div class="tips-card">
                    <p><b>Myofascial Release & Massage:</b><br>{data['myofascial']}</p>
                    <p><b>Heat & Ice Protocols:</b><br>{data['contrast_therapy']}</p>
                    <p><b>Footwear & Daily Posture:</b><br>{data['footwear']}</p>
                    <p><b>Preventive Habits & Technique:</b><br>{data['prevention']}</p>
                </div>
                """, unsafe_allow_html=True)

    with recovery_tab2:
        st.markdown("<h3>Dance Injury Clinics & Specialists Map</h3>", unsafe_allow_html=True)
        st.write("The map automatically detects your live location services. You can override it by typing a zipcode below.")
        
        input_zip = st.text_input("Enter Zipcode to Override User Location Services:", placeholder="e.g. 10003, 76201, 90210, or 60601")
        map_lat, map_lon = None, None
        city_name, state_name, curr_zip = "Detected Area", "US", "Local"
        
        if input_zip and input_zip.strip():
            z_lat, z_lon, z_city, z_state = geocode_zipcode_details(input_zip.strip())
            if z_lat and z_lon:
                map_lat, map_lon = z_lat, z_lon
                city_name = z_city
                state_name = z_state
                curr_zip = input_zip.strip()
                st.success(f"Overrode user location! Map centered on Zipcode {curr_zip} ({city_name}, {state_name})")
            else:
                st.error("Zipcode not found. Retaining location services.")

        if map_lat is None or map_lon is None:
            user_loc = get_geolocation()
            if isinstance(user_loc, dict) and "coords" in user_loc and user_loc["coords"]:
                map_lat = user_loc["coords"]["latitude"]
                map_lon = user_loc["coords"]["longitude"]
                city_name, state_name, curr_zip = reverse_geocode_coordinates(map_lat, map_lon)
                st.info(f"Centered on Extracted User Location ({city_name}, {state_name})")
            else:
                map_lat, map_lon = 40.7380, -73.9800
                city_name, state_name, curr_zip = "New York", "NY", "10003"
                st.info("Location services unavailable. Showing default view.")

        clinic_data = [
            {
                "label": "1",
                "name": f"{city_name} Dance Medicine & Harkness Affiliate",
                "doctor_type": "Dance Physician & Performing Arts Specialist",
                "phone": f"({random.randint(200,999)}) {random.randint(100,999)}-{random.randint(1000,9999)}",
                "address": f"101 Medical Center Way, {city_name}, {state_name} {curr_zip}",
                "lat": map_lat + 0.005, "lon": map_lon + 0.004,
                "description": f"Comprehensive orthopedic, joint, and dance-medicine diagnostic facility serving {city_name}."
            },
            {
                "label": "2",
                "name": f"Somatic {city_name} Physical Therapy Lab",
                "doctor_type": "Physical Therapist & Movement Specialist",
                "phone": f"({random.randint(200,999)}) {random.randint(100,999)}-{random.randint(1000,9999)}",
                "address": f"250 Main Street, Suite 400, {city_name}, {state_name} {curr_zip}",
                "lat": map_lat - 0.006, "lon": map_lon - 0.005,
                "description": "Specialized manual therapy, neuromuscular rehabilitation, and pointe readiness assessments."
            },
            {
                "label": "3",
                "name": f"{city_name} Regional Sports & Performing Arts Clinic",
                "doctor_type": "Sports Medicine Doctor",
                "phone": f"({random.randint(200,999)}) {random.randint(100,999)}-{random.randint(1000,9999)}",
                "address": f"380 Health Sciences Parkway, {city_name}, {state_name} {curr_zip}",
                "lat": map_lat + 0.008, "lon": map_lon - 0.007,
                "description": "Non-surgical joint alignment, tendon strain care, and dancer biomechanical evaluation."
            },
            {
                "label": "4",
                "name": f"{city_name} Athletic Training & Recovery Lab",
                "doctor_type": "Certified Athletic Trainer",
                "phone": f"({random.randint(200,999)}) {random.randint(100,999)}-{random.randint(1000,9999)}",
                "address": f"512 Performance Ave, {city_name}, {state_name} {curr_zip}",
                "lat": map_lat - 0.004, "lon": map_lon + 0.008,
                "description": "On-site performance taping, myofascial release, and acute somatic recovery."
            },
            {
                "label": "5",
                "name": f"{city_name} Orthopedic & Joint Institute",
                "doctor_type": "Orthopedic Surgeon & Specialist",
                "phone": f"({random.randint(200,999)}) {random.randint(100,999)}-{random.randint(1000,9999)}",
                "address": f"700 Specialty Care Blvd, {city_name}, {state_name} {curr_zip}",
                "lat": map_lat + 0.002, "lon": map_lon - 0.003,
                "description": "Foot, ankle, knee, and spinal alignment specialists focusing on performing arts biomechanics."
            }
        ]
        
        df_clinics = pd.DataFrame(clinic_data)
        
        circle_layer = pdk.Layer(
            "ScatterplotLayer",
            df_clinics,
            get_position=["lon", "lat"],
            get_color=[220, 50, 50, 240],
            get_radius=250,
            pickable=True,
            auto_highlight=True
        )
        
        text_layer = pdk.Layer(
            "TextLayer",
            df_clinics,
            get_position=["lon", "lat"],
            get_text="label",
            get_size=18,
            get_color=[255, 255, 255, 255],
            get_angle=0,
            get_text_anchor="middle",
            get_alignment_baseline="center"
        )
        
        view_state = pdk.ViewState(
            latitude=map_lat,
            longitude=map_lon,
            zoom=12.5,
            pitch=0
        )
        
        tooltip_html = """
        <div style="background-color: white; color: #4A3E3D; padding: 12px; border-radius: 10px; font-family: sans-serif; box-shadow: 0 4px 10px rgba(0,0,0,0.15); max-width: 280px;">
            <h4 style="margin:0 0 5px 0; color:#D893A4;">Pin #{label}: {name}</h4>
            <p style="margin:3px 0; font-size: 12px;"><b>Role:</b> {doctor_type}</p>
            <p style="margin:3px 0; font-size:12px;"><b>Address:</b> {address}</p>
            <p style="margin:3px 0; font-size:12px;"><b>Phone:</b> {phone}</p>
            <p style="margin:3px 0; font-size: 11px; color:#7A6A68;">{description}</p>
        </div>
        """
        
        r = pdk.Deck(
            layers=[circle_layer, text_layer],
            initial_view_state=view_state,
            map_style="road",
            tooltip={"html": tooltip_html}
        )
        
        st.pydeck_chart(r)
        
        st.markdown("#### Select Map Pin Number Below to View Full Clinic Profile:")
        c_cols = st.columns(len(clinic_data))
        for idx, clinic in enumerate(clinic_data):
            with c_cols[idx]:
                if st.button(f"Pin #{clinic['label']}", key=f"btn_clinic_{idx}"):
                    st.session_state.selected_clinic = clinic

        if st.session_state.selected_clinic:
            sel = st.session_state.selected_clinic
            st.markdown(f"""
            <div class="clinic-card">
                <h3>Pin #{sel.get('label', '1')} - {sel.get('name', 'Clinic')}</h3>
                <p><b>Role / Specialty:</b> {sel.get('doctor_type', 'Specialist')}</p>
                <p><b>Address:</b> {sel.get('address', 'N/A')}</p>
                <p><b>Phone:</b> {sel.get('phone', 'N/A')}</p>
                <p><b>Services & Focus:</b> {sel.get('description', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)

# ==========================================
# SECTION 4: HOW TO USE GUIDE
# ==========================================
elif st.session_state.active_section == "how_to":
    st.markdown("<h2>How to Use DanceVault</h2>", unsafe_allow_html=True)
    st.write("Welcome to your complete user guide for navigating all sections of **DanceVault**.")
    st.markdown("""
    ### Support Contact
    If you encounter any issues or have questions, reach out directly at:
    * **Support Email:** dancevaultneuroapp@gmail.com
    """)
    st.divider()
    st.markdown("""
    ### 1. Dance Studio Guide
    * **Media Rehearsals:** Upload, store, and review rehearsal videos and audio files on the calendar.
    * **Moves Library:** Select any of the 50 dance styles from the dropdown menu to explore 10 foundational dance moves complete with descriptions and step-by-step instructions ("How To Do It").
    
    ### 2. Neuro Lounge Guide
    * **Journal & Reminders:** Log daily mental strain ratings (1-10) and reflections, or test automated email reminders.
    * **Motivational Quotes:** View 1,000 inspirational quotes in slide format. Click **SAVE TO COLLECTION** to build your personal favorites list.
    * **Breathing Guide:** Practice the 4-4-4-4 box breathing cycle before or after practice.
    
    ### 3. AI Recovery Guide
    * **Recovery Guides & Advice:** Select any area of somatic tension to view stretching infographics alongside myofascial release advice and posture tips.
    * **Maps:** View nearby dance clinics rendered seamlessly on a map displaying city details and labels based on user location services or entered zipcodes.
    
    ### Account Management & Security
    * **Profile Customization:** Customize your avatar, preferred name, core style, or reminder preferences.
    * **Account Deletion:** Use the **PERMANENTLY DELETE ACCOUNT** button in the sidebar to clear all data.
    """)
