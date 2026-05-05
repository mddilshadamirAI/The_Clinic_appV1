import streamlit as st
import hashlib
import pandas as pd

# --- 1. ENHANCED DATA STRUCTURES ---
class User:
    def __init__(self, username, password, role, full_name, mobile="Not Provided"):
        self.username = username
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
        self.role = role
        self.full_name = full_name
        self.mobile = mobile

# Using session_state to keep the "Database" alive during the session
if 'users' not in st.session_state:
    st.session_state.users = {
        "admin": User("admin", "admin123", "doctor", "Dr. Dilshad (Founder)"),
        "patient1": User("patient1", "pass1", "patient", "Aman Kumar"),
    }

# Massive Indian Doctor Database
doctors_db = {
    "Dr. Khanna": {"specialty": "Cardiologist", "location": "Delhi", "experience": "15 yrs", "fee": "₹800"},
    "Dr. Isteaque": {"specialty": "Cardiologist", "location": "Mumbai", "experience": "10 yrs", "fee": "₹1000"},
    "Dr. Rehan": {"specialty": "Dermatologist", "location": "Hyderabad", "experience": "12 yrs", "fee": "₹600"},
    "Dr. Shubhash": {"specialty": "General Physician", "location": "Bengaluru", "experience": "8 yrs", "fee": "₹500"},
    "Dr. Ankit": {"specialty": "General Physician", "location": "Kolkata", "experience": "20 yrs", "fee": "₹400"},
    "Dr. Shreya": {"specialty": "Dermatologist", "location": "Chennai", "experience": "14 yrs", "fee": "₹700"},
    "Dr. Kahkasha": {"specialty": "Cardiologist", "location": "Pune", "experience": "9 yrs", "fee": "₹900"},
    "Dr. Iqra": {"specialty": "Pediatrician", "location": "Bengaluru", "experience": "7 yrs", "fee": "₹600"},
    "Dr. Adnan":{"speciality":"Dermatologist","location": "Kolkata", "experience": "2 yrs", "fee": "₹600"},
    "Dr. Aamir":{"speciality":"General Physician","location": "Kolkata", "experience": "1 yr", "fee": "₹600"},
    "Dr. Tabish":{"speciality":"Cardiologist","location": "Kolkata", "experience": "1 yr", "fee": "₹600"},
    "Dr. Zishan": {"specialty": "Pediatrician", "location": "Mumbai", "experience": "7 yrs", "fee": "₹600"},
    "Dr. Faizan":{"speciality":"Dermatologist","location": "Delhi", "experience": "2 yrs", "fee": "₹600"},
    "Dr. Farhan":{"speciality":"General Physician","location": "Hyderabad", "experience": "1 yr", "fee": "₹600"},
    "Dr. Danish":{"speciality":"Cardiologist","location": "Chennai", "experience": "1 yr", "fee": "₹600"},
}

