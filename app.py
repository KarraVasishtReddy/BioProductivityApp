import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import random
import io
from PIL import Image
from datetime import datetime

# --- 1. BACKEND & DATABASE ---
def init_db():
    conn = sqlite3.connect('oxidate_master.db')
    c = conn.cursor()
    # User accounts
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, email TEXT, 
                  age INTEGER, allergies TEXT, badge TEXT)''')
    # Health History
    c.execute('''CREATE TABLE IF NOT EXISTS history 
                 (username TEXT, food TEXT, grams REAL, impact REAL, calories REAL, time TIMESTAMP)''')
    # Custom Food Types
    c.execute('''CREATE TABLE IF NOT EXISTS custom_foods 
                 (username TEXT, food_name TEXT, impact_per_100g REAL)''')
    conn.commit()
    conn.close()

def get_connection():
    return sqlite3.connect('oxidate_master.db')

# --- 2. AI VISION ENGINE (NEURAL SCANNER) ---
def ai_vision_engine(food_name):
    """Predicts portion size, weight, and redox chemistry automatically."""
    kb = {
        "apple": {"cal": 52, "redox": 12, "avg": 150},
        "blueberry": {"cal": 57, "redox": 25, "avg": 100},
        "broccoli": {"cal": 34, "redox": 18, "avg": 120},
        "fries": {"cal": 312, "redox": -30, "avg": 200},
        "burger": {"cal": 250, "redox": -35, "avg": 250},
        "pizza": {"cal": 266, "redox": -28, "avg": 350},
        "soda": {"cal": 40, "redox": -15, "avg": 330}
    }
    
    name = food_name.lower()
    match = next((k for k in kb if k in name), "salad")
    data = kb[match]
    
    # Simulate AI portion sizing (Small, Medium, Large)
    size_factor = random.choice([0.7, 1.0, 1.5]) 
    weight = int(data["avg"] * size_factor)
    
    return {
        "weight": weight,
        "calories": int((data["cal"] / 100) * weight),
        "impact": round((data["redox"] / 100) * weight, 1),
        "size": "Small" if size_factor < 1 else ("Large" if size_factor > 1 else "Medium")
    }

# --- 3. UI CONFIGURATION ---
st.set_page_config(page_title="Oxidate Pro", page_icon="🛡️", layout="wide")
init_db()

BADGE_ICONS = {"🐣": "Beginner", "🛡️": "Shield Scout", "⚔️": "Oxide Crusher", "👑": "Legendary"}

if 'user' not in st.session_state:
    st.session_state.user = None

# --- 4. AUTHENTICATION ---
if st.session_state.user is None:
    st.title("🛡️ OXIDATE: AI Tummy Battle")
    tab1, tab2 = st.tabs(["Login", "Join the Squad"])
    
    with tab2:
        nu, ne, np, na = st.text_input("Username"), st.text_input("Email"), st.text_input("Password", type="password"), st.number_input("Age", 1, 100, 25)
        nall = st.text_input("Allergies (comma separated)")
        if st.button("Create Free Account"):
            conn = get_connection()
            try:
                conn.execute("INSERT INTO users VALUES (?,?,?,?,?,?)", (nu, hashlib.sha256(np.encode()).hexdigest(), ne, na, nall, "🐣"))
                conn.commit()
                st.success("Account Created! Use the Login tab.")
            except: st.error("Username already taken!")

    with tab1:
        u, p = st.text_input("User"), st.text_input("Pass", type="password")
        if st.button("Enter Battle"):
            conn = get_connection()
            res = conn.execute("SELECT password FROM users WHERE username=?", (u,)).fetchone()
            if res and res[0] == hashlib.sha256(p.encode()).hexdigest():
                st.session_state.user = u
                st.rerun()
            else: st.error("Invalid Login.")
    st.stop()

# --- 5. MAIN APP NAVIGATION ---
conn = get_connection()
c = conn.cursor()
user_data = c.execute("SELECT * FROM users WHERE username=?", (st.session_state.user,)).fetchone()

st.sidebar.title(f"{user_data[5]} {st.session_state.user}")
nav = st.sidebar.radio("Command Deck", ["Dashboard", "AI Vision Scanner", "Custom Food", "Profile & Badges", "Admin"])

if st.sidebar.button("Log Out"):
    st.session_state.user = None
    st.rerun()

# --- DASHBOARD ---
if nav == "Dashboard":
    st.title("🚀 Command Center")
    with st.expander("📖 The Mission (Purpose)", expanded=True):
        col_ad, col_kd = st.columns(2)
        col_ad.markdown("### 🧑‍🔬 Adults\nBalance your internal chemistry by neutralizing **Oxidative Stress** (Trash Monsters) with **Antioxidants** (Shield Heroes).")
        col_kd.markdown("### 🛡️ Kids\nHelp your Shield Heroes win the Tummy Battle! Keep your Hero Power score positive to stay strong!")

    res = c.execute("SELECT SUM(impact), SUM(calories) FROM history WHERE username=?", (st.session_state.user,)).fetchone()
    bal, cals = res[0] or 0, res[1] or 0
    
    c1, c2 = st.columns(2)
    c1.metric("Current Redox Balance", f"{bal:.1f} pts", delta="Safe" if bal >= 0 else "Oxidized")
    c2.metric("Total Calories", f"{int(cals)} kcal")

    if bal < 0:
        st.warning(f"💡 AI Suggestion: Eat 150g of Blueberries to neutralize the current monsters!")

# --- AI VISION SCANNER ---
elif nav == "AI Vision Scanner":
    st.title("📸 Neural Vision Scanner")
    img = st.camera_input("Scan your plate")
    food_label = st.text_input("What are we looking at? (e.g. 'Fries' or 'Apple')")

    if img and food_label:
        # Allergy Check
        if user_data[4] and user_data[4].lower() in food_label.lower():
            st.error(f"🚨 DANGER! This item contains {user_data[4]}!")
        
        scan = ai_vision_engine(food_label)
        st.subheader("AI Vision Prediction")
        col_s1, col_s2, col_s3 = st.columns(3)
        col_s1.write(f"⚖️ Size: **{scan['size']}** ({scan['weight']}g)")
        col_s2.write(f"🔥 Calories: **{scan['calories']} kcal**")
        col_s3.write(f"⚔️ Redox: **{scan['impact']:+.1f} pts**")

        if st.button("Confirm AI Report"):
            c.execute("INSERT INTO history VALUES (?,?,?,?,?,?)", 
                      (st.session_state.user, food_label, scan['weight'], scan['impact'], scan['calories'], datetime.now()))
            conn.commit()
            st.balloons()
            st.rerun()

# --- PROFILE & BADGES ---
elif nav == "Profile & Badges":
    st.title("👤 Hero Profile")
    res = c.execute("SELECT SUM(impact) FROM history WHERE username=?", (st.session_state.user,)).fetchone()[0] or 0
    st.write(f"**Total Hero Score:** {res:.1f}")
    
    eligible = [icon for icon, name in BADGE_ICONS.items()] # In this free version, all accessible
    new_badge = st.selectbox("Select Active Badge (Profile Photo)", eligible)
    if st.button("Update Profile Icon"):
        c.execute("UPDATE users SET badge=? WHERE username=?", (new_badge, st.session_state.user))
        conn.commit()
        st.rerun()

# --- ADMIN ---
elif nav == "Admin":
    st.title("🛠️ Global Metrics")
    st.write("Total Users Registered:", len(c.execute("SELECT * FROM users").fetchall()))
    st.dataframe(pd.read_sql_query("SELECT username, email, badge FROM users", conn))

conn.close()
