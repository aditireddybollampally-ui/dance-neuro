import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="NeuroDance & Recovery Vault", page_icon="🧠", layout="wide")

VAULT_DIR = "./local_dance_vault"
DB_FILE = "./vault_database.json"
os.makedirs(VAULT_DIR, exist_ok=True)

def load_db():
    if os.path.exists(DB_FILE):
        with open(DB_FILE, "r") as f:
            return json.load(f)
    return []

def save_db(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

st.title("🧠 NeuroDance: Biomechanical & Mental Recovery Vault")
st.markdown("*A localized edge-computing web tool designed to track somatic stress, organize rehearsal media offline, and deliver automated neuromuscular recovery protocols for dancers.*")

tab1, tab2, tab3 = st.tabs(["📁 Local Media Vault & Logger", "📊 Repertoire & Song Catalog", "🧬 AI Neuro-Recovery Engine"])

# ==========================================
# TAB 1: LOGGING & LOCAL FILE STORAGE
# ==========================================
with tab1:
    st.header("Session Logging & Offline Video Storage")
    
    col1, col2 = st.columns(2)
    with col1:
        dance_style = st.selectbox("Discipline:", ["Bharathanatyam", "Ballet", "Contemporary", "Hip Hop", "Kathak", "Other"])
        piece_title = st.text_input("Piece / Song Title:", placeholder="e.g., Varnam, Swan Lake Variation")
        session_date = st.date_input("Practice Date:", datetime.now())
    with col2:
        mental_load = st.slider("Cognitive / Performance Stress (1-10):", 1, 10, 5)
        somatic_pain = st.multiselect("Localized Physical Pain / Strain:", [
            "Plantar Fascia / Arch", "Achilles / Calf", "Lumbar Spine (Lower Back)", 
            "Hip Flexors / Hamstrings", "Cervical Spine / Neck & Shoulders"
        ])
        notes = st.text_area("Choreography Notes / Mental State:")

    media_file = st.file_uploader("Upload Rehearsal Video/Audio (Saved locally to bypass cloud limits):", type=["mp4", "mov", "avi", "mp3"])

    if st.button("Commit to Local Vault 💾"):
        if piece_title and media_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            ext = media_file.name.split(".")[-1]
            filename = f"{timestamp}_{piece_title.replace(' ', '_')}.{ext}"
            filepath = os.path.join(VAULT_DIR, filename)
            
            # Save bytes directly to local directory
            with open(filepath, "wb") as f:
                f.write(media_file.getbuffer())
                
            db = load_db()
            db.append({
                "timestamp": timestamp,
                "date": str(session_date),
                "style": dance_style,
                "piece": piece_title.strip(),
                "stress": mental_load,
                "pain": somatic_pain,
                "notes": notes,
                "path": filepath,
                "type": ext
            })
            save_db(db)
            st.success(f"Successfully cached clip locally under piece: '{piece_title}'")
        else:
            st.error("Please provide a Piece Title and upload a media file.")

# ==========================================
# TAB 2: MULTI-INDEX CATALOGING
# ==========================================
with tab2:
    st.header("🗂️ Multi-Index Repertoire Catalog")
    db = load_db()
    
    if not db:
        st.info("Vault is empty. Log a session in Tab 1.")
    else:
        df = pd.DataFrame(db)
        view_mode = st.radio("Organize Archive By:", ["Group by Song / Piece Name", "Chronological Timeline"], horizontal=True)
        
        if view_mode == "Group by Song / Piece Name":
            selected_piece = st.selectbox("Select Piece:", df["piece"].unique())
            piece_subset = df[df["piece"] == selected_piece]
            st.subheader(f"Accessing {len(piece_subset)} recorded iterations of '{selected_piece}'")
            
            for _, row in piece_subset.iterrows():
                with st.expander(f"📅 Date: {row['date']} | Stress Index: {row['stress']}/10"):
                    st.write(f"**Notes:** {row['notes']}")
                    if row['pain']:
                        st.markdown(f"⚠️ **Reported Strain:** {', '.join(row['pain'])}")
                    if row['type'] in ['mp4', 'mov', 'avi']:
                        st.video(row['path'])
                    else:
                        st.audio(row['path'])
        else:
            df_sorted = df.sort_values(by="date", ascending=False)
            for _, row in df_sorted.iterrows():
                with st.expander(f"🎵 {row['piece']} — {row['date']} ({row['style']})"):
                    st.write(f"**Stress Level:** {row['stress']} | **Pain Areas:** {row['pain']}")
                    if row['type'] in ['mp4', 'mov', 'avi']:
                        st.video(row['path'])

# ==========================================
# TAB 3: AI PAIN-TARGETED RECOVERY ENGINE
# ==========================================
with tab3:
    st.header("🧬 AI-Driven Neuromuscular Stretch Protocol")
    st.write("Dynamic recommendation matrix based on somatic pain inputs and cognitive stress indexes.")
    
    # AI logic mapping pain points to neuro-rehab routines
    ai_recommendations = {
        "Plantar Fascia / Arch": {
            "mechanism": "High impact shock absorption stress (common in classical foot-stamping like Bharathanatyam Aramandi/Mandai stings).",
            "protocol": "1. Myofascial release using a lacrosse ball under the medial longitudinal arch (2 mins).\n2. Eccentric calf drops to unload insertion points."
        },
        "Achilles / Calf": {
            "mechanism": "Repetitive rebound acceleration and plantarflexion overload.",
            "protocol": "1. Soleus-focused bent-knee wall stretches.\n2. Dynamic ankle dorsiflexion mobility drills."
        },
        "Lumbar Spine (Lower Back)": {
            "mechanism": "Compensatory extension strain during postural alignment or core fatigue.",
            "protocol": "1. Cat-Camel spinal articulation to reset proprioception.\n2. Dead-bug core stabilization activation to unload lumbar extensors."
        },
        "Hip Flexors / Hamstrings": {
            "mechanism": "Extreme range-of-motion holding under neuromuscular tension.",
            "protocol": "1. 90/90 hip transitions for internal/external rotation.\n2. PNF contract-relax stretching for hamstrings."
        },
        "Cervical Spine / Neck & Shoulders": {
            "mechanism": "Sympathetic nervous system elevation ('fight-or-flight' performance anxiety translation into upper trapezius tension).",
            "protocol": "1. Vagus nerve stimulation: 4-7-8 diaphragmatic breathing block.\n2. Scapular retraction and thoracic spine foam rolling."
        }
    }
    
    selected_issues = st.multiselect("Select active strain areas for real-time recovery synthesis:", list(ai_recommendations.keys()))
    
    if st.button("Generate Personalized Protocol ⚙️"):
        if not selected_issues:
            st.info("Please select at least one strain area above.")
        else:
            for issue in selected_issues:
                data = ai_recommendations[issue]
                st.markdown(f"### 🎯 Target System: {issue}")
                st.info(f"**Biomechanical Analysis:** {data['mechanism']}")
                st.success(f"**Prescribed Action Protocol:**\n{data['protocol']}")
                st.divider()
