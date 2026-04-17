import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import requests
from datetime import datetime

# --- 1. CORE ENGINE: DIFFERENTIATOR ---
def calculate_oxide_score(food_name):
    """
    Strictly differentiates between Oxides (Fried) and Anti-oxides (Fruits/Veggies).
    Returns a 'Points per 100g' value.
    """
    name = food_name.lower()
    
    # Category 1: THE OXIDES (Pro-oxidants / Trash Monsters)
    # Keywords for fried, oily, or high-sugar items
    oxide_keywords = ['fried', 'fries', 'burger', 'pizza', 'soda', 'donut', 'crispy', 'grease', 'oil', 'chip']
    
    # Category 2: THE ANTI-OXIDES (Shield Heroes)
    # Keywords for fresh produce and healing items
    antioxidant_keywords = ['fruit', 'berry', 'apple', 'orange', 'veg', 'leaf', 'spinach', 'broccoli', 'kale', 'tea', 'salad']

    # Logic Check: Prioritize 'Fried' detection to avoid misclassifying 'French Fries'
    if any(word in name for word in oxide_keywords):
        return -25  # High Oxidative Impact
    elif any(word in name for word in antioxidant_keywords):
        return 15   # High Antioxidant Impact
    else:
        return 0    # Neutral/Unknown

# --- 2. BACKEND & API SETUP ---
API_KEY = "YOUR_SPOONACULAR_API_KEY" # Optional for Calorie Accuracy

def init_db():
    conn = sqlite3.connect('oxidate_pro_v5.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (username TEXT PRIMARY KEY, email TEXT, password TEXT, allergies TEXT, is_pro BOOLEAN, icon TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS history 
                 (username TEXT, food TEXT, grams REAL, impact REAL, calories REAL, time TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

# --- 3. UI & AUTHENTICATION ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.user = None

if not st.session_state.logged_in:
    st.title("🧪 Oxidate: Pro-Health Tracker")
    t1, t2 = st.tabs(["Login", "Sign Up"])
    with t2:
        u, p, e, al = st.text_input("Username"), st.text_input("Password", type="password"), st.text_input("Email"), st.text_input("Allergies")
        if st.button("Register"):
            conn = sqlite3.connect('oxidate_pro_v5.db')
            c = conn.cursor()
            c.execute("INSERT INTO users VALUES (?,?,?,?,?,?)", (u, e, hashlib.sha256(p.encode()).hexdigest(), al, False, "🐣"))
            conn.commit()
            st.success("Hero Created!")
    with t1:
        u_l, p_l = st.text_input("User"), st.text_input("Pass", type="password")
        if st.button("Login"):
            conn = sqlite3.connect('oxidate_pro_v5.db')
            c = conn.cursor()
            c.execute("SELECT password FROM users WHERE username=?", (u_l,))
            res = c.fetchone()
            if res and res[0] == hashlib.sha256(p_l.encode()).hexdigest():
                st.session_state.logged_in, st.session_state.user = True, u_l
                st.rerun()
    st.stop()

# --- 4. MAIN DASHBOARD ---
conn = sqlite3.connect('oxidate_pro_v5.db')
c = conn.cursor()
c.execute("SELECT * FROM users WHERE username=?", (st.session_state.user,))
user_info = c.fetchone()

st.sidebar.title(f"{user_info[5]} {st.session_state.user}")
menu = st.sidebar.radio("Navigation", ["Dashboard", "Log Food", "History", "Profile"])

if menu == "Dashboard":
    st.title("🛡️ Tummy Battle Command")
    
    # Purpose Section
    st.info("### The Goal: Oxide Neutralization")
    st.write("**Oxides (Trash Monsters):** Found in fried food. They steal energy from your cells.")
    st.write("**Anti-oxides (Shield Heroes):** Found in fruits. They protect your cells and give them energy.")

    c.execute("SELECT SUM(impact), SUM(calories) FROM history WHERE username=?", (st.session_state.user,))
    stats = c.fetchone()
    bal, cals = stats[0] or 0, stats[1] or 0
    
    col1, col2 = st.columns(2)
    col1.metric("Net Balance Score", f"{bal:.1f}", delta="Healing" if bal >= 0 else "Oxidizing")
    col2.metric("Energy Consumed", f"{int(cals)} kcal")

# --- 5. LOG FOOD (Fixed Logic) ---
elif menu == "Log Food":
    st.title("⚖️ Precision Intake")
    food_name = st.text_input("Enter Food (e.g., 'French Fries' or 'Blueberry')")
    grams = st.number_input("Weight (Grams)", 1, 1000, 100)

    if food_name:
        # Check Allergies
        if user_info[3] and user_info[3].lower() in food_name.lower():
            st.error(f"🚨 STOP! Allergy detected for: {user_info[3]}")
        
        # Calculate Score using the new differentiator
        base_score = calculate_oxide_score(food_name)
        total_impact = (base_score / 100) * grams
        
        # Calorie Logic (Simplified for this demo, can connect to API)
        cal_est = 300 if base_score < 0 else 50 
        total_cals = (cal_est / 100) * grams

        st.subheader("Analysis Preview")
        if base_score < 0:
            st.error(f"👾 This is an **Oxide** (Fried/Heavy). It will add **{total_impact}** points of stress.")
        elif base_score > 0:
            st.success(f"🛡️ This is an **Anti-oxide** (Fruit/Veg). It will add **{total_impact}** points of protection.")
        else:
            st.warning("⚖️ This food is Neutral.")

        if st.button("Log to Backend"):
            c.execute("INSERT INTO history VALUES (?,?,?,?,?,?)", 
                      (st.session_state.user, food_name, grams, total_impact, total_cals, datetime.now()))
            conn.commit()
            st.success("Logged successfully!")

# --- 6. LOGOUT ---
if st.sidebar.button("Logout"):
    st.session_state.logged_in = False
    st.rerun()

conn.close()
