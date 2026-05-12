import streamlit as st
import urllib.parse

# --- 1. CONFIGURATION & THEME ---
st.set_page_config(
    page_title="Dilshad AI Clinic",
    page_icon="🏥",
    layout="wide"
)

# Professional CSS Styling with Fix for Invisible Text
st.markdown("""
    <style>
    /* Force main background to a light gray */
    .stApp { background-color: #f4f7f6; }
    
    /* Ensure all primary text and labels are dark and visible */
    .stApp p, .stApp label, .stApp h1, .stApp h2, .stApp h3, .stApp span {
        color: #1a1a1a !important;
    }
    
    .main-header { color: #004d40; text-align: center; padding: 10px; }
    
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        background-color: #007bff;
        color: white !important;
        font-weight: bold;
    }
    
    .guide-box {
        padding: 20px;
        background-color: white;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        margin-bottom: 15px;
        color: #1a1a1a;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA CONSTANTS ---
DISEASE_MAP = {
    "Fever / Flu / Cold": "General Physician",
    "Chest Pain / Heart Issues": "Cardiologist",
    "Skin Rash / Acne / Hair Fall": "Dermatologist",
    "Diabetes / Thyroid / Hormones": "Endocrinologist",
    "Joint Pain / Bone Fracture": "Orthopedic Surgeon",
    "Anxiety / Stress / Mental Health": "Psychiatrist",
    "High Blood Pressure": "Cardiologist"
}

MEDICINE_DB = {
    "Paracetamol": "Used for Fever and Pain relief. Typical dosage: 500mg.",
    "Metformin": "Commonly used to manage Type 2 Diabetes.",
    "Amlodipine": "Used to treat High Blood Pressure (Hypertension).",
    "Cetirizine": "Used for Allergies and Skin Rashes.",
    "Azithromycin": "Antibiotic used for bacterial infections.",
    "Omeprazole": "Used for acid reflux and heartburn.",
    "Atorvastatin": "Used to lower high cholesterol."
}

# --- 3. SIDEBAR NAVIGATION ---
st.sidebar.title("🏥 Clinic Menu")
menu = st.sidebar.radio("Go to:", ["Find a Doctor", "Medicine Database", "BMI Calculator", "Health Guidance"])

st.markdown(f"<h1 class='main-header'>Dilshad AI Clinic</h1>", unsafe_allow_html=True)
st.markdown(f"<h3 style='text-align: center;'>{menu}</h3>", unsafe_allow_html=True)

# --- 4. PAGE: FIND A DOCTOR ---
if menu == "Find a Doctor":
    st.write("### Search for verified specialists in your area.")
    col1, col2 = st.columns(2)
    with col1:
        disease = st.selectbox("What is your health concern?", list(DISEASE_MAP.keys()))
    with col2:
        location = st.text_input("Enter your City (e.g., Bengaluru, Mumbai):", placeholder="Type here...")

    if st.button("Find Specialist"):
        if not location:
            st.warning("Please enter a location.")
        else:
            spec = DISEASE_MAP[disease]
            st.success(f"Recommended Specialist: **{spec}**")
            
            search_q = f"best {spec} in {location} reviews"
            maps_q = f"{spec} clinics in {location}"
            
            c1, c2 = st.columns(2)
            with c1:
                st.link_button(f"🌐 View Top {spec}s", f"https://www.google.com/search?q={urllib.parse.quote(search_q)}")
            with c2:
                st.link_button(f"📍 View on Google Maps", f"https://www.google.com/maps/search/{urllib.parse.quote(maps_q)}")

# --- 5. PAGE: MEDICINE DATABASE ---
elif menu == "Medicine Database":
    st.write("### Quick Reference for Common Medications")
    search_med = st.text_input("Enter medicine name (e.g., Paracetamol):").title()
    
    if search_med:
        if search_med in MEDICINE_DB:
            st.info(f"**{search_med}**: {MEDICINE_DB[search_med]}")
        else:
            st.error("Medicine not found in local database.")
            st.link_button(f"Search for '{search_med}' info", f"https://www.google.com/search?q={urllib.parse.quote(search_med + ' uses and side effects')}")

# --- 6. PAGE: BMI CALCULATOR ---
elif menu == "BMI Calculator":
    st.write("### Body Mass Index (BMI) Tool")
    c1, c2 = st.columns(2)
    weight = c1.number_input("Weight (kg)", min_value=1.0, value=70.0)
    height_cm = c2.number_input("Height (cm)", min_value=1.0, value=170.0)
    
    if st.button("Calculate My BMI"):
        bmi = weight / ((height_cm/100) ** 2)
        st.metric("Your BMI Score", f"{bmi:.2f}")
        
        if bmi < 18.5: st.warning("Category: Underweight")
        elif 18.5 <= bmi < 24.9: st.success("Category: Normal / Healthy Weight")
        elif 25 <= bmi < 29.9: st.warning("Category: Overweight")
        else: st.error("Category: Obesity")

# --- 7. PAGE: HEALTH GUIDANCE ---
elif menu == "Health Guidance":
    st.write("### Expert Lifestyle Tips for Chronic Conditions")
    condition = st.selectbox("Select a condition:", ["Diabetes", "High Blood Pressure (BP)", "Obesity"])
    
    if condition == "Diabetes":
        st.markdown("""<div class='guide-box'>
            <h4>🍎 Diabetes Management</h4>
            <ul>
                <li><b>Diet:</b> Focus on whole grains and lean protein. Avoid refined sugar.</li>
                <li><b>Exercise:</b> At least 30 mins of brisk walking daily.</li>
                <li><b>Monitoring:</b> Check blood sugar levels regularly.</li>
            </ul></div>""", unsafe_allow_html=True)
            
    elif condition == "High Blood Pressure (BP)":
        st.markdown("""<div class='guide-box'>
            <h4>❤️ BP Management</h4>
            <ul>
                <li><b>Sodium:</b> Reduce salt intake to less than 5g per day.</li>
                <li><b>Stress:</b> Practice deep breathing or meditation.</li>
                <li><b>Activity:</b> Regular cardio helps lower blood pressure.</li>
            </ul></div>""", unsafe_allow_html=True)

    elif condition == "Obesity":
        st.markdown("""<div class='guide-box'>
            <h4>🏃 Weight Management</h4>
            <ul>
                <li><b>Caloric Deficit:</b> Burn more calories than you consume.</li>
                <li><b>Hydration:</b> Drink plenty of water; avoid sugary sodas.</li>
                <li><b>Consistency:</b> Focus on small, daily improvements.</li>
            </ul></div>""", unsafe_allow_html=True)

# --- 8. FOOTER ---
st.write("---")
st.caption("🚨 Disclaimer: This tool is for informational purposes only. Always consult a certified doctor before starting any medication.")