# Pharmacy Database
medicine_db = {
    "Paracetamol": "Used for Fever and Pain relief. Dosage: 500mg (Consult Doctor).",
    "Cetirizine": "Used for Allergies and Skin Rashes.",
    "Azithromycin": "Antibiotic for bacterial infections.",
    "Digene": "Used for acidity and gas.",
    "Acetaminophen":"Pain relief and fever reduction"
 	"Amoxicillin":"Bacterial infections (e.g., strep throat)"
 	"Ibuprofen (Advil/Motrin)":	"Inflammation, pain, and fever"
	"Atorvastatin (Lipitor)":	"High cholesterol"
	"Metformin" : "Type 2 diabetes"
	"Lisinopril": "High blood pressure"
	"Albuterol" :"Asthma and bronchospasm"
	"Levothyroxine" :"Hypothyroidism (underactive thyroid)"
	"Amlodipine" :"High blood pressure and chest pain"
	"Gabapentin" :"Nerve pain and seizures"
	"Omeprazole (Prilosec)" :"Acid reflux and heartburn"
	"Losartan" :"High blood pressure"
	"Sertraline (Zoloft)":"Depression and anxiety"
	"Metoprolol" :"High blood pressure and chest pain"
	"Azithromycin (Z-Pak)":"Bacterial infections"
    "Hydrochlorothiazide":"	Fluid retention and high blood pressure"
	"Warfarin (Coumadin)":"Blood clots"
	"Furosemide (Lasix)":"Edema (fluid buildup)"
	"Pantoprazole":"GERD and stomach acid issues"
	"Escitalopram (Lexapro)":"Anxiety and depression "
	"Ranitidine (Zantac)":"Heartburn and ulcers"
	"Prednisone" :"Severe inflammation and allergies"
	"Rosuvastatin (Crestor)":"High cholesterol"
	"Tamsulosin (Flomax)":"Enlarged prostate symptoms"
	"Meloxicam":"Arthritis pain"
	"Clopidogrel (Plavix)":"Prevents stroke and heart attack"
	"Montelukast (Singulair)":"	Asthma and seasonal allergies"
	"Fluoxetine (Prozac)":"Depression and OCD"
	"Tramadol":"Moderate to severe pain"
	"Duloxetine (Cymbalta)":"Nerve pain and depression"
	"Lorazepam (Ativan)":"Anxiety and seizures"
	"Ciprofloxacin":"Urinary tract and skin infections"
	"Doxycycline":"Acne and bacterial infections"
	"Cyclobenzaprine":"Muscle spasms"
	"Cephalexin (Keflex)":"	Skin and bone infections"
	"Venlafaxine (Effexor)":"Panic disorder and depression"
	"Ventolin (Salbutamol)":"Shortness of breath"
	"Diazepam (Valium)":"Anxiety and muscle spasms"
	"Fluticasone (Flonase)":"Nasal allergies"
	"Oxycodone":"Severe pain"
	"Warfarin":"To prevent blood clotting"
	"Methylprednisolone":"Allergic reactions"
	"Aspirin":"Pain and prevention of heart attack"
	"Loratadine (Claritin)":"Allergies (non-drowsy)"
	"Cetirizine (Zyrtec)":"Hay fever and hives"
	"Ranitidine":"Stomach ulcers"
	"Spironolactone":"Heart failure and high blood pressure"
	"Allopurinol":"Gout"
    "Folic Acid":"Anemia and prenatal health"
	"Insulin Glargine (Lantus)":"Diabetes management"
}

symptom_to_specialty = {
    "Chest Pain": "Cardiologist",
    "High Blood Pressure": "Cardiologist",
    "Skin Rash": "Dermatologist",
    "Acne": "Dermatologist",
    "Fever": "General Physician",
    "Headache": "General Physician",
    "Child Cough/Cold": "Pediatrician",
}

# --- 2. PAGE CONFIG ---
st.set_page_config(page_title="Dilshad AI Clinic", page_icon="🏥", layout="wide")

# --- 3. AUTHENTICATION ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    st.title("🏥 Welcome to BharatHealth AI")
    st.info("India's fastest growing digital clinic platform.")
    
    tab1, tab2 = st.tabs(["🔐 Login", "📝 New Registration"])
    
    with tab1:
        u_name = st.text_input("Username")
        p_word = st.text_input("Password", type="password")
        if st.button("Access Dashboard"):
            if u_name in st.session_state.users:
                h = hashlib.sha256(p_word.encode()).hexdigest()
                if st.session_state.users[u_name].password_hash == h:
                    st.session_state.logged_in = True
                    st.session_state.user = st.session_state.users[u_name]
                    st.rerun()
                else:
                    st.error("Incorrect Password.")
            else:
                st.warning("User not found.")

    with tab2:
        st.subheader("Create a Founder-level Account")
        new_u = st.text_input("Choose Username")
        new_p = st.text_input("Choose Password", type="password")
        new_f = st.text_input("Full Name")
        new_m = st.text_input("Mobile Number")
        role = st.selectbox("I am a:", ["patient", "doctor"])
        
        if st.button("Register on Platform"):
            st.session_state.users[new_u] = User(new_u, new_p, role, new_f, new_m)
            st.success("Registration Successful! Please switch to Login tab.")

