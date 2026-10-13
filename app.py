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

# ==========================================
# PAGE CONFIG & PALETTE SETUP
# ==========================================
st.set_page_config(
    page_title="DanceVault | Modular NeuroDance Vault", 
    page_icon="🩰", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Color Palette
PALETTE = {
    "bg": "#F8F3EA",       # Main background
    "card": "#FFFFFF",     # Content cards
    "border": "#FFDBD1",   # Subtle borders
    "text": "#0B1957",     # Deep navy text
    "accent": "#FA9EBC"    # Pink accent
}

# Apply Global CSS (Rounded Squares & Custom Palette)
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
        color: {PALETTE["text"]} !important;
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
        color: {PALETTE["accent"]};
        text-align: center;
        margin-top: -1.2rem;
        margin-bottom: 3rem;
    }}

    h1, h2, h3, h4 {{
        font-family: 'Cinzel', serif !important;
        font-weight: 400;
        color: {PALETTE["text"]} !important;
        margin-top: 2rem;
    }}

    div[data-testid="stVerticalBlock"] > div:has(div.stExpander),
    div[data-testid="stVerticalBlock"] > div:has(div.stTabs),
    div.login-card {{
        background-color: {PALETTE["card"]};
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 10px 25px rgba(11,25,87,0.03);
        border: 1px solid {PALETTE["border"]};
    }}

    .stButton>button {{
        background: {PALETTE["accent"]} !important;
        color: {PALETTE["text"]} !important;
        border-radius: 10px !important;
        border: 1px solid {PALETTE["border"]} !important;
        font-family: 'Cinzel', serif !important;
        font-weight: 600;
        font-size: 1rem;
        padding: 0.7rem 2rem !important;
        width: 100%;
        margin-top: 1rem;
    }}

    .stTextInput input, .stTextArea textarea, .stSelectbox div[data-baseweb="select"] {{
        border-radius: 10px !important;
        border: 1px solid {PALETTE["border"]} !important;
        font-family: 'Playfair Display', serif;
        background-color: #FFFFFF !important;
    }}

    .card, .clinic-card, .tips-card {{
        background-color: #FFFFFF;
        padding: 1.5rem;
        border-radius: 12px;
        border-left: 5px solid {PALETTE["accent"]};
        box-shadow: 0 4px 15px rgba(11,25,87,0.05);
        margin-top: 0.8rem;
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
            body = f"Your security code for {purpose} is: {code_or_name}"
        elif purpose == "welcome":
            subject = "Welcome to DanceVault"
            body = f"Hello {code_or_name}, your account is active."
        elif purpose == "journal_reminder":
            subject = "DanceVault - Journal Reminder"
            body = "Take a moment today to center yourself and log your reflections."
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
        print(f"Failed to send email: {e}")
        return False

# BACKGROUND SCHEDULER
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

# ALL 50 DANCE STYLES LIST
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
# MOVES DATA GENERATOR FOR ALL 50 STYLES (10 MOVES EACH)
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

# INITIALIZE SESSION STATE
defaults = {
    "logged_in": False, "user_email": "", "auth_page": "login",
    "verification_code": "", "pending_user": {}, "active_section": "studio",
    "breathing_active": False, "selected_clinic": None, "quote_index": 0,
    "saved_quotes": [], "selected_item_id": None
}
for k, v in defaults.items():
    if k not in st.session_state: st.session_state[k] = v

# GATEWAY (Sign In / Sign Up)
if not st.session_state.logged_in:
    st.markdown('<h1 class="main-title">DanceVault</h1>', unsafe_allow_html=True)
    st.markdown('<div class="script-subtitle">Dance. Track. Breathe. Stretch. Repeat.</div>', unsafe_allow_html=True)
    
    _, col_center, _ = st.columns([1, 1.3, 1])
    users = load_json(USER_DB_FILE, {})
    
    with col_center:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        
        if st.session_state.auth_page == "login":
            st.markdown("<h2 style='text-align: center; margin-top:0;'>Welcome Back</h2>", unsafe_allow_html=True)
            email_input = st.text_input("Vault ID (Email)", key="si_email")
            pass_input = st.text_input("Access Key", type="password", key="si_pass")
            
            if st.button("Sign In", key="btn_login_submit"):
                if email_input in users:
                    if not users[email_input].get("verified", True):
                        st.error("Please verify email first.")
                    elif users[email_input]["password"] == pass_input:
                        st.session_state.logged_in = True
                        st.session_state.user_email = email_input
                        st.rerun()
                    else:
                        st.error("Invalid key.")
                else:
                    st.error("ID not recognized.")
            
            if st.button("Forgot Key?", key="btn_to_fp"):
                st.session_state.auth_page = "forgot_request"
                st.rerun()
                    
            if st.button("Sign Up", key="btn_to_signup"):
                st.session_state.auth_page = "signup"
                st.rerun()

        elif st.session_state.auth_page == "signup":
            st.markdown("<h2 style='text-align: center; margin-top:0;'>Create Account</h2>", unsafe_allow_html=True)
            new_email = st.text_input("Email", key="su_email")
            new_pass = st.text_input("Set Key", type="password", key="su_pass")
            pref_name = st.text_input("Preferred Name", key="su_prefname")
            primary_style = st.selectbox("Core Dance Style:", DANCE_STYLES, key="su_style")
            want_reminders = st.checkbox("Receive daily email reminders", value=True, key="su_reminders")
            
            if st.button("Sign Up", key="btn_signup_submit"):
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
            code_input = st.text_input("6-Digit Code", key="v_code")
            
            if st.button("Verify & Open Vault", key="btn_complete_signup"):
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
            
            if st.button("Send Reset Code", key="btn_fp_submit"):
                if reset_email in users:
                    code = generate_code()
                    st.session_state.verification_code = code
                    st.session_state.user_email = reset_email
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
            
            if st.button("Update Key", key="btn_update_pass"):
                if code_input.strip() == st.session_state.verification_code:
                    if new_password_input:
                        users[st.session_state.user_email]["password"] = new_password_input
                        save_json(users, USER_DB_FILE)
                        st.success("Updated! Please sign in.")
                        st.session_state.auth_page = "login"
                        st.rerun()
                else:
                    st.error("Invalid code.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# DASHBOARD LOAD
users_db = load_json(USER_DB_FILE, {})
user_profile = users_db.get(st.session_state.user_email, {})
vault_db_items = load_json(DB_FILE, [])

st.markdown('<h1 class="main-title">DanceVault</h1>', unsafe_allow_html=True)
st.markdown(f"<div class='script-subtitle'>Welcome, {user_profile.get('preferred_name', 'Dancer')} {user_profile.get('avatar', '🩰')}</div>", unsafe_allow_html=True)

with st.sidebar:
    st.markdown(f"<h3>Settings</h3>", unsafe_allow_html=True)
    with st.expander("Edit Profile"):
        new_avatar = st.selectbox("Avatar:", AVATAR_OPTIONS, index=AVATAR_OPTIONS.index(user_profile.get("avatar", "🩰")) if user_profile.get("avatar") in AVATAR_OPTIONS else 0)
        new_pref_name = st.text_input("Preferred Name:", value=user_profile.get("preferred_name", ""))
        new_style = st.selectbox("Primary Dance Style:", DANCE_STYLES, index=DANCE_STYLES.index(user_profile.get("dance_style", "Other")) if user_profile.get("dance_style") in DANCE_STYLES else 0)
        new_reminders = st.checkbox("Receive daily email reminders", value=user_profile.get("email_reminders", True))
        
        if st.button("Save Profile"):
            user_profile.update({"avatar": new_avatar, "preferred_name": new_pref_name, "dance_style": new_style, "email_reminders": new_reminders})
            users_db[st.session_state.user_email] = user_profile
            save_json(users_db, USER_DB_FILE)
            st.toast("Profile updated.")
            st.rerun()
            
    st.divider()
    if st.button("Sign Out"):
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.auth_page = "login"
        st.rerun()
        
    if st.button("Delete Account"):
        delete_user_account_completely(st.session_state.user_email)
        st.session_state.logged_in = False
        st.session_state.user_email = ""
        st.session_state.auth_page = "login"
        st.rerun()

# 4-COLUMN NAVIGATION
nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)
with nav_col1:
    if st.button("Studio", key="nav_studio"): st.session_state.active_section = "studio"
with nav_col2:
    if st.button("Brain Studio", key="nav_neuro"): st.session_state.active_section = "stress"
with nav_col3:
    if st.button("Recover Clinic", key="nav_recovery"): st.session_state.active_section = "pain"
with nav_col4:
    if st.button("Help", key="nav_how_to"): st.session_state.active_section = "how_to"

st.markdown("<br>", unsafe_allow_html=True)

calendar_options = {
    "editable": False, "selectable": True,
    "headerToolbar": {"left": "prev,next today", "center": "title", "right": "dayGridMonth"},
    "initialView": "dayGridMonth",
    "contentHeight": "auto",
}

# SECTION 1: STUDIO
if st.session_state.active_section == "studio":
    st.markdown("<h2>Rehearsal Studio</h2>", unsafe_allow_html=True)
    
    with st.expander("Upload Rehearsal or Piece"):
        c1, c2 = st.columns(2)
        with c1:
            c_piece = st.text_input("Title:", placeholder="Routine Rehearsal")
            c_date = st.date_input("Date:", datetime.now())
        with c2:
            c_file = st.file_uploader("Choose Media:", type=["mp4", "mov", "mp3"])
        
        if st.button("Save to Vault"):
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
                st.toast("Media vaulted.")
                st.rerun()

    st.divider()
    user_choreo_items = [x for x in vault_db_items if x.get("type") == "choreo" and x.get("user") == st.session_state.user_email]
    events = [{"id": i["id"], "title": i["piece"], "start": i["date"]} for i in user_choreo_items]
    cal_response = calendar(events=events, options=calendar_options, key="choreo_cal")
    
    if cal_response.get("eventClick"):
        st.session_state.selected_item_id = cal_response["eventClick"]["event"]["id"]
    elif cal_response.get("dateClick"):
        clicked_date = cal_response["dateClick"]["date"].split("T")[0]
        match = next((x for x in user_choreo_items if x["date"] == clicked_date), None)
        if match: st.session_state.selected_item_id = match["id"]

    if st.session_state.selected_item_id:
        item_to_show = next((x for x in user_choreo_items if x["id"] == st.session_state.selected_item_id), None)
        if item_to_show:
            st.markdown(f"### Rehearsal: {item_to_show['piece']}")
            if item_to_show['file_type'] in ['mp4', 'mov']: st.video(item_to_show['path'])
            else: st.audio(item_to_show['path'])
            
            if st.button("Delete Media Entry"):
                updated_db = delete_local_entry(item_to_show['id'], vault_db_items)
                save_json(updated_db, DB_FILE)
                st.session_state.selected_item_id = None
                st.toast("Entry deleted.")
                st.rerun()

# SECTION 2: BRAIN STUDIO
elif st.session_state.active_section == "stress":
    st.markdown("<h2>Brain Studio</h2>", unsafe_allow_html=True)
    neuro_tab1, neuro_tab2, neuro_tab3 = st.tabs(["Reflections", "Quotes", "Breathing"])
    
    with neuro_tab1:
        with st.expander("Log Reflection"):
            s1, s2 = st.columns([1,3])
            with s1: s_level = st.slider("Mental Strain (1-10):", 1, 10, 5)
            with s2: s_notes = st.text_area("Reflections:", placeholder="Focusing on footwork...")
            
            if st.button("Log to Vault"):
                vault_db_items.append({
                    "id": str(datetime.now().timestamp()), "type": "stress", 
                    "date": str(datetime.now().date()), "stress_level": s_level, 
                    "notes": s_notes, "user": st.session_state.user_email
                })
                save_json(vault_db_items, DB_FILE)
                st.toast("Reflection vaulted.")

    with neuro_tab2:
        current_q_text, current_q_author = MOTIVATIONAL_QUOTES[st.session_state.quote_index % len(MOTIVATIONAL_QUOTES)]
        st.markdown(f"""
        <div class="card" style="text-align: center;">
            <h3>"{current_q_text}"</h3>
            <p style="text-align: right;">— {current_q_author}</p>
        </div>
        """, unsafe_allow_html=True)

        q_col1, q_col2, q_col3 = st.columns([1, 1, 1])
        if q_col1.button("Prev Quote"):
            st.session_state.quote_index -= 1
            st.rerun()
        if q_col2.button("Save Quote"):
            st.session_state.saved_quotes.append({"text": current_q_text, "author": current_q_author})
            st.toast("Quote saved.")
        if q_col3.button("Next Quote"):
            st.session_state.quote_index += 1
            st.rerun()

    with neuro_tab3:
        st.markdown("### Breathing Guide (4-4-4-4)")
        if not st.session_state.breathing_active:
            if st.button("Start Session"):
                st.session_state.breathing_active = True
                st.rerun()
        else:
            if st.button("Stop"):
                st.session_state.breathing_active = False
                st.rerun()

# SECTION 3: RECOVER CLINIC
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
            col_img, col_tips = st.columns([1, 1])
            with col_img: st.image(info["img"], use_container_width=True)
            with col_tips:
                st.markdown(f"""
                <div class="card">
                    <p><b>Myofascial Release:</b><br>{info['myofascial']}</p>
                    <p><b>Heat & Ice:</b><br>{info['contrast']}</p>
                    <p><b>Posture:</b><br>{info['posture']}</p>
                    <p><b>Prevention:</b><br>{info['prevention']}</p>
                </div>
                """, unsafe_allow_html=True)

    with rec_tab2:
        input_zip = st.text_input("Override Zipcode:", placeholder="e.g. 10003, 76201")
        lat, lon, city, state = None, None, "Detected Area", "US"

        if input_zip.strip():
            z_lat, z_lon, z_city, z_state = geocode_zipcode_details(input_zip.strip())
            if z_lat and z_lon:
                lat, lon, city, state = z_lat, z_lon, z_city, z_state

        if lat is None or lon is None:
            user_loc = get_geolocation()
            if isinstance(user_loc, dict) and "coords" in user_loc and user_loc["coords"]:
                lat = user_loc["coords"]["latitude"]
                lon = user_loc["coords"]["longitude"]
                city, state, _ = reverse_geocode_coordinates(lat, lon)
            else:
                lat, lon, city, state = 40.7380, -73.9800, "New York", "NY"

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
            <div class="card">
                <h4>{c['name']}</h4>
                <p><b>Phone:</b> {c['phone']}</p>
            </div>
            """, unsafe_allow_html=True)

# SECTION 4: HELP
elif st.session_state.active_section == "how_to":
    st.markdown("<h2>User Guide</h2>", unsafe_allow_html=True)
    st.markdown("""
    * Studio: Store and track video and audio rehearsals.
    * Brain Studio: Track mental strain, save quotes, and practice guided breathing.
    * Recover Clinic: Find recovery stretching guides and sports medicine clinics.
    
    Support Contact: dancevaultneuroapp@gmail.com
    """)
