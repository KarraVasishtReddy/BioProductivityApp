import streamlit as st
import pandas as pd
import sqlite3
import hashlib
from datetime import datetime

# --- 1. BACKEND SETUP ---
def init_db():
    conn = sqlite3.connect('oxidate_v6.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, password TEXT, is_pro BOOLEAN, badge TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS logs 
                 (username TEXT, tribe TEXT, food TEXT, grams REAL, score REAL, time TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

# --- 2. THE SIMPLE DIFFERENTIATOR LOGIC ---
# We use a fixed "Power Factor" per gram to keep the math simple
# Anti-oxides = +0.2 points per gram | Oxides = -0.3 points per gram
def calculate_score(tribe, grams):
    if tribe == "🛡️ Team Antioxide (Hero)":
        return 0.2 * grams
    else:
        return -0.3 * grams

# --- 3. LOGIN & AUTH ---
if 'user' not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.title("🧪 Oxidate MVP")
    choice = st.radio("Access", ["Login", "Sign Up"])
    u = st.text_input("Username")
    p = st.text_input("Password", type="password")
    
    if st.button("Proceed"):
        conn = sqlite3.connect('oxidate_v6.db')
        c = conn.cursor()
        hashed_p = hashlib.sha256(p.encode()).hexdigest()
        if choice == "Sign Up":
            c.execute("INSERT INTO users VALUES (?,?,?,?)", (u, hashed_p, False, "🐣"))
            conn.commit()
            st.success("Account Created!")
        else:
            c.execute("SELECT * FROM users WHERE username=? AND password=?", (u, hashed_p))
            if c.fetchone():
                st.session_state.user = u
                st.rerun()
            else: st.error("Wrong credentials.")
    st.stop()

# --- 4. MAIN DASHBOARD ---
conn = sqlite3.connect('oxidate_v6.db')
c = conn.cursor()

# Get User Info
c.execute("SELECT is_pro, badge FROM users WHERE username=?", (st.session_state.user,))
user_data = c.fetchone()
is_pro, current_badge = user_data[0], user_data[1]

st.sidebar.title(f"{current_badge} {st.session_state.user}")
if st.sidebar.button("Logout"):
    st.session_state.user = None
    st.rerun()

# AD SPACE FOR FREE USERS
if not is_pro:
    st.sidebar.markdown("---")
    st.sidebar.error("📺 AD: Tired of Trash Monsters? Buy 'Shield-Tea' today!")
    st.sidebar.button("Upgrade to Pro for $9")

# --- 5. PURPOSE (The Goal) ---
st.title("🛡️ Tummy Battle Tracker")
st.info("**Purpose:** Balance your stomach chemistry. Every 'Oxide' (Fried/Junk) must be neutralized by an 'Antioxide' (Fruit/Veg) to keep you healthy!")

# --- 6. LOGGING (Simple Differentiator) ---
st.subheader("What are you putting in your tummy?")
tribe = st.radio("Which Tribe does this food belong to?", 
                 ["🛡️ Team Antioxide (Hero)", "👾 Team Oxide (Monster)"])

food_name = st.text_input("Food Name", placeholder="e.g. Blueberries or French Fries")
grams = st.number_input("Portion in Grams", 1, 1000, 100)

if st.button("Log Intake"):
    points = calculate_score(tribe, grams)
    c.execute("INSERT INTO logs VALUES (?,?,?,?,?,?)", 
              (st.session_state.user, tribe, food_name, grams, points, datetime.now()))
    conn.commit()
    st.success(f"Logged! {tribe} impact: {points:+.1f} points.")

# --- 7. RESULTS & BADGES ---
c.execute("SELECT SUM(score) FROM logs WHERE username=?", (st.session_state.user,))
total_bal = c.fetchone()[0] or 0

st.divider()
st.metric("Total Internal Balance", f"{total_bal:.1f} pts")

# Badge Logic
new_badge = "🐣"
if total_bal > 100: new_badge = "🛡️"
if total_bal > 300: new_badge = "⚔️"
if total_bal > 500: new_badge = "👑"

if new_badge != current_badge:
    c.execute("UPDATE users SET badge=? WHERE username=?", (new_badge, st.session_state.user))
    conn.commit()
    st.balloons()
    st.rerun()

# --- 8. PRO VERSION ($9 FEATURE) ---
if is_pro:
    st.subheader("💎 Pro Calorie Intelligence")
    # Simulating API Data
    avg_cals = 50 if tribe == "🛡️ Team Antioxide (Hero)" else 250
    st.write(f"Estimated Calories: {(avg_cals/100)*grams} kcal")
    
    st.subheader("Your History Trend")
    history = pd.read_sql_query(f"SELECT score FROM logs WHERE username='{st.session_state.user}'", conn)
    st.line_chart(history)

conn.close()