# --- 4. MAIN DASHBOARD ---
else:
    user = st.session_state.user
    
    # Sidebar Navigation
    st.sidebar.title(f"Namaste, {user.full_name}")
    st.sidebar.write(f"**Role:** {user.role.upper()}")
    
    if user.role == "patient":
        page = st.sidebar.radio("Go to:", ["Symptoms & Doctors", "Health Tools (BMI)", "Pharmacy Search", "Emergency"])
    else:
        page = st.sidebar.radio("Go to:", ["Doctor Dashboard", "Manage Appointments", "Emergency Alerts"])

    if st.sidebar.button("Log Out"):
        st.session_state.logged_in = False
        st.rerun()

    # --- PATIENT WORKFLOW ---
    if user.role == "patient":
        if page == "Symptoms & Doctors":
            st.header("🔍 Intelligent Symptom Checker")
            col1, col2 = st.columns(2)
            
            with col1:
                symptom = st.selectbox("What is your main symptom?", list(symptom_to_specialty.keys()))
                spec = symptom_to_specialty[symptom]
                st.write(f"Target Specialist: **{spec}**")
            
            with col2:
                city = st.selectbox("Select your City", ["Delhi", "Mumbai", "Bengaluru", "Kolkata", "Hyderabad", "Chennai", "Pune"])
            
            if st.button("Find Available Specialists"):
                results = [ (n, d) for n, d in doctors_db.items() if d["specialty"] == spec and d["location"] == city ]
                
                if results:
                    for name, info in results:
                        with st.expander(f"👨‍⚕️ {name}"):
                            st.write(f"**Experience:** {info['experience']}")
                            st.write(f"**Consultation Fee:** {info['fee']}")
                            st.button(f"Book Appointment with {name}")
                else:
                    st.error(f"No {spec} found in {city} currently. Try a nearby city.")

        elif page == "Health Tools (BMI)":
            st.header("⚖️ Digital Health Calculator")
            weight = st.number_input("Weight (kg)", min_value=1.0, value=70.0)
            height_cm = st.number_input("Height (cm)", min_value=1.0, value=170.0)
            
            if st.button("Calculate BMI"):
                height_m = height_cm / 100
                bmi = weight / (height_m ** 2)
                st.metric("Your BMI", f"{bmi:.2f}")
                if bmi < 18.5: st.warning("Underweight")
                elif 18.5 <= bmi < 25: st.success("Healthy Weight")
                else: st.error("Overweight")

        elif page == "Pharmacy Search":
            st.header("💊 Quick Medicine Info")
            med = st.selectbox("Search Medicine Name:", list(medicine_db.keys()))
            st.info(medicine_db[med])

        elif page == "Emergency":
            st.header("🚨 Emergency Services")
            st.error("In case of an emergency, call 102 (Ambulance) or 108 (Emergency).")
            st.write("---")
            st.subheader("Nearest 24/7 Hospitals (Estimated)")
            st.write("1. Apollo Hospital - 2.5km away")
            st.write("2. Fortis Care - 4.1km away")

    # --- DOCTOR WORKFLOW ---
    elif user.role == "doctor":
        st.header(f"Administrative Panel - {user.full_name}")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Total Consultations", "142", "+5 today")
        col2.metric("Patient Satisfaction", "98%", "+2%")
        col3.metric("Revenue Generated", "₹28,400", "Weekly")
        
        st.subheader("Today's Patient Queue")
        queue_data = {
            "Time": ["10:00 AM", "10:30 AM", "11:15 AM"],
            "Patient Name": ["Aman Kumar", "Sneha Rao", "Rahul Singh"],
            "Issue": ["Fever", "Follow-up", "Chest Pain"]
        }
        st.table(pd.DataFrame(queue_data))
