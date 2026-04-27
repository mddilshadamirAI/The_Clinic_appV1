import streamlit as st
import hashlib

# --- 1. Data Structures (Same logic, new display) ---
class User:
    def __init__(self, username, password, role, full_name, address=None):
        self.username = username
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
        self.role = role
        self.full_name = full_name
        self.address = address

# In-memory database (Note: In a real app, we'd use a real database or st.session_state)
if 'users' not in st.session_state:
    st.session_state.users = {
        "patient1": User("patient1", "pass1", "patient", "John Doe"),
        "davis": User("davis", "docpass1", "doctor", "Dr. Davis"),
    }

doctors_db = {
    "Dr. Davis": {"specialty": "Cardiologist", "location": "New York"},
    "Dr. Chen": {"specialty": "Dermatologist", "location": "Los Angeles"},
    "Dr. Patel": {"specialty": "General Physician", "location": "New York"},
}

symptom_to_specialty = {
    "Chest Pain": "Cardiologist",
    "Fever": "General Physician",
    "Skin Rash": "Dermatologist",
}

home_treatments = {
    "Fever": "Rest, drink plenty of fluids, and consider acetaminophen.",
    "Default": "Please consult a doctor for an accurate diagnosis."
}

# --- 2. Streamlit UI Setup ---
st.set_page_config(page_title="Dilshad's AI Clinic", page_icon="🏥")
st.title("🏥 Advanced Clinic System")

# --- 3. Authentication Logic ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        u_name = st.text_input("Username")
        p_word = st.text_input("Password", type="password")
        if st.button("Login"):
            if u_name in st.session_state.users:
                h = hashlib.sha256(p_word.encode()).hexdigest()
                if st.session_state.users[u_name].password_hash == h:
                    st.session_state.logged_in = True
                    st.session_state.user = st.session_state.users[u_name]
                    st.rerun()
                else:
                    st.error("Invalid password")
            else:
                st.warning("User not found. Please register.")

    with tab2:
        new_u = st.text_input("New Username")
        new_p = st.text_input("New Password", type="password")
        new_f = st.text_input("Full Name")
        if st.button("Create Account"):
            st.session_state.users[new_u] = User(new_u, new_p, "patient", new_f)
            st.success("Account created! Go to Login tab.")

# --- 4. Post-Login Workflows ---
else:
    user = st.session_state.user
    st.sidebar.write(f"Logged in as: **{user.full_name}** ({user.role})")
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.rerun()

    if user.role == "patient":
        st.header(f"Welcome, {user.full_name}")
        
        # Symptom Selection
        symptom = st.selectbox("What is your symptom?", list(symptom_to_specialty.keys()))
        specialty = symptom_to_specialty[symptom]
        st.info(f"Recommended Specialist: **{specialty}**")

        # Home Treatment
        if st.checkbox("Show Home Treatment Advice"):
            treatment = home_treatments.get(symptom, home_treatments["Default"])
            st.write(f"💡 **Advice:** {treatment}")

        # Find Doctor
        city = st.text_input("Enter your city to find a doctor")
        if city:
            results = [name for name, d in doctors_db.items() 
                       if d["specialty"] == specialty and city.lower() in d["location"].lower()]
            if results:
                st.success(f"Found {len(results)} specialist(s) in {city}:")
                for r in results:
                    st.write(f"- {r}")
            else:
                st.error("No specialists found in this city.")

    elif user.role == "doctor":
        st.header(f"Doctor Dashboard: {user.full_name}")
        st.write("---")
        st.subheader("Patient Feedback")
        # In Streamlit, we can't easily edit local .txt files on the cloud, 
        # so we display a placeholder or use st.session_state
        st.text_area("Latest Feedback", "Dr. Davis is very helpful! - John Doe", height=150)
