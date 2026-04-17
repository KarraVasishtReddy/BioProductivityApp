import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- 1. THE NEUTRALIZER ENGINE ---
def get_neutralizer_suggestion(current_balance):
    """Suggests a specific food to fix a negative balance."""
    if current_balance < 0:
        needed = abs(current_balance)
        if needed < 10: return "🍵 A cup of Green Tea"
        if needed < 30: return "🫐 A bowl of Blueberries"
        return "🥗 A large Spinach & Kale Salad"
    return "✅ You are perfectly balanced! No neutralizing needed."

# --- 2. INTEGRATED APP UI ---
st.set_page_config(page_title="Oxidate: Tummy Battle", page_icon="🛡️")

# (Assume login logic from previous version is here)
if 'balance' not in st.session_state: st.session_state.balance = 0
if 'streak' not in st.session_state: st.session_state.streak = 0

st.title("🛡️ Oxidate: The Tummy Battle")

# --- FEATURE 1: THE NEUTRALIZER (Dynamic Coaching) ---
if st.session_state.balance < 0:
    st.warning("⚠️ **TRASH MONSTERS ARE WINNING!**")
    suggestion = get_neutralizer_suggestion(st.session_state.balance)
    st.write(f"**AI COACH SAYS:** To fix your stomach chemistry, eat: **{suggestion}**")

# --- FEATURE 2: DAILY QUESTS ---
st.sidebar.markdown("### 🏆 Daily Quests")
quest_completed = st.sidebar.checkbox("The Rainbow Quest: Eat 3 Colors")
if quest_completed:
    st.sidebar.success("2x Multiplier Active! ⚡")

# --- FEATURE 3: LOGGING WITH AUTO-DIFFERENTIATION ---
st.subheader("⚔️ Send Reinforcements")
col1, col2 = st.columns(2)

with col1:
    food_input = st.text_input("What did you eat?", placeholder="e.g. Pizza")
    grams = st.number_input("Grams", 1, 1000, 100)

with col2:
    # This is the "Automatic Differentiator" we built earlier
    is_hero = st.toggle("Is this a Healthy Hero?", value=True)
    
if st.button("LOG TO BATTLE"):
    # Simple Power Math: Heroes +0.2/g, Monsters -0.4/g
    impact = (0.2 * grams) if is_hero else (-0.4 * grams)
    if quest_completed and impact > 0: impact *= 2 # Quest Bonus
    
    st.session_state.balance += impact
    st.success(f"Logged! Impact: {impact:+.1f} points")
    st.rerun()

# --- FEATURE 4: PRO STREAK & HISTORY ---
st.divider()
st.subheader("📈 Your Health Journey")
c1, c2 = st.columns(2)
c1.metric("Current Balance", f"{st.session_state.balance:.1f} pts")
c2.metric("Shield Streak", f"{st.session_state.streak} Days", "🔥")

# --- 9$ PRO AD ---
if st.button("Unlock AI Camera Scanner ($9)"):
    st.toast("Redirecting to Secure Payment...", icon="💳")
