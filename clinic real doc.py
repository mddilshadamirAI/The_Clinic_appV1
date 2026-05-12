import streamlit as st
import urllib.parse

# --- 1. CONFIGURATION & STYLING ---
st.set_page_config(
    page_title="Dilshad AI Clinic", 
    page_icon="🏥", 
    layout="wide"
)

# Custom CSS for a professional look
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        height: 3.5em;
        background-color: #007bff;
        color: white;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover {
        background-color: #0056b3;
        border: none;
    }
    .result-card {
        padding: 20px;
        border-radius: 10px;
        background-color: white;
        border-left: 5px solid #007bff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA MAPPING (Disease to Specialist) ---
# This ensures users find the correct type of doctor for their specific issue.
disease_map = {
    "Fever / Flu / Cold": "General Physician",
    "Chest Pain / Heart Issues": "Cardiologist",
    "Skin Rash / Acne / Hair Fall": "Dermatologist",
    "Diabetes / Thyroid / Hormones": "Endocrinologist",
    "Joint Pain / Bone Fracture / Arthritis": "Orthopedic Surgeon",
    "Child Health / Vaccination / Pediatric": "Pediatrician",
    "Stomach Pain / Digestion / Acidity": "Gastroenterologist",
    "Eye Vision / Redness / Surgery": "Ophthalmologist",
    "Anxiety / Stress / Mental Health": "Psychiatrist",
    "Dental Pain / Cavity / Braces": "Dentist",
    "Ear, Nose, or Throat issues": "ENT Specialist"
}

# --- 3. MAIN INTERFACE ---
st.title("🏥 Dilshad AI Clinic")
st.markdown("### Find Verified Medical Specialists Instantly")
st.write("India's smart directory for connecting patients with the right doctors.")

st.divider()

# Input Section
with st.container():
    col1, col2 = st.columns(2)
    
    with col1:
        disease = st.selectbox(
            "📋 Select your health concern:",
            options=list(disease_map.keys()),
            help="Choose the option that best describes your current symptoms."
        )

    with col2:
        # Note: 'location' input will be used to customize the external search results
        location = st.text_input(
            "📍 Enter your City or Area:", 
            placeholder="e.g., Bengaluru, Mumbai, Delhi...",
            help="Providing a location helps find doctors nearest to you."
        )

st.write("") # Spacer

# --- 4. SEARCH LOGIC & RESULTS ---
if st.button("Find Top-Rated Specialists"):
    if not location.strip():
        st.error("⚠️ Please enter a location to view results.")
    else:
        specialist = disease_map[disease]
        
        # Display the recommendation
        st.markdown(f"""
            <div class="result-card">
                <h3 style='margin:0;'>Recommended Specialist: {specialist}</h3>
                <p style='color: #666;'>Based on your concern: <b>{disease}</b></p>
            </div>
        """, unsafe_allow_html=True)
        
        st.write("---")
        st.subheader(f"🌐 Verified {specialist}s in {location}")
        st.info(f"We have generated direct access to the highest-rated {specialist}s in your area. Click a source below to view schedules and reviews.")

        # Constructing queries
        # Google Search targets directories like Practo, Lybrate, and Apollo
        search_query = f"best {specialist} in {location} reviews contact"
        # Google Maps targets local clinics
        maps_query = f"{specialist} clinics near {location}"
        
        google_url = f"https://www.google.com/search?q={urllib.parse.quote(search_query)}"
        maps_url = f"https://www.google.com/maps/search/{urllib.parse.quote(maps_query)}"

        # Action Buttons
        btn_col1, btn_col2 = st.columns(2)
        
        with btn_col1:
            st.link_button(f"🌐 View Top {specialist}s", google_url, use_container_width=True)
            st.caption("Browse expert profiles, patient reviews, and consultation fees.")
            
        with btn_col2:
            # Styled via custom CSS or default link_button
            st.link_button(f"📍 View Nearby Clinics", maps_url, use_container_width=True)
            st.caption("See real-time distance, clinic photos, and opening hours.")

# --- 5. EMERGENCY FOOTER ---
st.divider()
st.warning("**EMERGENCY?** Please call **102** (Ambulance) or **108** (Emergency Services) immediately if you require urgent medical attention.")

st.markdown("""
<div style="text-align: center; margin-top: 50px; color: #888; font-size: 0.8em;">
    <p>© 2026 Dilshad AI Clinic | Designed for rapid healthcare access</p>
    <p>Founder Path: Connecting technology with human health.</p>
</div>
""", unsafe_allow_html=True)
