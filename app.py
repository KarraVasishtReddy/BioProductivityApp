import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import random
from PIL import Image
from datetime import datetime

# --- 1. DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('oxidate_kids_pro.db')
    c = conn.cursor()
    # Users: added 'hero_name' and 'pet_level'
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, email TEXT, 
                  allergies TEXT, badge TEXT, hero_name TEXT, pet_level INTEGER)''')
    c.execute('''CREATE TABLE IF NOT EXISTS history 
                 (username TEXT, food TEXT, grams REAL, impact REAL, calories REAL, time TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

# --- 2. MEDINDIA AI VISION ENGINE ---
def get_redox_data(food_name):
    kb = {
        "turmeric": {"cal": 312, "redox": 45}, "spinach": {"cal": 23, "redox": 22},
        "pomegranate": {"cal": 83, "redox": 28}, "apple": {"cal": 52, "redox": 12},
        "fries": {"cal": 312, "redox": -30}, "burger": {"cal": 250, "redox": -35},
        "soda": {"cal": 40, "redox": -18}, "donut": {"cal": 450, "redox": -40}
    }
    name = food_name.lower()
    match = next((k for k in kb if k in name), "general")
    data = kb.get(match, {"cal": 100, "redox": -5})
    
    size_factor = random.choice([0.8, 1.0, 1.5]) 
    weight = int(100 * size_factor)
    return {
        "weight": weight, "cal": int((data["cal"]/100)*weight),
        "impact": round((data["redox"]/100)*weight, 1),
        "size": "Small" if size_factor < 1 else "Large"
    }

# --- 3. UI STYLING ---
st.set_page_config(page_title="Oxidate: Hero Quest", page_icon="🛡️", layout="wide")

if 'user' not in st.session_state:
    st.session_state.user = None

# --- 4. LOGIN & SIGN UP ---
if st.session_state.user is None:
    st.title("🛡️ OXIDATE: The Great Tummy Quest")
    t1, t2 = st.tabs(["Login", "Create Your Hero"])
    with t2:
        u = st.text_input("Username")
        h_name = st.text_input("Name Your Pet Hero (e.g., Sparky)")
        p = st.text_input("Password", type="password")
        e = st.text_input("Email")
        al = st.text_input("Any Food Traps? (Allergies)")
        if st.button("Start My Quest"):
            conn = sqlite3.connect('oxidate_kids_pro.db')
            conn.execute("INSERT INTO users VALUES (?,?,?,?,?,?,?)", (u, hashlib.sha256(p.encode()).hexdigest(), e, al, "🐣", h_name, 1))
            conn.commit()
            st.success(f"{h_name} is ready for battle! Please log in.")
    with t1:
        ul, pl = st.text_input("User"), st.text_input("Pass", type="password")
        if st.button("Enter Battle"):
            conn = sqlite3.connect('oxidate_kids_pro.db')
            res = conn.execute("SELECT password FROM users WHERE username=?", (ul,)).fetchone()
            if res and res[0] == hashlib.sha256(pl.encode()).hexdigest():
                st.session_state.user = ul
                st.rerun()
    st.stop()

# --- 5. MAIN APP DATA ---
conn = sqlite3.connect('oxidate_kids_pro.db')
c = conn.cursor()
user_data = c.execute("SELECT * FROM users WHERE username=?", (st.session_state.user,)).fetchone()
# (0:user, 1:pass, 2:email, 3:allergies, 4:badge, 5:hero_name, 6:level)

# SIDEBAR: THE PET
st.sidebar.markdown(f"<h1 style='text-align: center;'>{user_data[4]}</h1>", unsafe_allow_html=True)
st.sidebar.markdown(f"<h3 style='text-align: center;'>{user_data[5]} (Lv. {user_data[6]})</h3>", unsafe_allow_html=True)

nav = st.sidebar.radio("Go To:", ["Dashboard & Map", "AI Vision Scanner", "Hero Profile"])

# --- DASHBOARD: THE WORLD MAP ---
if nav == "Dashboard & Map":
    st.title(f"📍 {user_data[5]}'s Tummy World")
    
    # Calculate Balance
    res = c.execute("SELECT SUM(impact) FROM history WHERE username=?", (st.session_state.user,)).fetchone()
    score = res[0] or 0
    
    # THE WORLD MAP PROGRESS BAR
    st.subheader("Your Journey to Shield Fortress")
    progress = min(1.0, score/500) if score > 0 else 0
    st.progress(progress)
    
    cols = st.columns(4)
    cols[0].write("🏘️ Tummy Town")
    cols[1].write("⛰️ Berry Peaks")
    cols[2].write("🏰 Shield Fortress")
    cols[3].write("👑 Hall of Legends")

    st.divider()
    c1, c2 = st.columns(2)
    c1.metric("Hero Shield Power", f"{score:.1f} pts")
    
    if score < 0:
        st.error(f"👾 **TRASH MONSTERS ARE ATTACKING!** Feed {user_data[5]} some fruit to fight back!")
    else:
        st.success(f"🛡️ **SHIELD ACTIVE!** {user_data[5]} is protecting your tummy.")

# --- AI VISION SCANNER: BATTLE MODE ---
elif nav == "AI Vision Scanner":
    st.title("📸 Neural Vision: Hero vs Monster")
    img = st.camera_input("Scan a plate to see its power!")
    label = st.text_input("What food is this?")

    if img and label:
        # Allergy Check
        if user_data[3] and user_data[3].lower() in label.lower():
            st.error(f"🚨 **DANGER TRAP!** {user_data[5]} says this food has {user_data[3]}! DON'T EAT!")
        else:
            data = get_redox_data(label)
            st.subheader("AI Visual Report")
            
            if data['impact'] > 0:
                st.info(f"✨ **HERO DETECTED!** This {label} adds **+{data['impact']}** Shield Power.")
            else:
                st.error(f"👾 **MONSTER DETECTED!** This {label} takes away **{data['impact']}** Shield Power.")
            
            st.write(f"⚖️ Weight: {data['weight']}g | 🔥 Calories: {data['cal']} kcal")
            
            if st.button("Send to Battle (Log)"):
                c.execute("INSERT INTO history VALUES (?,?,?,?,?,?)", (st.session_state.user, label, data['weight'], data['impact'], data['cal'], datetime.now()))
                # Level Up Pet if score is high
                if score > (user_data[6] * 100):
                    c.execute("UPDATE users SET pet_level = pet_level + 1 WHERE username=?", (st.session_state.user,))
                conn.commit()
                st.balloons()
                st.rerun()

# --- PROFILE: THE BADGE ROOM ---
elif nav == "Hero Profile":
    st.title("👤 The Trophy Room")
    df = pd.read_sql_query(f"SELECT food, impact, time FROM history WHERE username='{st.session_state.user}' ORDER BY time DESC", conn)
    st.write("### Your Battle History")
    st.table(df.head(10))

if st.sidebar.button("Log Out"):
    st.session_state.user = None
    st.rerun()

conn.close()
