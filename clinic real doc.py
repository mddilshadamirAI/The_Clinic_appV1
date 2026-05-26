import streamlit as st
import urllib.parse

# --- 1. CONFIGURATION & THEME ---
st.set_page_config(
    page_title="Dilshad Clinical Tool",
    page_icon="🏥",
    layout="wide"
)
st.sidebar.markdown("---")
st.sidebar.markdown("👨‍💻 **Developed by Md Dilshad Amir**")

# --- 2. PROFESSIONAL DARK UI (BLUISH-BLACK) ---
st.markdown("""
    <style>
    /* Main Background: Bluish-Black */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
        color: #f8fafc;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0f172a !important;
        border-right: 1px solid #334155;
    }

    /* Navigation Radio Buttons */
    .st-eb { color: #f8fafc !important; }

    /* Titles & Headers */
    h1, h2, h3 {
        color: #38bdf8 !important; /* Sky Blue Accent */
        font-family: 'Inter', sans-serif;
        font-weight: 800;
    }

    /* Input Boxes & Selectboxes */
    .stSelectbox div[data-baseweb="select"], .stTextInput input {
        background-color: #1e293b !important;
        color: white !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
    }
    
    label p {
        color: #94a3b8 !important; /* Muted slate for labels */
        font-weight: 600;
    }

    /* Professional Buttons */
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        background: linear-gradient(90deg, #0ea5e9 0%, #2563eb 100%);
        color: white !important;
        font-weight: bold;
        border: none;
        padding: 12px;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(14, 165, 233, 0.4);
    }

    /* Custom Card for Results & Guidance */
    .content-card {
        padding: 25px;
        background: rgba(30, 41, 59, 0.7);
        border: 1px solid #334155;
        border-radius: 15px;
        backdrop-filter: blur(10px);
        margin-bottom: 20px;
    }

    /* Metrics & Info Boxes */
    div[data-testid="stMetricValue"] {
        color: #38bdf8 !important;
    }
    .stAlert {
        background-color: #1e293b !important;
        border: 1px solid #334155 !important;
        color: #f8fafc !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATA CONSTANTS ---
DISEASE_MAP = {
    "Fever / Flu / Cold": "General Physician",
    "Chest Pain / Heart Issues": "Cardiologist",
    "Skin Rash / Acne / Hair Fall": "Dermatologist",
    "Diabetes / Thyroid / Hormones": "Endocrinologist",
    "Joint Pain / Bone Fracture": "Orthopedic Surgeon",
    "Anxiety / Stress / Mental Health": "Psychiatrist",
    "High Blood Pressure": "Cardiologist"
}
SYMPTOM_DIAGNOSTICS = {
    "Fever": {
        "remedy": "Maintain strict hydration, prioritize electrolyte-rich fluids, use lukewarm sponging, and ensure adequate ventilation.",
        "medicine": "Paracetamol (500mg) - monitor core temperature.",
        "urgency": "Persistent fever > 103°F (39.4°C), severe headache, or stiff neck.",
        "triage": "Yellow"
    },
    "Headache": {
        "remedy": "Dark, quiet environment, cold compress, and hydration.",
        "medicine": "Acetaminophen or Ibuprofen.",
        "urgency": "Sudden onset of 'thunderclap' pain, slurred speech, or vision loss.",
        "triage": "Red"
    },
    "Cough": {
        "remedy": "Steam inhalation, honey/ginger warm water, salt water gargle.",
        "medicine": "Dextromethorphan (dry) or Guaifenesin (chesty).",
        "urgency": "Coughing blood, wheezing, or difficulty breathing.",
        "triage": "Red"
    },
    "Acidity/Heartburn": {
        "remedy": "Avoid spicy foods/caffeine, eat smaller meals, sit upright.",
        "medicine": "Antacids (Digene) or Omeprazole.",
        "urgency": "Pain radiating to jaw/arm or unexplained weight loss.",
        "triage": "Yellow"
    }
}


MEDICINE_DB = {
    "Paracetamol": "Used for Fever and Pain relief. Dosage: 500mg (Consult Doctor).",
    "Cetirizine": "Used for Allergies and Skin Rashes.",
    "Azithromycin": "Antibiotic for bacterial infections.",
    "Digene": "Used for acidity and gas.",
    "Acetaminophen": "Pain relief and fever reduction",
    "Amoxicillin": "Bacterial infections (e.g., strep throat)",
    "Ibuprofen (Advil/Motrin)": "Inflammation, pain, and fever",
    "Atorvastatin (Lipitor)": "High cholesterol",
    "Metformin": "Type 2 diabetes",
    "Lisinopril": "High blood pressure",
    "Albuterol": "Asthma and bronchospasm",
    "Levothyroxine": "Hypothyroidism (underactive thyroid)",
    "Amlodipine": "High blood pressure and chest pain",
    "Gabapentin": "Nerve pain and seizures",
    "Omeprazole (Prilosec)": "Acid reflux and heartburn",
    "Losartan": "High blood pressure",
    "Sertraline (Zoloft)": "Depression and anxiety",
    "Metoprolol": "High blood pressure and chest pain",
    "Azithromycin (Z-Pak)": "Bacterial infections",
    "Hydrochlorothiazide": "Fluid retention and high blood pressure",
    "Warfarin (Coumadin)": "Blood clots",
    "Furosemide (Lasix)": "Edema (fluid buildup)",
    "Pantoprazole": "GERD and stomach acid issues",
    "Escitalopram (Lexapro)": "Anxiety and depression",
    "Ranitidine (Zantac)": "Heartburn and ulcers",
    "Prednisone": "Severe inflammation and allergies",
    "Rosuvastatin (Crestor)": "High cholesterol",
    "Tamsulosin (Flomax)": "Enlarged prostate symptoms",
    "Meloxicam": "Arthritis pain",
    "Clopidogrel (Plavix)": "Prevents stroke and heart attack",
    "Montelukast (Singulair)": "Asthma and seasonal allergies",
    "Fluoxetine (Prozac)": "Depression and OCD",
    "Tramadol": "Moderate to severe pain",
    "Duloxetine (Cymbalta)": "Nerve pain and depression",
    "Lorazepam (Ativan)": "Anxiety and seizures",
    "Ciprofloxacin": "Urinary tract and skin infections",
    "Doxycycline": "Acne and bacterial infections",
    "Cyclobenzaprine": "Muscle spasms",
    "Cephalexin (Keflex)": "Skin and bone infections",
    "Venlafaxine (Effexor)": "Panic disorder and depression",
    "Ventolin (Salbutamol)": "Shortness of breath",
    "Diazepam (Valium)": "Anxiety and muscle spasms",
    "Fluticasone (Flonase)": "Nasal allergies",
    "Oxycodone": "Severe pain",
    "Warfarin": "To prevent blood clotting",
    "Methylprednisolone": "Allergic reactions",
    "Aspirin": "Pain and prevention of heart attack",
    "Loratadine (Claritin)": "Allergies (non-drowsy)",
    "Cetirizine (Zyrtec)": "Hay fever and hives",
    "Ranitidine": "Stomach ulcers",
    "Spironolactone": "Heart failure and high blood pressure",
    "Allopurinol": "Gout",
    "Folic Acid": "Anemia and prenatal health",
    "Insulin Glargine (Lantus)": "Diabetes management"
}

# --- 4. SIDEBAR NAVIGATION ---
st.sidebar.markdown("<h2 style='text-align:center;'>🏥 CLINICAL TOOL</h2>", unsafe_allow_html=True)
menu = st.sidebar.radio("Navigation", ["Find a Doctor", "Medicine Database", "BMI Calculator", "Health Guidance", "Symptom Tracker"])
st.sidebar.markdown("---")
st.sidebar.info("Logged in as a user connect to developer via email mddilshadamir@gmail.com and give your valuable feedback")

# --- 5. PAGE LOGIC ---

# Header Section
st.markdown("<h1 style='text-align: center;'>CLINICAL TOOL</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #94a3b8;'>{menu} Portal</p>", unsafe_allow_html=True)
st.write("---")

if menu == "Find a Doctor":
    st.markdown("### 🔍 Intelligent Specialist Matching")
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            disease = st.selectbox("Select Health Concern", list(DISEASE_MAP.keys()))
        with col2:
            location = st.text_input("Enter Your City", placeholder="e.g. Bengaluru/Makhdumpur")

    if st.button("Search Specialists"):
        if not location:
            st.error("Please specify a location to continue.")
        else:
            spec = DISEASE_MAP[disease]
            st.markdown(f"""
                <div class='content-card'>
                    <h3 style='margin:0;'>Recommended Specialist: {spec}</h3>
                    <p style='color: #94a3b8;'>Searching real-time verified data for {location}...</p>
                </div>
            """, unsafe_allow_html=True)
            
            search_q = f"best {spec} in {location} reviews"
            maps_q = f"{spec} clinics in {location}"
            
            c1, c2 = st.columns(2)
            with c1:
                st.link_button(f"🌐 View Verified {spec}s", f"https://www.google.com/search?q={urllib.parse.quote(search_q)}")
            with c2:
                st.link_button(f"📍 Locate Nearby Clinics", f"https://www.google.com/maps/search/{urllib.parse.quote(maps_q)}")

elif menu == "Medicine Database":
    st.markdown("### 💊 Pharmaceutical Reference")
    search_med = st.text_input("Search Medication (e.g., Metformin):").title()
    
    if search_med:
        if search_med in MEDICINE_DB:
            st.markdown(f"<div class='content-card'><h4>{search_med}</h4><p>{MEDICINE_DB[search_med]}</p></div>", unsafe_allow_html=True)
        else:
            st.warning("Not in local records. Directing to global medical database...")
            st.link_button(f"Research {search_med}", f"https://www.google.com/search?q={urllib.parse.quote(search_med + ' uses dosage')}")

elif menu == "BMI Calculator":
    st.markdown("### ⚖️ Digital Health Assessment")
    col1, col2 = st.columns(2)
    with col1:
        weight = st.number_input("Weight (kg)", min_value=1.0, value=70.0)
    with col2:
        height_cm = st.number_input("Height (cm)", min_value=1.0, value=170.0)
    
    if st.button("Calculate Metrics"):
        bmi = weight / ((height_cm/100) ** 2)
        st.metric("BMI Score", f"{bmi:.2f}")
        
        status = "Healthy" if 18.5 <= bmi < 25 else "Attention Required"
        st.markdown(f"<div class='content-card' style='text-align:center;'><h4>Status: {status}</h4></div>", unsafe_allow_html=True)

elif menu == "Health Guidance":
    st.markdown("### 🥗 Lifestyle & Chronic Management")
    
    # Ensure these options match the dictionary keys exactly
    options = [
        "Diabetes", 
        "High Blood Pressure (BP)", 
        "Obesity", 
        "Heart Disease", 
        "Depression & Anxiety", 
        "Chronic Fatigue Syndrome"
    ]


    condition = st.selectbox("Choose Condition", options)
    
    guides = {
        "Diabetes": ("🍎 Blood Sugar Control", "Prioritize low-GI foods (oats, legumes). Limit carbs. Daily 20-min cardio."),
        "High Blood Pressure (BP)": ("❤️ Heart Health", "DASH Diet: low salt, high potassium. Stress management (Yoga/Meditation)."),
        "Obesity": ("🏃 Metabolic Boost", "High protein intake. Caloric tracking. Strength training 3x weekly."),
        "Heart Disease": ("🫀 Daily Habit", "Consume Heart-Healthy Fats and Fiber (nuts, olive oil, vegetables) and avoid trans-fats. Quit smoking immediately."),
        "Depression & Anxiety": ("🧠 Daily Habit", "Practice Daily Mindfulness or Gratitude Journaling for 5–10 minutes to reduce cortisol levels."),
        "Chronic Fatigue Syndrome": ("⚡ Daily Habit", "Follow a Structured Pacing Schedule—budget your energy by dividing tasks into smaller chunks throughout the day.")    
    }
    
    # This logic displays the data based on your selection
    if condition in guides:
        title, desc = guides[condition]
        st.markdown(f"""
            <div class='content-card'>
                <h4>{title}</h4>
                <p style='font-size: 1.1em; color: #f8fafc;'>{desc}</p>
            </div>
        """, unsafe_allow_html=True)

elif menu == "Symptom Checker":
    st.markdown("### 🩺 AI Triage & Assessment")
    symptom = st.selectbox("Select your symptom:", list(SYMPTOM_DIAGNOSTICS.keys()))
    
    if st.button("Get Clinical Advice"):
        data = SYMPTOM_DIAGNOSTICS[symptom]
        color = "#ef4444" if data['triage'] == "Red" else "#eab308"
        
        st.markdown(f"""
        <div class='content-card'>
            <h4>Advice for {symptom}</h4>
            <p><b>🏡 Remedy:</b> {data['remedy']}</p>
            <p><b>💊 Medicine:</b> {data['medicine']}</p>
            <div style='padding: 10px; border-left: 5px solid {color}; background: rgba(239, 68, 68, 0.1);'>
                <p style='margin:0;'><b>⚠️ Urgency Warning:</b> {data['urgency']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        if data['triage'] == "Red":
            st.error("🚨 THIS IS AN URGENT SYMPTOM. PLEASE CONSULT A DOCTOR IMMEDIATELY.")
    
        
elif menu == "About the developer":
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
    st.header("About the Developer")
    st.write("""
        Hi, I'm Md Dilshad Amir! The developer of Dilshad AI Clinic. I built this platform to 
        bridge the gap between patients and verified healthcare providers 
        using python and streamlit. 
    """)
    st.markdown("</div>", unsafe_allow_html=True)
    
    title, desc = guides[condition]
    st.markdown(f"""
        <div class='content-card'>
            <h4>{title}</h4>
            <p style='font-size: 1.1em;'>{desc}</p>
        </div>
    """, unsafe_allow_html=True)

# --- 6. FOOTER ---
st.write("---")
st.markdown("""
    <div style='text-align: center; color: #64748b; padding: 20px;'>
        <p>🚨 <b>Emergency Services:</b> Dial 102 (Ambulance) or 108 immediately.</p>
        <p>© 2026 Dilshad AI Clinic | Modern Healthcare for the Founder Path</p>
    </div>
""", unsafe_allow_html=True)
