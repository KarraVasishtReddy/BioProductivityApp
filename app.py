import streamlit as st
import pandas as pd
import sqlite3
import hashlib
import random
import io
from PIL import Image # Requirement: pip install Pillow
from datetime import datetime

# --- 1. ENHANCED VISION ENGINE (SIMULATED) ---
def analyze_plate_vision(image_file, food_label):
    """
    Simulates Computer Vision identifying food, predicting size/volume, 
    and calculating chemical impact.
    """
    # Knowledge base: Points per 100g
    kb = {
        "apple": {"cal": 52, "redox": 12},
        "blueberry": {"cal": 57, "redox": 25},
        "fries": {"cal": 312, "redox": -30},
        "burger": {"cal": 250, "redox": -35},
        "pizza": {"cal": 266, "redox": -28},
        "salad": {"cal": 25, "redox": 20}
    }

    # AI Visual Size Prediction (Simulated based on image analysis)
    # In a real app, pixel-to-object ratio determines this.
    sizes = ["Small", "Medium", "Large", "Super-Size"]
    predicted_size = random.choice(sizes)
    
    # Weight Mapping
    size_weights = {"Small": 100, "Medium": 250, "Large": 450, "Super-Size": 700}
    weight = size_weights[predicted_size]

    name = food_label.lower()
    match = next((k for k in kb if k in name), "salad")
    data = kb[match]

    calories = (data["cal"] / 100) * weight
    impact = (data["redox"] / 100) * weight

    return {
        "size": predicted_size,
        "weight": weight,
        "calories": int(calories),
        "impact": round(impact, 1),
        "type": "Hero (Antioxide)" if impact > 0 else "Monster (Oxide)"
    }

# --- 2. BACKEND & STYLING ---
st.set_page_config(page_title="Oxidate AI Vision", page_icon="📸", layout="wide")

def init_db():
    conn = sqlite3.connect('oxidate_vision.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS history (user TEXT, food TEXT, weight REAL, impact REAL, cal REAL, time TEXT)')
    conn.commit()
    conn.close()

init_db()

if 'user' not in st.session_state:
    st.session_state.user = "Hero_User" # Simplified for deployment demo

# --- 3. MAIN UI ---
st.title("📸 Oxidate: AI Vision Scanner")
st.write("Point your camera at your food to detect its size, weight, and chemical impact.")

# CAMERA INPUT
img_file = st.camera_input("Scan Your Plate")

if img_file:
    # 1. Show the Image
    img = Image.open(img_file)
    st.image(img, caption="Image Processed by Oxidate AI", width=300)
    
    # 2. Manual Label for AI context (Better for MVP Accuracy)
    food_label = st.text_input("What is this? (e.g., 'Fries' or 'Apples')")
    
    if food_label:
        # 3. RUN VISION PREDICTION
        with st.spinner("AI analyzing portion size..."):
            prediction = analyze_plate_vision(img_file, food_label)
        
        st.divider()
        st.subheader(f"📊 AI Vision Report: {food_label}")
        
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Predicted Size", prediction['size'])
        c2.metric("Estimated Weight", f"{prediction['weight']}g")
        c3.metric("Calories", f"{prediction['calories']} kcal")
        
        # Oxide vs Antioxide Differentiation
        if prediction['impact'] > 0:
            c4.metric("Shield Power", f"+{prediction['impact']}", delta="Antioxide")
            st.success(f"🛡️ This {prediction['size']} portion sends in strong Shield Heroes!")
        else:
            c4.metric("Oxide Load", f"{prediction['impact']}", delta="Monster", delta_color="inverse")
            st.error(f"👾 Careful! This {prediction['size']} portion releases high levels of Trash Monsters.")

        if st.button("Confirm and Log to Tummy"):
            conn = sqlite3.connect('oxidate_vision.db')
            c = conn.cursor()
            c.execute("INSERT INTO history VALUES (?,?,?,?,?,?)", 
                      (st.session_state.user, food_label, prediction['weight'], prediction['impact'], prediction['calories'], datetime.now().strftime("%Y-%m-%d %H:%M")))
            conn.commit()
            st.balloons()
            st.rerun()

# --- 4. HISTORY DASHBOARD ---
st.divider()
st.subheader("📈 Your Internal Chemistry Trend")
conn = sqlite3.connect('oxidate_vision.db')
df = pd.read_sql_query(f"SELECT * FROM history WHERE user='{st.session_state.user}'", conn)

if not df.empty:
    st.line_chart(df.set_index('time')['impact'])
    st.write("Full History Log:")
    st.dataframe(df, use_container_width=True)
else:
    st.info("No logs yet. Scan your first meal to see the trend!")
