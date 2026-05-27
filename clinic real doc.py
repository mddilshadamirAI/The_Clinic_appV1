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
    /* Gives the list items more space and makes them look like a cohesive clinical guide */
.content-card div {
    margin-bottom: 8px !important;
    line-height: 1.5;
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
    # --- PAIN & FEVER ---
    "Paracetamol": "Common fever and mild pain reliever.",
    "Acetaminophen": "Reduces fever and helps with headaches.",
    "Ibuprofen": "Reduces inflammation, body aches, and fever.",
    "Aspirin": "Used for minor pain and to help prevent heart attacks.",
    "Naproxen": "Long-lasting relief for muscle and joint pain.",
    "Diclofenac": "Strong relief for joint and muscle inflammation.",
    "Tramadol": "Prescription strength for moderate to severe pain.",
    "Codeine": "Strong pain reliever, often used for coughs too.",
    "Oxycodone": "Very strong pain medication for severe pain.",
    "Hydrocodone": "Prescription pain relief for severe injuries.",
    "Meloxicam": "Relieves stiffness and pain from arthritis.",
    "Celecoxib": "Helps with chronic pain and arthritis.",
    "Morphine": "Hospital-grade relief for intense, severe pain.",
    "Fentanyl": "Extremely strong pain relief (clinical use only).",
    "Ketorolac": "Short-term relief for severe post-surgery pain.",
    "Piroxicam": "Reduces pain and swelling in joints.",
    "Indomethacin": "Used specifically for gout pain and inflammation.",
    "Butalbital": "Often combined with caffeine for severe migraines.",
    "Topiramate": "Used to prevent migraine headaches.",
    "Sumatriptan": "Treats migraine headaches once they start.",

    # --- ALLERGIES & RESPIRATORY ---
    "Cetirizine": "Daily allergy relief for sneezing and itchy eyes.",
    "Loratadine": "Non-drowsy relief for seasonal allergies.",
    "Fexofenadine": "Strong relief for hay fever and skin hives.",
    "Diphenhydramine": "Helps with severe allergies and can aid sleep.",
    "Fluticasone": "Nasal spray for stuffy, runny noses.",
    "Montelukast": "Keeps airways open for asthma and allergies.",
    "Albuterol": "Inhaler for sudden asthma or breathing trouble.",
    "Salbutamol": "Opens airways during a coughing/wheezing fit.",
    "Budesonide": "Reduces swelling in lungs for asthma control.",
    "Mometasone": "Nasal spray for long-term allergy congestion.",
    "Pseudoephedrine": "Decongestant to help breathe through a blocked nose.",
    "Phenylephrine": "Helps shrink swollen nasal passages.",
    "Guaifenesin": "Thins mucus to make coughing more productive.",
    "Dextromethorphan": "Blocks the urge to cough.",
    "Bromhexine": "Helps clear sticky phlegm from the throat.",
    "Chlorpheniramine": "Relieves cold and allergy symptoms.",
    "Levocetirizine": "Potent relief for year-round allergies.",
    "Montelukast Sodium": "Prevents asthma attacks and allergy symptoms.",
    "Theophylline": "Helps relax muscles around airways.",
    "Ipratropium": "Helps dry up runny noses and open airways.",

    # --- DIGESTION & STOMACH ---
    "Omeprazole": "Reduces acid for heartburn and reflux.",
    "Pantoprazole": "Treats stomach acid issues and GERD.",
    "Esomeprazole": "Stronger acid reducer for chronic heartburn.",
    "Lansoprazole": "Protects the stomach lining from excess acid.",
    "Ranitidine": "Relieves occasional heartburn.",
    "Digene": "Neutralizes gas and stomach acid immediately.",
    "Simethicone": "Reduces painful bloating and gas.",
    "Loperamide": "Stops sudden diarrhea.",
    "Bisacodyl": "Helps with constipation.",
    "Lactulose": "Gentle stool softener for constipation.",
    "Metoclopramide": "Relieves nausea and helps stomach move food.",
    "Ondansetron": "Stops severe nausea and vomiting.",
    "Domperidone": "Helps with bloating and nausea after eating.",
    "Dicyclomine": "Calms stomach cramps (IBS symptoms).",
    "Hyoscine": "Relieves abdominal pain and stomach spasms.",
    "Psyllium Husk": "Natural fiber for regular bowel movements.",
    "Magnesium Hydroxide": "Laxative for constipation and acid relief.",
    "Famotidine": "Reduces stomach acid before a meal.",
    "Rabeprazole": "Heals stomach ulcers caused by excess acid.",
    "Cisapride": "Helps food move through the digestive tract.",

    # --- INFECTIONS (Antibiotics/Antivirals) ---
    "Amoxicillin": "Standard antibiotic for throat and ear infections.",
    "Azithromycin": "Short-course antibiotic for bacterial infections.",
    "Ciprofloxacin": "Treats urinary and some skin infections.",
    "Doxycycline": "Treats acne and various bacterial illnesses.",
    "Cephalexin": "Used for common skin and bone infections.",
    "Metronidazole": "Treats infections caused by parasites.",
    "Clindamycin": "Strong antibiotic for deep skin or dental infections.",
    "Nitrofurantoin": "Specific antibiotic for bladder infections.",
    "Trimethoprim": "Helps clear up urinary tract infections.",
    "Sulfamethoxazole": "Common antibiotic for various infections.",
    "Acyclovir": "Treats viral infections like cold sores.",
    "Valacyclovir": "Fights off shingles and genital herpes.",
    "Fluconazole": "Treats fungal/yeast infections.",
    "Clotrimazole": "Cream for athlete's foot and skin fungus.",
    "Terbinafine": "Strong medicine for nail fungus.",
    "Nystatin": "Used for oral thrush (fungal mouth infection).",
    "Oseltamivir": "Reduces duration of the flu.",
    "Cefixime": "Antibiotic for bacterial infections of the lungs.",
    "Levofloxacin": "Powerful antibiotic for respiratory infections.",
    "Mupirocin": "Antibiotic cream for infected skin wounds.",

    # --- CHRONIC CONDITIONS (BP, Cholesterol, Diabetes) ---
    "Metformin": "Controls blood sugar in Type 2 diabetes.",
    "Lisinopril": "Lowers blood pressure to protect the heart.",
    "Amlodipine": "Relaxes blood vessels to lower blood pressure.",
    "Atorvastatin": "Lowers bad cholesterol to protect heart health.",
    "Rosuvastatin": "Potent cholesterol-lowering medicine.",
    "Losartan": "Helps manage high blood pressure.",
    "Metoprolol": "Slows heart rate and lowers blood pressure.",
    "Hydrochlorothiazide": "Helps body shed extra fluid to lower BP.",
    "Spironolactone": "Manages heart failure and fluid buildup.",
    "Furosemide": "Strong diuretic for swelling (edema).",
    "Levothyroxine": "Replaces hormones for an underactive thyroid.",
    "Insulin Glargine": "Long-acting insulin for blood sugar control.",
    "Glipizide": "Helps the pancreas release insulin.",
    "Sitagliptin": "Helps regulate blood sugar levels.",
    "Telmisartan": "Manages blood pressure and heart health.",
    "Enalapril": "Prevents long-term heart and kidney damage.",
    "Simvastatin": "Standard medicine to lower cholesterol.",
    "Carvedilol": "Helps the heart pump more efficiently.",
    "Clopidogrel": "Prevents blood clots and heart attacks.",
    "Warfarin": "Strong medicine to prevent harmful blood clots.",

    # --- MENTAL HEALTH & NERVES ---
    "Sertraline": "Helps balance mood for anxiety and depression.",
    "Escitalopram": "Common treatment for anxiety and depression.",
    "Fluoxetine": "Helps with mood regulation and OCD.",
    "Duloxetine": "Treats depression and nerve-related pain.",
    "Gabapentin": "Treats nerve pain and helps prevent seizures.",
    "Lorazepam": "Reduces severe anxiety and calms nerves.",
    "Diazepam": "Relaxes muscles and calms anxiety.",
    "Venlafaxine": "Boosts mood for panic and depressive states.",
    "Amitriptyline": "Used for depression and nerve pain relief.",
    "Alprazolam": "Short-term relief for panic attacks.",
    "Pregabalin": "Relieves nerve pain and seizures.",
    "Quetiapine": "Helps stabilize mood swings.",
    "Buspirone": "Gentle daily aid for chronic anxiety.",
    "Zolpidem": "Short-term help for sleeping problems.",
    "Melatonin": "Natural supplement for sleep cycles.",
    "Mirtazapine": "Helps with mood and sleeping issues.",
    "Bupropion": "Helps with mood and quitting smoking.",
    "Citalopram": "Standard treatment for depression.",
    "Paroxetine": "Helps manage severe social anxiety.",
    "Clonazepam": "Prevents seizures and panic attacks.",

    # --- MUSCLE & BONE ---
    "Cyclobenzaprine": "Relaxes stiff, spasming muscles.",
    "Methocarbamol": "Helps with muscle pain and injury recovery.",
    "Baclofen": "Reduces muscle tightness and cramping.",
    "Tizanidine": "Relaxes muscles for back or neck pain.",
    "Allopurinol": "Prevents gout attacks.",
    "Colchicine": "Relieves pain during a gout flare-up.",
    "Calcium Carbonate": "Supplements bone health.",
    "Vitamin D3": "Essential for bone and immune health.",
    "Magnesium Oxide": "Supports muscle function.",
    "Alendronate": "Strengthens bones (prevents osteoporosis).",
    "Glucosamine": "Helps keep joints flexible.",
    "Chondroitin": "Supports joint health and cushioning.",
    "Orphenadrine": "Helps with painful muscle spasms.",
    "Dexamethasone": "Strong steroid for inflammation.",
    "Prednisone": "Used for severe allergic reactions or asthma.",
    "Methylprednisolone": "Reduces severe inflammatory swelling.",
    "Hydrocortisone": "Cream for skin inflammation and rashes.",
    "Betamethasone": "Stronger cream for stubborn skin rashes.",
    "Triamcinolone": "Reduces severe skin swelling/itching.",
    "Sulfasalazine": "Reduces inflammation in joints.",

    # --- SUPPLEMENTS & ESSENTIALS ---
    "Folic Acid": "Crucial for blood health and pregnancy.",
    "Ferrous Sulfate": "Iron supplement for anemia/low energy.",
    "Multivitamin": "General daily supplement for health.",
    "Vitamin C": "Boosts immunity and skin health.",
    "Zinc": "Supports immune system and healing.",
    "Omega-3": "Fish oil for heart and brain health.",
    "Probiotic": "Helps with gut health and digestion.",
    "Potassium": "Essential for muscle and heart function.",
    "Vitamin B12": "Boosts energy and nerve health.",
    "B-Complex": "Group of vitamins for energy and metabolism.",
    "Selenium": "Supports thyroid and immune function.",
    "Calcium Citrate": "Easier to absorb form of calcium.",
    "Coenzyme Q10": "Supports heart health and energy.",
    "Magnesium Glycinate": "Better absorbed magnesium for relaxation.",
    "Iron Bisglycinate": "Gentle iron for sensitive stomachs.",
    "Vitamin E": "Antioxidant for skin and cell health.",
    "Vitamin K2": "Helps calcium stay in bones.",
    "Ashwagandha": "Herbal supplement for stress management.",
    "Turmeric": "Natural anti-inflammatory.",
    "Ginger": "Natural remedy for nausea.",

    # --- SKIN, EYES, & EARS ---
    "Benzoyl Peroxide": "Kills bacteria for acne treatment.",
    "Salicylic Acid": "Clears pores for acne and warts.",
    "Hydroquinone": "Lightens dark spots on the skin.",
    "Adapalene": "Retinoid for deep acne prevention.",
    "Calamine": "Relieves itchy bug bites or rashes.",
    "Permethrin": "Cream for scabies or lice.",
    "Ketoconazole": "Fights stubborn dandruff and fungus.",
    "Silver Sulfadiazine": "Cream for burn healing.",
    "Timolol": "Eye drops for glaucoma.",
    "Latanoprost": "Lowers pressure inside the eye.",
    "Ciprofloxacin Eye Drops": "Antibiotic for eye infections.",
    "Ofloxacin": "Antibiotic drops for ear infections.",
    "Carbamide Peroxide": "Helps remove earwax.",
    "Fluocinolone": "Eardrops for ear canal inflammation.",
    "Sodium Hyaluronate": "Artificial tears for dry eyes.",
    "Povidone-Iodine": "Antiseptic to clean wounds.",
    "Hydrogen Peroxide": "Cleans minor cuts and scrapes.",
    "Chlorhexidine": "Antiseptic mouthwash.",
    "Benzocaine": "Numbs pain in mouth/gums.",
    "Azelic Acid": "Treats acne and redness.",

    # --- MISCELLANEOUS ---
    "Tamsulosin": "Helps men with prostate issues.",
    "Finasteride": "Treats hair loss and prostate issues.",
    "Sildenafil": "Treats erectile dysfunction.",
    "Tadalafil": "Long-acting treatment for ED.",
    "Dutasteride": "Treats enlarged prostate symptoms.",
    "Nitrofurantoin": "Prevents bladder infections.",
    "Desmopressin": "Helps control bedwetting.",
    "Oxybutynin": "Controls overactive bladder.",
    "Tolterodine": "Relaxes bladder for bladder control.",
    "Phenazopyridine": "Relieves pain from bladder infections.",
    "Tamoxifen": "Used in breast cancer hormone therapy.",
    "Anastrozole": "Used for breast cancer maintenance.",
    "Letrozole": "Used to treat breast cancer.",
    "Methotrexate": "Reduces inflammation in arthritis.",
    "Hydroxychloroquine": "Treats autoimmune conditions.",
    "Allopurinol": "Prevents uric acid buildup (gout).",
    "Febuxostat": "Lower uric acid levels.",
    "Levodopa": "Treats tremors in Parkinson’s.",
    "Carbidopa": "Helps Levodopa work better.",
    "Donepezil": "Helps with memory/Alzheimer’s symptoms."
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
    search_med = st.text_input("Start typing to search medication (e.g., Metformin):")
    
    # 1. Filter Logic: Find matches in real-time
    # This checks if the user's input exists inside any of the keys in your DB
    if search_med:
        matches = [m for m in MEDICINE_DB.keys() if search_med.lower() in m.lower()]
        
        if matches:
            # 2. Show a dynamic selectbox if there are multiple matches
            selection = st.selectbox("Select a matching medication:", matches)
            
            # 3. Display the details of the selected item
            st.markdown(f"""
                <div class='content-card'>
                    <h4>{selection}</h4>
                    <p>{MEDICINE_DB[selection]}</p>
                </div>
            """, unsafe_allow_html=True)
            
        else:
            st.warning("No matches found in local records.")
            st.link_button(f"Search global database for '{search_med}'", 
                           f"https://www.google.com/search?q={urllib.parse.quote(search_med + ' uses dosage')}")
    else:
        st.info("💡 Tip: Type a few letters (e.g., 'Met') to see matching medicines pop up.")

elif menu == "⚖️ BMI Calculator":
    st.markdown("<h3 style='margin-bottom: 0px;'>⚖️ Comprehensive Health Assessment</h3>", unsafe_allow_html=True)
    st.markdown("<div class='content-card'>", unsafe_allow_html=True)
    
    # --- NEW PERSONALIZED INPUTS ---
    colA, colB = st.columns(2)
    with colA:
        user_name = st.text_input("Full Name", value="Patient")
    with colB:
        last_weighing_date = st.date_input("Last Weighing Date")
    
    col1, col2 = st.columns(2)
    with col1:
        weight = st.number_input("Weight (kg)", min_value=1.0, value=70.0)
        height_cm = st.number_input("Height (cm)", min_value=1.0, value=170.0)
    with col2:
        body_type = st.selectbox("Body/Activity Type", ["Average", "Athletic/Gym Goer", "Slim/Ectomorph"])
        health_conditions = st.multiselect("Known Health Conditions", 
                                           ["None", "Diabetes", "High BP", "Low BP", "Heart-related issues", "Obesity"])
    
    if st.button("Calculate & Generate Report"):
        bmi = weight / ((height_cm/100) ** 2)
        st.metric("Your BMI Score", f"{bmi:.2f}")
        
        # Clinical Logic
        if bmi < 18.5: status, advice_list = "Underweight", ["Prioritize nutrient-dense foods.", "Incorporate strength training."]
        elif 18.5 <= bmi < 25: status, advice_list = "Healthy", ["Maintain your balanced diet.", "Continue regular activity."]
        elif 25 <= bmi < 30: status, advice_list = "Overweight", ["Focus on portion control.", "Increase aerobic activity."]
        else: status, advice_list = "Obese", ["Consult a healthcare provider for a weight-loss plan.", "Focus on low-impact movement."]

        # Apply Condition Logic
        if "Diabetes" in health_conditions: advice_list.insert(0, "DIABETES ALERT: Monitor glucose daily.")
        if "High BP" in health_conditions: advice_list.insert(0, "HIGH BP ALERT: Strict low-sodium diet.")
        
        advice_text = "\n".join(advice_list)
        st.markdown(f"**Status:** {status}")
        for point in advice_list: st.info(point)
        
        # --- PDF GENERATION LOGIC ---
        from datetime import date
        current_date = date.today()
        
        # Create PDF content
        report_text = f"BMI Report for {user_name}\nDate: {current_date}\nLast Weighing: {last_weighing_date}\nBMI: {bmi:.2f}\nStatus: {status}\nAdvice: {advice_text}"
        
        # Download Button
        st.download_button(
            label="📥 Download Your Personal BMI Report",
            data=report_text,
            file_name=f"bmireport_{user_name.replace(' ', '_')}.txt", # Use .txt for simplicity, or use fpdf for actual PDF
            mime="text/plain"
        )
        
        st.markdown("### Understanding your BMI")
        st.image("bmi.png", caption="BMI Classification Chart")
    
    st.markdown("</div>", unsafe_allow_html=True)
    
elif menu == "🥗 Health Guidance":
    st.markdown("### 🥗 Lifestyle & Chronic Management")
    
    # 1. Define Emojis for each condition
    condition_icons = {
        "Diabetes": "🍎", 
        "High Blood Pressure (BP)": "❤️", 
        "Obesity": "🏃", 
        "Heart Disease": "🫀", 
        "Depression & Anxiety": "🧠", 
        "Chronic Fatigue Syndrome": "⚡"
    }
    
  
    
    guides = {
    "Diabetes": [
        "1. Prioritize low-GI foods: Focus on oats, legumes, and non-starchy vegetables to keep blood sugar stable.",
        "2. Portion control: Use the 'plate method'—half your plate with vegetables, one-quarter protein, one-quarter whole grains.",
        "3. Consistency is key: Eat meals at the same time daily to help manage insulin response.",
        "4. Stay active: Engage in at least 20 minutes of moderate cardio (brisk walking) daily.",
        "5. Hydration: Opt for water or herbal teas instead of sugary sodas or juices.",
        "6. Regular monitoring: Keep a log of your blood sugar levels to share with your endocrinologist."
    ],
    "High Blood Pressure (BP)": [
        "1. Adopt the DASH Diet: Focus on fruits, vegetables, and low-fat dairy while minimizing sodium intake.",
        "2. Limit salt: Strictly avoid processed/canned foods, which are hidden sources of sodium.",
        "3. Potassium-rich diet: Incorporate bananas, spinach, and sweet potatoes to help balance blood pressure.",
        "4. Stress management: Dedicate 10 minutes daily to deep breathing, yoga, or meditation.",
        "5. Limit stimulants: Reduce caffeine and alcohol intake as they can cause temporary BP spikes.",
        "6. Quality sleep: Aim for 7–9 hours of restful sleep to allow your cardiovascular system to recover."
    ],
    "Obesity": [
        "1. Protein-focused meals: Increase protein intake to stay fuller for longer and preserve muscle mass.",
        "2. Track your intake: Use a food log to become aware of your daily caloric consumption.",
        "3. Strength training: Aim for resistance training 3x weekly to boost your basal metabolic rate (BMR).",
        "4. Mindful eating: Eat slowly and avoid distractions (like TV/phones) during meals to recognize satiety signals.",
        "5. Increase daily movement: Focus on 'NEAT'—increase steps, use stairs, and stand more during the day.",
        "6. Gradual progress: Aim for sustainable, slow weight loss (0.5–1 kg per week) rather than extreme dieting."
    ],
    "Heart Disease": [
        "1. Healthy fats: Replace saturated/trans-fats with heart-healthy sources like olive oil, nuts, and avocados.",
        "2. Boost fiber: Eat more whole grains and legumes to help lower LDL (bad) cholesterol.",
        "3. Quit smoking: Smoking is the #1 risk factor; seek support to stop immediately.",
        "4. Monitor markers: Keep a regular check on your cholesterol panels and triglyceride levels.",
        "5. Active recovery: Prioritize low-intensity steady-state cardio like swimming or cycling.",
        "6. Medical adherence: Never skip prescribed medications (like blood thinners or statins) without physician consultation."
    ],
    "Depression & Anxiety": [
        "1. Mindfulness practice: Spend 5–10 minutes daily on breathing exercises to lower cortisol.",
        "2. Gratitude journaling: Write down 3 positive things daily to shift your neurological focus.",
        "3. Sunlight exposure: Get at least 15 minutes of natural sunlight daily to boost serotonin.",
        "4. Sleep hygiene: Maintain a strict wake-up and bedtime to regulate your circadian rhythm.",
        "5. Social connection: Reach out to one person per day; social interaction is a proven mood stabilizer.",
        "6. Limit screen time: Reduce exposure to blue light and stressful social media content before bed."
    ],
    "Chronic Fatigue Syndrome": [
        "1. Structured Pacing: Budget your energy by dividing tasks into smaller, manageable chunks.",
        "2. Prioritize rest: Do not wait until you are exhausted to rest; take micro-breaks throughout the day.",
        "3. Avoid 'Push-Crash' cycles: Do not try to do double the work on a 'good' day—keep exertion levels steady.",
        "4. Gentle movement: If recommended by a doctor, do very light stretching—never push to the point of exhaustion.",
        "5. Nutrition: Focus on easy-to-digest, nutrient-dense small meals to maintain blood sugar.",
        "6. Prioritize tasks: Use the 80/20 rule—focus only on the most important 20% of your daily tasks."
    ]
}
      # 2. Add icons to the dropdown options
    options = [f"{condition_icons.get(c, '🔹')} {c}" for c in guides.keys()]
    
    # 3. Interactive Selectbox
    selected_option = st.selectbox("Select a condition to view your personalized guide:", options)
    
    # 4. Extract the clean key
    condition = selected_option.split(" ", 1)[1]
    
    # 5. Display the guide in a card
    st.markdown("---")
    st.markdown(f"### {condition_icons.get(condition, '🔹')} Management Plan for {condition}")
    
    with st.container():
        st.markdown("<div class='content-card'>", unsafe_allow_html=True)
        
        # Loop through the list of points
        for point in guides[condition]:
            # Each point is formatted with a consistent look
            st.markdown(f"✅ {point}")
            
        st.markdown("</div>", unsafe_allow_html=True)
        
    st.info("💡 **Pro-tip:** Consistency is more important than intensity. Start with just two of these habits today!")
    

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
