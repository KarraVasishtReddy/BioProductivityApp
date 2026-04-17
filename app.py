import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import random
from datetime import datetime

# --- 1. THE AI VISION MOCK ENGINE ---
# This simulates the AI scanning a photo to predict weight and health data
def ai_vision_scan(food_name):
    """
    Simulates AI predicting portion, weight, calories, and redox score.
    In a production app, this would use a Computer Vision API (like Google Vision).
    """
    # Database of average densities (Cal/100g and Oxide/100g)
    knowledge_base = {
        "apple": {"cal": 52, "redox": 12, "avg_weight": 180},
        "blueberry": {"cal": 57, "redox": 25, "avg_weight": 150},
        "french fries": {"cal": 312, "redox": -30, "avg_weight": 200},
        "burger": {"cal": 250, "redox": -35, "avg_weight": 250},
        "broccoli": {"cal": 34, "redox": 18, "avg_weight": 100},
        "pizza": {"cal": 266, "redox": -28, "avg_weight": 300},
        "rice": {"cal": 130, "redox": 5, "avg_weight": 200}
    }
    
    name = food_name.lower()
    match = next((k for k in knowledge_base if k in name), None)
    
    if match:
        data = knowledge_base[match]
        # AI "Predicts" a slightly random weight based on average to look real
        predicted_weight = data["avg_weight"] + random.randint(-20, 20)
        calories = (data["cal"] / 100) * predicted_weight
        redox_impact = (data["redox"] / 100) * predicted_weight
        return {"weight": predicted_weight, "calories": int(calories), "impact": round(redox_impact, 1)}
    else:
        # Generic prediction for unknown foods
        return {"weight": 150, "calories": 200, "impact": -5.0}

# --- 2. BACKEND DATABASE ---
def init_db():
    conn = sqlite3.connect('oxidate_playstore.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, email TEXT, allergies TEXT, icon TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS history 
                 (username TEXT, food TEXT, weight REAL, impact REAL, calories REAL, time TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

# --- 3. UI STYLING & AUTH ---
st.set_page_config(page_title="Oxidate: AI Health", page_icon="🛡️", layout="wide")

if 'user' not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.title("🛡️ OXIDATE: AI Tummy Battle")
    auth_tab1, auth_tab2 = st.tabs(["Login", "Sign Up (Free)"])
    
    with auth_tab2:
        new_u = st.text_input("Username")
        new_e = st.text_input("Email")
        new_p = st.text_input("Password", type="password")
        new_all = st.text_input("Allergies")
        if st.button("Start My Journey"):
            conn = sqlite3.connect('oxidate_playstore.db')
            c = conn.cursor()
            c.execute("INSERT INTO users VALUES (?,?,?,?,?)", (new_u, hashlib.sha256(new_p.encode()).hexdigest(), new_e, new_all, "🐣"))
            conn.commit()
            st.success("Welcome Hero! Switch to Login.")
            
    with auth_tab1:
        u = st.text_input("User")
        p = st.text_input("Pass", type="password")
        if st.button("Enter Battle"):
            conn = sqlite3.connect('oxidate_playstore.db')
            c = conn.cursor()
            c.execute("SELECT password FROM users WHERE username=?", (u,))
            res = c.fetchone()
            if res and res[0] == hashlib.sha256(p.encode()).hexdigest():
                st.session_state.user = u
                st.rerun()
    st.stop()

# --- 4. MAIN APP ---
conn = sqlite3.connect('oxidate_playstore.db')
c = conn.cursor()
c.execute("SELECT * FROM users WHERE username=?", (st.session_state.user,))
user_data = c.fetchone()

st.sidebar.title(f"{user_data[4]} {st.session_state.user}")
if st.sidebar.button("Logout"):
    st.session_state.user = None
    st.rerun()

menu = st.sidebar.radio("Navigation", ["Dashboard", "AI Food Scanner", "Profile & Badges"])

# --- DASHBOARD ---
if menu == "Dashboard":
    st.title("🚀 Hero Command Center")
    st.info("**Purpose:** We use AI to track 'Oxidative Stress.' Fried foods create Trash Monsters (Oxides). Healthy foods send Shield Heroes (Antioxidants). **Neutralize the monsters to win!**")
    
    c.execute("SELECT SUM(impact), SUM(calories) FROM history WHERE username=?", (st.session_state.user,))
    stats = c.fetchone()
    total_bal, total_cals = stats[0] or 0, stats[1] or 0
    
    col1, col2 = st.columns(2)
    col1.metric("Current Redox Balance", f"{total_bal:.1f} pts", delta="Healthy" if total_bal >= 0 else "Oxidized")
    col2.metric("Total Calories Today", f"{int(total_cals)} kcal")

# --- AI SCANNER (PREMIUM FEATURE NOW FREE) ---
elif menu == "AI Food Scanner":
    st.title("📸 AI Neural Vision Scanner")
    st.write("AI will automatically predict portion weight, calories, and redox impact.")
    
    food_input = st.text_input("What is in the photo? (Simulated Camera Input)")
    
    if food_input:
        # Check Allergy
        if user_data[3] and user_data[3].lower() in food_input.lower():
            st.error(f"🚨 ALLERGY ALERT: AI detected {user_data[3]} in this item!")
        
        # AI PREDICTION
        scan = ai_vision_scan(food_input)
        
        st.subheader("AI Vision Prediction:")
        c1, c2, c3 = st.columns(3)
        c1.write(f"⚖️ **Weight:** {scan['weight']}g")
        c2.write(f"🔥 **Calories:** {scan['calories']} kcal")
        c3.write(f"🛡️ **Redox Score:** {scan['impact']:+.1f}")
        
        if st.button("Accept AI Prediction & Log"):
            c.execute("INSERT INTO history VALUES (?,?,?,?,?,?)", 
                      (st.session_state.user, food_input, scan['weight'], scan['impact'], scan['calories'], datetime.now()))
            conn.commit()
            st.success("Logged! Your Shield Heroes thank you.")

# --- PROFILE & BADGES ---
elif menu == "Profile & Badges":
    st.title("👤 Hero Profile")
    c.execute("SELECT SUM(impact) FROM history WHERE username=?", (st.session_state.user,))
    score = c.fetchone()[0] or 0
    
    st.subheader("Your Progress to Shield Fortress")
    st.progress(min(1.0, score/500))
    
    # Badge Unlock Logic
    badges = {"🐣 Beginner": 0, "🛡️ Shield Scout": 100, "⚔️ Oxide Crusher": 300, "👑 Legendary": 500}
    eligible = [k for k,v in badges.items() if score >= v]
    
    selected_badge = st.selectbox("Equip Your Earned Badge", eligible)
    if st.button("Update Profile"):
        c.execute("UPDATE users SET icon=? WHERE username=?", (selected_badge.split()[0], st.session_state.user))
        conn.commit()
        st.rerun()

conn.close()
