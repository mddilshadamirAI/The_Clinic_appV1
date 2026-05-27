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
    /* 1. Global Background: Sophisticated Bluish-Green Gradient */
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #115e59 100%);
        color: #f8fafc;
    }

    /* 2. Sidebar: Deep Midnight Charcoal */
    section[data-testid="stSidebar"] {
        background: #020617 !important;
        border-right: 1px solid #1e293b;
    }

    /* Sidebar Text: Ensure absolute white for high contrast */
    section[data-testid="stSidebar"] p, 
    section[data-testid="stSidebar"] div, 
    section[data-testid="stSidebar"] label {
        color: #ffffff !important;
        font-weight: 500;
    }

    /* 3. Cards: White, high-contrast surface */
    .content-card {
        padding: 25px;
        background: #ffffff;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
        color: #1e293b; /* Dark text for readability */
    }

    /* 4. Headers: Deep Teal */
    h1, h2, h3 {
        color: #0d9488 !important;
    }

    /* 3. The "Annoying White" Parts: Now Charcoal Black */
    .content-card, 
    .stTextInput input, 
    .stSelectbox div[data-baseweb="select"] {
        background-color: #1e293b !important; /* Charcoal Black */
        border: 1px solid #334155 !important;
        color: #f1f5f9 !important; /* Light text for contrast */
        border-radius: 12px !important;
    }

    /* 6. Buttons: High-contrast Teal */
    .stButton>button {
        background-color: #0d9488 !important;
        color: white !important;
        border: none !important;
        border-radius: 6px !important;
    }
    .stButton>button:hover {
        background-color: #0f766e !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
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
    # --- RESPIRATORY ---
    "Fever": {
        "remedy": "Drink at least 8 to 10 glasses of water or fresh juice throughout the day. "
                  "Use a clean, damp cloth to gently sponge your forehead and neck to bring your heat down. "
                  "Make sure you get plenty of uninterrupted sleep in a room with good air circulation. "
                  "Avoid wearing heavy layers of clothing that can trap heat against your skin. "
                  "Check your temperature every four hours to see if it is rising or falling.",
        "medicine": "Paracetamol (500mg) for fever and body ache.",
        "avoid": "Cold showers, heavy blankets, and dehydration.",
        "urgency": "Fever > 103°F, confusion, or stiff neck.",
        "triage": "Yellow"
    },
    "Common Cold": {
        "remedy": "Try steam inhalation twice a day by breathing in hot water vapor to clear your nose. "
                  "Gargle with warm salt water at least three times a day to soothe your scratchy throat. "
                  "Focus on eating warm, easy-to-digest foods like soups, broths, and cooked vegetables. "
                  "Keep your head slightly elevated with an extra pillow when sleeping to help you breathe easier. "
                  "Wash your hands frequently to prevent the cold from spreading to other people.",
        "medicine": "Vitamin C or over-the-counter cold relief tablets.",
        "avoid": "Cold drinks, ice cream, and smoking.",
        "urgency": "Shortness of breath or fever lasting > 7 days.",
        "triage": "Green"
    },
    "Cough": {
        "remedy": "Mix one teaspoon of organic honey into a cup of warm water and sip it slowly. "
                  "Keep your throat moist by drinking warm herbal tea or plain warm water frequently. "
                  "Try to cover your mouth with a clean tissue when you cough to keep the air clean. "
                  "Use a humidifier in your room if the air feels very dry to stop the throat irritation. "
                  "Avoid talking excessively or shouting, as this can strain your vocal cords and chest muscles.",
        "medicine": "Dextromethorphan (dry) or Guaifenesin (mucus).",
        "avoid": "Dusty environments and cigarette smoke.",
        "urgency": "Coughing up blood or wheezing.",
        "triage": "Red"
    },
    "Sore Throat": {
        "remedy": "Sip warm fluids like herbal tea with lemon to keep the throat lubricated and warm. "
                  "Avoid talking or singing for a few hours to give your irritated vocal cords a chance to rest. "
                  "Use a warm-mist humidifier in your room to prevent the air from drying out your throat lining. "
                  "Try sucking on medicated lozenges to produce more saliva and keep your throat moist naturally. "
                  "Ensure you are getting enough sleep to help your immune system fight off the irritation.",
        "medicine": "Lozenges or salt water gargle.",
        "avoid": "Speaking too much or eating crunchy, sharp foods.",
        "urgency": "Difficulty swallowing saliva or severe swelling.",
        "triage": "Green"
    },
    "Asthma Flare": {
        "remedy": "Sit upright and try to stay as calm as possible to help regulate your breathing. "
                  "Move away from anything that might be triggering your breathing difficulty like dust or smoke. "
                  "Use your rescue inhaler exactly as your doctor has instructed you to during an attack. "
                  "Loosen any restrictive clothing around your chest or neck to allow for maximum lung expansion. "
                  "If you have a peak flow meter, use it to check how well your lungs are working right now.",
        "medicine": "Salbutamol (Rescue Inhaler).",
        "avoid": "Strong perfumes, smoke, and cold air.",
        "urgency": "Inability to speak in full sentences or blue lips.",
        "triage": "Red"
    },

    # --- DIGESTIVE ---
    "Acidity / Heartburn": {
        "remedy": "Eat smaller, more frequent meals throughout the day instead of two or three large ones. "
                  "Make sure you sit upright for at least two hours after you finish your last meal of the day. "
                  "Try to chew your food very thoroughly before swallowing to help your stomach digest it better. "
                  "Loosen any tight clothing around your waist to reduce the pressure on your stomach area. "
                  "Keep a small food diary to identify which specific foods trigger your heartburn symptoms.",
        "medicine": "Antacids (Digene) or Omeprazole.",
        "avoid": "Spicy food, caffeine, and late-night snacks.",
        "urgency": "Chest pain radiating to the left arm/jaw.",
        "triage": "Yellow"
    },
    "Diarrhea": {
        "remedy": "Mix an Oral Rehydration Salt (ORS) packet into clean water and sip it throughout the day. "
                  "Focus on eating the BRAT diet, which includes bananas, plain rice, applesauce, and dry toast. "
                  "Avoid eating any raw salads, uncooked vegetables, or fruits with skin until you feel better. "
                  "Wash your hands thoroughly with soap after every trip to the bathroom to stop the spread. "
                  "Give your digestive system a break by choosing bland, non-greasy, and low-fiber foods.",
        "medicine": "Probiotics or anti-diarrheal (after doctor check).",
        "avoid": "Dairy, spicy food, and caffeine.",
        "urgency": "Blood in stool or severe dehydration.",
        "triage": "Red"
    },
    "Constipation": {
        "remedy": "Increase the amount of fiber in your diet by eating more papaya, beans, and green leafy vegetables. "
                  "Make sure you drink at least two liters of water daily to help soften your digestive waste. "
                  "Try to walk for at least 15 to 20 minutes every day to encourage your bowel movements. "
                  "Establish a consistent daily time for using the bathroom to train your body's natural rhythm. "
                  "If you feel an urge to go, do not ignore it, as waiting can make the stool harder and dryer.",
        "medicine": "Fiber supplements or mild laxatives (Ispaghula).",
        "avoid": "Refined flour, excess meat, and processed food.",
        "urgency": "Severe pain or no movement for 7 days.",
        "triage": "Green"
    },
    "Bloating": {
        "remedy": "Sip on warm peppermint or ginger tea after your meals to help relax your stomach muscles. "
                  "Try to eat your meals slowly and mindfully to avoid swallowing extra air while you eat. "
                  "Apply a gentle, circular massage to your abdomen to help move trapped gas through your system. "
                  "Go for a light, gentle walk after eating to aid digestion and release built-up gas pressure. "
                  "Keep track of whether certain foods like beans or lentils consistently cause you to feel swollen.",
        "medicine": "Simethicone drops.",
        "avoid": "Carbonated drinks and chewing gum.",
        "urgency": "Severe, persistent abdominal pain.",
        "triage": "Green"
    },
    "Nausea": {
        "remedy": "Sip small amounts of cold ginger tea or suck on a thin slice of fresh lemon. "
                  "Try to stay in a room with fresh, moving air and avoid stuffy or closed-off environments. "
                  "Focus on deep, slow breaths to help calm your stomach and reduce the feeling of wanting to vomit. "
                  "Choose cold or room-temperature foods, as they have less strong odors than hot, steaming meals. "
                  "Keep yourself upright for a while after eating to prevent that uneasy, sick feeling.",
        "medicine": "Ondansetron (if prescribed).",
        "avoid": "Strong smells, heavy perfumes, and greasy foods.",
        "urgency": "Vomiting blood or severe abdominal pain.",
        "triage": "Yellow"
    },

    # --- NEUROLOGICAL & MUSCULAR ---
    "Headache": {
        "remedy": "Rest in a dark, quiet room and close your eyes to reduce visual stimulation. "
                  "Apply a cool, damp cloth across your forehead or the back of your neck for relief. "
                  "Practice gentle, rhythmic deep breathing to help your muscles and mind relax. "
                  "Ensure you have drank enough water, as mild dehydration is a very common cause of head pain. "
                  "Try to limit your screen time on phones or computers until the pain completely subsides.",
        "medicine": "Acetaminophen (Paracetamol) or Ibuprofen.",
        "avoid": "Bright screens, loud music, and harsh light.",
        "urgency": "Sudden 'worst-ever' pain or vision loss.",
        "triage": "Red"
    },
    "Muscle Pain": {
        "remedy": "Give your sore muscle plenty of rest and avoid any heavy lifting or intense movement. "
                  "Use an ice pack wrapped in a thin towel for 15 minutes to reduce inflammation and heat. "
                  "Once the initial swelling goes down, you can switch to a warm pack to improve blood flow. "
                  "Perform very gentle, slow stretches to keep the muscle from getting stiff without straining it. "
                  "Make sure you get good quality sleep to help your body repair the micro-tears in the muscle.",
        "medicine": "Diclofenac gel or pain relief patches.",
        "avoid": "Strenuous exercise until the pain stops.",
        "urgency": "Inability to move the limb or deformity.",
        "triage": "Green"
    },
    "Back Pain": {
        "remedy": "Sleep on a firm mattress to provide the right support for your spine while resting. "
                  "Be mindful of your posture; keep your shoulders back and your core slightly engaged while sitting. "
                  "Use a small pillow to support the natural curve of your lower back when sitting for long periods. "
                  "Apply a warm heating pad to the area to soothe the deep muscle tension in your back. "
                  "Move your body gently throughout the day rather than staying in one position for too long.",
        "medicine": "Ibuprofen or muscle relaxant creams.",
        "avoid": "Lifting heavy objects or slouching.",
        "urgency": "Numbness in legs or loss of bladder control.",
        "triage": "Yellow"
    },
    "Migraine": {
        "remedy": "Find a completely dark and quiet space to lie down until the pulsing sensation starts to fade. "
                  "Place a cold pack on your forehead or the back of your neck to help narrow the blood vessels. "
                  "Stick to a very regular sleep schedule every single day to keep your brain rhythm stable. "
                  "Keep a small snack nearby, as skipping meals can often be a major trigger for a migraine. "
                  "Write down your migraine attacks in a diary to figure out if specific foods or lights start them.",
        "medicine": "Triptans (doctor prescribed) or NSAIDs.",
        "avoid": "Known triggers (light, specific foods, stress).",
        "urgency": "Numbness on one side of body or speech difficulty.",
        "triage": "Red"
    },
    "Neck Stiffness": {
        "remedy": "Apply a warm compress to the area for 15 minutes to help loosen the tight muscles in your neck. "
                  "Do very gentle, slow side-to-side neck rotations to slowly regain your range of motion. "
                  "Check your pillow height to ensure your neck is aligned straight with your spine while sleeping. "
                  "Avoid hunching over your phone or computer screen, which puts immense pressure on your neck. "
                  "Try a light self-massage with a soothing oil to encourage blood flow to the tense area.",
        "medicine": "Ibuprofen gel.",
        "avoid": "Sudden jerky movements or heavy backpacks.",
        "urgency": "Severe pain with high fever or inability to touch chin to chest.",
        "triage": "Yellow"
    },

    # --- DERMATOLOGICAL ---
    "Skin Rash": {
        "remedy": "Clean the area gently with lukewarm water and a very mild, fragrance-free cleanser. "
                  "Pat the skin dry with a soft, clean towel instead of rubbing it, which can cause irritation. "
                  "Wear loose-fitting, breathable cotton clothing that won't rub against the sensitive area. "
                  "Avoid the urge to scratch the rash, as your fingernails can introduce bacteria and cause infection. "
                  "Keep the skin moisturized with a simple, soothing lotion to help the protective barrier heal.",
        "medicine": "Calamine lotion or anti-histamine cream.",
        "avoid": "Scratching and perfumed soaps.",
        "urgency": "Rapid spread, blistering, or difficulty breathing.",
        "triage": "Red"
    },
    "Acne": {
        "remedy": "Wash your face twice every day using a gentle cleanser that removes excess oil but doesn't dry skin. "
                  "Avoid touching, squeezing, or popping your pimples, as this leads to permanent dark spots. "
                  "Keep your hair clean and pulled away from your face to stop hair oils from clogging your pores. "
                  "Change your pillowcases at least once a week to prevent bacteria from transferring to your skin. "
                  "Use only oil-free or 'non-comedogenic' makeup and moisturizers to ensure your pores stay open.",
        "medicine": "Salicylic acid or Benzoyl peroxide.",
        "avoid": "Touching your face and oily cosmetic products.",
        "urgency": "Deep, painful cysts causing fever.",
        "triage": "Green"
    },
    "Dry Skin": {
        "remedy": "Apply a thick, unscented moisturizer within three minutes of finishing your shower to lock in water. "
                  "Keep your showers short and use lukewarm water instead of very hot water, which strips natural oils. "
                  "Use a gentle, soap-free cleanser that is designed to be hydrating rather than harsh on the skin. "
                  "Drink plenty of water to hydrate your body from the inside out, which helps skin stay supple. "
                  "Wear gloves when using cleaning chemicals or washing dishes to protect the skin on your hands.",
        "medicine": "Ceramide-based lotions.",
        "avoid": "Very hot showers and harsh chemical soaps.",
        "urgency": "Skin cracking, bleeding, or infection signs.",
        "triage": "Green"
    },

    # --- MISCELLANEOUS ---
    "Allergy": {
        "remedy": "Identify and strictly avoid the specific trigger, such as dust, pollen, or certain pets. "
                  "Use an air purifier in your bedroom to keep the air you breathe while sleeping clean. "
                  "Change your clothes and shower after being outside to wash away pollen or environmental dust. "
                  "Keep your windows closed during high-pollen seasons to keep allergens out of your home. "
                  "Wash your bed linens in hot water every week to kill off dust mites that may be triggering you.",
        "medicine": "Cetirizine or Loratadine.",
        "avoid": "Known triggers and smoky areas.",
        "urgency": "Swelling of lips/tongue or throat tightness.",
        "triage": "Red"
    },
    "Eye Strain": {
        "remedy": "Use the 20-20-20 rule: every 20 minutes, look at an object 20 feet away for 20 full seconds. "
                  "Ensure your screen is at a comfortable distance, about an arm's length away from your face. "
                  "Adjust your lighting so that there is no harsh glare hitting your screen from behind or above. "
                  "Blink more frequently than usual while reading or working to keep your eyes naturally lubricated. "
                  "Use a lubricating eye drop if your eyes feel particularly tired or gritty at the end of the day.",
        "medicine": "Artificial tears (lubricating eye drops).",
        "avoid": "Blue light before sleep.",
        "urgency": "Sudden vision loss or severe pain.",
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
menu = st.sidebar.radio(
    "Navigation", 
    [
        "🔍 Find a Doctor", 
        "💊 Medicine Database", 
        "⚖️ BMI Calculator", 
        "🥗 Health Guidance", 
        "🩺 Symptom Checker"
    ]
)
st.sidebar.markdown("---")
st.sidebar.info("Logged in as a user connect to developer via email mddilshadamir@gmail.com and give your valuable feedback")

# --- 5. PAGE LOGIC ---

# Header Section
st.markdown("<h1 style='text-align: center;'>CLINICAL TOOL</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; color: #94a3b8;'>{menu} Portal</p>", unsafe_allow_html=True)
st.write("---")

if menu == "🔍 Find a Doctor":
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

elif menu == "💊 Medicine Database":
    st.markdown("### 💊 Pharmaceutical Reference")
    search_med = st.text_input("Search Medication (e.g., Metformin):").title()
    
    if search_med:
        if search_med in MEDICINE_DB:
            st.markdown(f"<div class='content-card'><h4>{search_med}</h4><p>{MEDICINE_DB[search_med]}</p></div>", unsafe_allow_html=True)
        else:
            st.warning("Not in local records. Directing to global medical database...")
            st.link_button(f"Research {search_med}", f"https://www.google.com/search?q={urllib.parse.quote(search_med + ' uses dosage')}")

elif menu == "⚖️ BMI Calculator":
    # 1. Compact Header
    st.markdown("<h3 style='margin-bottom: 0px;'>⚖️ Comprehensive Health Assessment</h3>", unsafe_allow_html=True)
    # 2. Main content container
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    with col1:
        weight = st.number_input("Weight (kg)", min_value=1.0, value=70.0)
        height_cm = st.number_input("Height (cm)", min_value=1.0, value=170.0)
    with col2:
        body_type = st.selectbox("Body/Activity Type", ["Average", "Athletic/Gym Goer", "Slim/Ectomorph"])
        health_conditions = st.multiselect("Known Health Conditions", 
                                         ["None", "Diabetes", "High BP", "Low BP", "Heart-related issues", "Obesity"])
    
    if st.button("Calculate Comprehensive Metrics"):
        bmi = weight / ((height_cm/100) ** 2)
        st.metric("Your BMI Score", f"{bmi:.2f}")
        
        # Clinical Logic
        if bmi < 18.5:
            status, advice = "Underweight", "Focus on nutrient-dense calorie intake and strength training."
        elif 18.5 <= bmi < 25:
            status, advice = "Healthy", "Maintain your current lifestyle. Balance cardio and resistance."
        elif 25 <= bmi < 30:
            status, advice = "Overweight", "Focus on moderate aerobic activity and portion control."
        else:
            status, advice = "Obese", "Consult a healthcare provider; focus on low-impact movement."

        # Dynamic Advice
        if "Diabetes" in health_conditions:
            advice += " Prioritize complex carbs and glucose monitoring."
        if "High BP" in health_conditions:
            advice += " Focus on low-sodium intake."
        
        # Display Results
        st.markdown(f"**Status:** {status}")
        st.info(advice)
        
        st.markdown("### Understanding your BMI")
        # Ensure this is indented to match the level of st.info(advice)
        st.image("bmi.png", caption="BMI Classification Chart")
            
    # This closes the 'content-card' div after the calculation logic
    st.markdown("</div>", unsafe_allow_html=True)
    
elif menu == "🥗 Health Guidance":
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

elif menu == "🩺 Symptom Checker":
    st.markdown("### 🩺 AI Triage & Assessment")
    symptom = st.selectbox("Select your symptom:", list(SYMPTOM_DIAGNOSTICS.keys()))
    
    if st.button("Get Clinical Advice"):
        data = SYMPTOM_DIAGNOSTICS[symptom]
        color = "#ef4444" if data['triage'] == "Red" else "#eab308"
        
        st.markdown(f"""
        <div class='content-card'>
            <h4>Advice for {symptom}</h4>
            <p><b>🤒 Avoid:</b> {data['avoid']}</p>
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
