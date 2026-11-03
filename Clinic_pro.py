"""
CLINIC PRO — Smart Healthcare Companion
Run: streamlit run clinic_pro.py

Safety design:
- Educational information only; never diagnoses or prescribes.
- No medicine doses or self-medication recommendations.
- No fabricated doctor/clinic listings.
- Personal entries are session-only unless the user exports them.
"""

import streamlit as st
import json
import csv
import io
from datetime import datetime, date

st.set_page_config(
    page_title="CLINIC PRO | Healthcare Companion",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ----------------------------- DESIGN SYSTEM -----------------------------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@500;600;700;800&display=swap');
:root { --ink:#eaf2ff; --muted:#9fb0c8; --panel:#111d31; --panel2:#17263d; --line:#263954; --teal:#38d6c0; --blue:#77a9ff; }
html, body, [class*="css"] { font-family:'DM Sans',sans-serif; }
.stApp { background: radial-gradient(ellipse at 15% 0%, #153b4c 0%, #0b1424 48%, #08111e 100%); color:var(--ink); }
[data-testid="stSidebar"] { background:#081321; border-right:1px solid #20334d; }
[data-testid="stSidebar"] * { color:#eaf2ff !important; }
h1,h2,h3 { font-family:'Manrope',sans-serif !important; letter-spacing:-.035em; color:#f4f8ff !important; }
p, label, li { color:#d5e0ef; }
div[data-testid="stMetric"] { background:linear-gradient(145deg,#15263c,#101c2e); border:1px solid #29415e; padding:16px; border-radius:16px; }
div[data-testid="stMetric"] label { color:#9fb0c8 !important; }
div[data-testid="stMetric"] [data-testid="stMetricValue"] { color:#f4f8ff !important; }
.stButton>button, .stDownloadButton>button { border-radius:11px; border:1px solid #39cdb9; background:#087f78; color:white; font-weight:700; min-height:2.7rem; }
.stButton>button:hover, .stDownloadButton>button:hover { background:#0b9b8d; border-color:#72f0dc; color:white; }
.stTextInput input, .stTextArea textarea, .stNumberInput input, [data-baseweb="select"] > div { background:#111f33 !important; color:#edf5ff !important; border-color:#304761 !important; border-radius:10px !important; }
div[data-testid="stExpander"] { background:#111e31; border:1px solid #263b55; border-radius:13px; }
div[data-testid="stAlert"] { border-radius:12px; }
.hero { padding:28px 30px; border:1px solid #2b5267; border-radius:22px; background:linear-gradient(115deg,rgba(15,115,112,.32),rgba(31,59,99,.38)); margin:8px 0 22px; }
.hero-kicker { color:#65e6d3; font-size:.78rem; font-weight:800; letter-spacing:.16em; text-transform:uppercase; }
.hero-title { font-family:Manrope,sans-serif; font-size:2.2rem; line-height:1.12; font-weight:800; color:#fff; margin:.35rem 0; }
.hero-sub { color:#b6c8dd; max-width:760px; }
.panel { padding:18px 20px; border:1px solid #293f5b; border-radius:16px; background:rgba(17,30,49,.88); margin-bottom:14px; }
.small-muted { color:#9fb0c8; font-size:.88rem; }
.pill { display:inline-block; padding:4px 10px; border-radius:99px; background:#163b46; color:#83eee0; font-size:.76rem; font-weight:700; }
.footer { color:#8296b1; text-align:center; padding:22px 0 10px; border-top:1px solid #20334d; margin-top:30px; font-size:.82rem; }
</style>
""", unsafe_allow_html=True)

# ----------------------------- CONTENT LIBRARY -----------------------------
MEDICINES = {
    "Paracetamol (acetaminophen)": ("Pain reliever / fever reducer", "Used for pain and fever.", "Too much can seriously damage the liver. Check combination cold/flu products to avoid duplicate ingredients.", "Use only according to the product label or a clinician's instructions."),
    "Ibuprofen": ("NSAID pain reliever", "Used for pain, fever and inflammation.", "May be unsuitable with stomach ulcers, kidney disease, dehydration, some asthma, blood thinners or pregnancy. Can irritate the stomach.", "Ask a pharmacist or clinician whether it is appropriate for you."),
    "Naproxen": ("NSAID pain reliever", "Used for pain and inflammation.", "Has stomach, kidney and cardiovascular risks; can interact with blood thinners and other NSAIDs.", "Clinician/pharmacist guidance is important."),
    "Cetirizine": ("Antihistamine", "Used for allergy symptoms such as sneezing and itching.", "Can cause drowsiness in some people. Avoid combining with sedating medicines unless advised.", "Check age-specific label instructions with a pharmacist."),
    "Loratadine": ("Antihistamine", "Used for allergy symptoms.", "Usually less sedating, but drowsiness can still occur.", "Check the label and ask a pharmacist if unsure."),
    "Fexofenadine": ("Antihistamine", "Used for allergy symptoms.", "Interactions and absorption can be affected by some fruit juices and antacids.", "Ask a pharmacist about timing and suitability."),
    "Salbutamol (albuterol)": ("Bronchodilator inhaler", "A reliever medicine used in some asthma action plans.", "A worsening asthma attack or poor response to a reliever needs urgent medical assessment.", "Use only as prescribed and follow the personal asthma action plan."),
    "Budesonide": ("Corticosteroid", "An anti-inflammatory medicine used in several conditions, including asthma control.", "Not usually a rescue treatment for sudden severe breathing difficulty. Rinse mouth after inhaled use if instructed.", "Follow the prescribed plan; do not change controller treatment independently."),
    "Omeprazole": ("Proton-pump inhibitor", "Reduces stomach acid in conditions such as reflux.", "Long-term use should be reviewed; may interact with other medicines.", "Seek assessment for swallowing difficulty, bleeding, unexplained weight loss or persistent symptoms."),
    "Pantoprazole": ("Proton-pump inhibitor", "Reduces stomach acid.", "Long-term use and interactions should be reviewed by a clinician.", "Use according to professional advice."),
    "Oral rehydration salts (ORS)": ("Rehydration product", "Helps replace water and electrolytes during diarrhoea-related fluid loss.", "Mix exactly as directed on the packet; incorrect concentration can be harmful.", "Seek care for severe dehydration, blood in stool, or inability to keep fluids down."),
    "Amoxicillin": ("Prescription antibiotic", "Treats certain bacterial infections when prescribed.", "Does not treat viral colds or flu. Allergy and antibiotic resistance are important concerns.", "Never use leftover antibiotics or share them; complete the prescribed plan unless the prescriber changes it."),
    "Azithromycin": ("Prescription antibiotic", "Treats selected bacterial infections.", "Can affect heart rhythm and interact with other medicines; not appropriate for every infection.", "Use only when prescribed for the current illness."),
    "Doxycycline": ("Prescription antibiotic", "Treats selected bacterial infections and some skin conditions.", "Can cause sun sensitivity and irritation of the oesophagus; suitability varies by age and pregnancy status.", "Prescription and pharmacist guidance required."),
    "Metformin": ("Prescription diabetes medicine", "Helps manage blood glucose in type 2 diabetes.", "Needs review in kidney problems and during some acute illnesses or procedures.", "Do not start, stop or change without the diabetes care team."),
    "Insulin": ("Prescription hormone medicine", "Used in diabetes treatment plans.", "Incorrect use can cause dangerously low blood glucose.", "Only use the exact insulin and plan prescribed; get urgent help for severe symptoms."),
    "Amlodipine": ("Prescription blood-pressure medicine", "A calcium-channel blocker used for high blood pressure and some heart conditions.", "May cause ankle swelling or dizziness; interactions are possible.", "Do not stop or adjust blood-pressure treatment without the prescriber."),
    "Losartan": ("Prescription blood-pressure medicine", "An angiotensin receptor blocker used for blood pressure and selected kidney/heart conditions.", "Not suitable in pregnancy; potassium and kidney function may need monitoring.", "Use only under clinician supervision."),
    "Atorvastatin": ("Prescription lipid-lowering medicine", "Lowers LDL cholesterol and cardiovascular risk in selected people.", "Report unexplained muscle pain or weakness; interactions are possible.", "Treatment decisions depend on overall cardiovascular risk."),
    "Levothyroxine": ("Prescription thyroid hormone", "Replaces thyroid hormone in hypothyroidism.", "Absorption is affected by food, iron, calcium and some other products.", "Timing and blood-test monitoring should follow clinician instructions."),
    "Sertraline": ("Prescription antidepressant (SSRI)", "Used for depression and several anxiety-related conditions.", "Can take weeks to help; stopping suddenly may cause problems. Interactions can be serious.", "Do not start, stop or change without the prescriber."),
    "Escitalopram": ("Prescription antidepressant (SSRI)", "Used for depression and some anxiety conditions.", "May cause side effects and has important interaction considerations.", "Clinician monitoring is recommended, especially after starting or changing."),
    "Prednisolone": ("Prescription corticosteroid", "Reduces inflammation in selected conditions.", "Can affect blood sugar, mood, infection risk and blood pressure; prolonged use requires careful management.", "Do not abruptly stop a prolonged course unless a clinician directs you."),
    "Diclofenac": ("NSAID pain reliever", "Used for pain and inflammation in selected situations.", "Can increase stomach, kidney and cardiovascular risks; avoid combining NSAIDs unless instructed.", "Ask a clinician/pharmacist before use."),
    "Ondansetron": ("Prescription anti-nausea medicine", "Used for nausea and vomiting in selected situations.", "Can affect heart rhythm and interact with other medicines.", "Use only when prescribed; urgent assessment may be needed for persistent vomiting."),
    "Fluconazole": ("Antifungal medicine", "Treats selected fungal infections.", "Can interact with many medicines and may affect the liver or heart rhythm.", "Use only for the diagnosed infection and as advised."),
    "Clotrimazole": ("Antifungal medicine", "Treats selected fungal skin or yeast infections.", "The correct formulation and treatment duration depend on the infection site.", "Ask a pharmacist if the diagnosis or product is uncertain."),
    "Warfarin": ("Prescription anticoagulant", "Reduces blood clot formation in selected conditions.", "Bleeding risk and interactions are significant; regular INR monitoring is required.", "Never change the dose yourself; seek urgent help for serious bleeding."),
    "Clopidogrel": ("Prescription antiplatelet", "Helps prevent harmful blood clots in selected patients.", "Bleeding risk and medicine interactions matter.", "Do not stop after a stent or stroke unless the treating clinician says so."),
    "Furosemide": ("Prescription diuretic", "Helps remove excess fluid in selected heart, kidney or liver conditions.", "Can alter hydration, blood pressure and electrolyte levels.", "Requires an individual plan and sometimes blood tests."),
    "Montelukast": ("Prescription allergy/asthma medicine", "Used in selected asthma or allergy treatment plans.", "Can cause mood, sleep or behaviour changes in some people; discuss new changes promptly.", "Not a substitute for a rescue inhaler in an asthma emergency."),
    "Gabapentin": ("Prescription nerve-pain/seizure medicine", "Used for selected nerve-pain conditions and seizure disorders.", "Can cause sleepiness and dizziness; stopping suddenly may be unsafe.", "Use only as prescribed and review sedating combinations."),
    "Methotrexate": ("Specialist prescription medicine", "Used for selected inflammatory and cancer conditions.", "Weekly-vs-daily errors can be dangerous; requires blood-test monitoring and pregnancy precautions.", "Follow the exact specialist instructions; never guess the schedule."),
}

CONDITIONS = {
    "Asthma": ("Respiratory", "A condition in which airways become inflamed and narrowed.", "Wheeze, cough, chest tightness or shortness of breath.", "Severe breathlessness, blue/grey lips, exhaustion, or difficulty speaking: seek emergency help.", "A clinician-created asthma action plan, trigger review and correct inhaler technique are important."),
    "Type 2 diabetes": ("Endocrine", "A long-term condition affecting blood glucose regulation.", "Increased thirst, frequent urination, tiredness; sometimes no early symptoms.", "Vomiting, confusion, deep/rapid breathing or severe drowsiness: emergency assessment.", "Care may include monitoring, food/activity support and prescribed medicines."),
    "High blood pressure": ("Cardiovascular", "Blood pressure that remains above the recommended range.", "Often no symptoms; measurement is needed.", "Chest pain, severe breathlessness, weakness on one side or sudden speech/vision changes: emergency help.", "Accurate repeat measurements and clinician review are important."),
    "Migraine": ("Neurological", "A neurological condition that can cause recurring headache attacks.", "Head pain, nausea, light/sound sensitivity; patterns vary.", "A sudden extremely severe headache, new weakness, confusion, fainting or vision loss needs urgent assessment.", "A headache diary can help a clinician identify patterns and treatment options."),
    "GERD / acid reflux": ("Digestive", "Stomach contents flow back into the food pipe and cause symptoms.", "Heartburn, sour taste or symptoms after meals/lying down.", "Chest pressure, breathlessness, sweating, or pain spreading to arm/jaw: emergency assessment.", "Persistent symptoms or swallowing difficulty should be reviewed."),
    "Anaemia": ("Blood", "A reduced ability of blood to carry oxygen, often related to low haemoglobin.", "Tiredness, weakness, pallor, dizziness or breathlessness on exertion.", "Chest pain, fainting or breathlessness at rest needs urgent assessment.", "A blood test is needed to identify the cause; do not assume it is iron deficiency."),
    "Hypothyroidism": ("Endocrine", "The thyroid gland does not make enough thyroid hormone.", "Fatigue, feeling cold, constipation or dry skin; symptoms are non-specific.", "Severe confusion, unusual coldness or reduced responsiveness needs emergency assessment.", "Diagnosis requires appropriate blood tests and clinician interpretation."),
    "Osteoarthritis": ("Musculoskeletal", "A joint condition involving changes to cartilage and surrounding tissues.", "Joint pain, stiffness and reduced movement.", "A hot swollen joint with fever or sudden inability to bear weight needs prompt care.", "Management is individual and may include movement support, physiotherapy and clinician-guided treatment."),
    "Depression": ("Mental wellbeing", "A health condition affecting mood, interest, energy and daily functioning.", "Persistent low mood, loss of interest, sleep or concentration changes.", "If someone may be in immediate danger or cannot stay safe, contact emergency services and a trusted adult/person now.", "Support from a qualified mental-health professional can help; it is treatable."),
    "Anxiety disorders": ("Mental wellbeing", "Conditions involving persistent or intense fear, worry or physical anxiety symptoms.", "Excessive worry, restlessness, tension, panic symptoms or avoidance.", "New chest pain, fainting or severe breathing difficulty needs medical assessment rather than assuming anxiety.", "Evidence-based psychological support and, when appropriate, clinician-prescribed treatment can help."),
    "Chronic kidney disease": ("Kidney", "Long-term reduction in kidney function or evidence of kidney damage.", "May have no symptoms early; later swelling, fatigue or urine changes.", "Very little urine, severe breathlessness, confusion or chest pain needs urgent assessment.", "Monitoring and medicine review are important; avoid unreviewed supplements or pain medicines."),
    "Urinary tract infection": ("Urinary", "An infection affecting part of the urinary system.", "Burning urination, urgency, frequency or lower abdominal discomfort.", "Fever with back/flank pain, vomiting, pregnancy or feeling very unwell needs prompt assessment.", "Testing may be needed; antibiotics are not appropriate without clinical assessment."),
    "Pneumonia": ("Respiratory", "An infection that inflames air sacs in one or both lungs.", "Cough, fever, chest discomfort and breathlessness.", "Severe breathlessness, blue/grey lips, confusion or collapse: emergency help.", "Assessment is important, especially for children, older adults and people with chronic illness."),
    "Dengue": ("Infectious disease", "A mosquito-borne viral infection found in some regions.", "Fever, aches, headache, nausea or rash.", "Severe abdominal pain, persistent vomiting, bleeding, unusual drowsiness or cold/clammy skin: urgent hospital care.", "Avoid self-medicating with aspirin or ibuprofen when dengue is possible; seek medical advice."),
    "Malaria": ("Infectious disease", "A mosquito-borne parasitic infection that can become severe.", "Fever, chills, headache, body aches; symptoms vary.", "Confusion, seizures, breathing difficulty, jaundice or collapse: emergency help.", "Fever after travel or in a malaria-risk area needs prompt testing and assessment."),
    "Tuberculosis (TB)": ("Infectious disease", "A bacterial infection that most often affects the lungs but can affect other organs.", "Cough lasting weeks, fever, night sweats, weight loss or blood in sputum.", "Severe breathlessness or coughing blood requires urgent care.", "Testing and completing the full clinician-supervised treatment plan are essential."),
    "Epilepsy": ("Neurological", "A condition involving a tendency to have recurrent unprovoked seizures.", "Seizures can look different; some involve staring or altered awareness.", "A seizure lasting 5 minutes, repeated seizures without recovery, injury or breathing difficulty: emergency help.", "A personalised seizure first-aid and treatment plan should be discussed with a clinician."),
    "Stroke": ("Neurological", "A medical emergency caused by interrupted blood flow or bleeding in the brain.", "Sudden face droop, arm weakness, speech difficulty, vision or balance changes.", "Any possible stroke symptom: call emergency services immediately, even if it improves.", "Note the time symptoms began; do not drive the person yourself if emergency transport is available."),
    "Heart attack": ("Cardiovascular", "A medical emergency involving reduced blood flow to heart muscle.", "Chest pressure/discomfort, breathlessness, sweating, nausea or pain in arm/jaw/back; symptoms vary.", "Suspected heart attack: call emergency services immediately.", "Do not delay care to use an online checker."),
    "Heart failure": ("Cardiovascular", "A condition in which the heart cannot pump or fill as effectively as the body needs.", "Breathlessness, leg swelling, fatigue or difficulty lying flat.", "Sudden severe breathlessness, fainting or chest pain: emergency help.", "A clinician-led plan and medication review are important."),
    "Eczema": ("Skin", "A group of conditions causing dry, inflamed and itchy skin.", "Dryness, itching, redness or recurrent rash.", "Rapidly spreading redness, fever, severe pain or facial swelling needs prompt care.", "Gentle skin care and clinician-guided treatment may help."),
    "Psoriasis": ("Skin", "An immune-mediated condition that can cause inflamed, scaly skin patches.", "Well-defined scaly patches; nails or joints may also be affected.", "A widespread painful rash with fever or a suddenly hot swollen joint needs prompt assessment.", "Treatment depends on severity and location; a dermatologist can advise."),
    "PCOS": ("Reproductive / endocrine", "A hormonal condition that can affect menstrual cycles and metabolism.", "Irregular periods, acne or excess hair growth; features vary.", "Severe sudden pelvic pain or very heavy bleeding with faintness needs urgent care.", "Diagnosis requires clinical assessment; symptoms can have other causes."),
    "Osteoporosis": ("Bone", "A condition in which bones become weaker and fracture risk increases.", "Often no symptoms until a fracture occurs.", "A suspected fracture or sudden severe back pain after a minor fall needs prompt assessment.", "Risk assessment and prevention are individualised."),
    "Gout": ("Joint", "An inflammatory arthritis caused by urate crystal deposits.", "Sudden painful, red, swollen joint, often at the big toe.", "A first hot swollen joint with fever needs urgent assessment to exclude infection.", "Long-term prevention and flare treatment need clinician guidance."),
    "Allergic reaction": ("Immune / allergy", "An immune response to a substance such as food, medicine or an insect sting.", "Itching, hives, sneezing or swelling.", "Tongue/throat swelling, breathing difficulty, faintness or collapse: possible anaphylaxis; call emergency services.", "People at risk should have a clinician-provided allergy emergency plan."),
}

SYMPTOM_GUIDES = {
    "Fever": ("Fever has many possible causes, including infections. Measure and record temperature if possible, rest and maintain fluids if able.", "Difficulty breathing, confusion, seizure, stiff neck, a non-fading rash, severe dehydration, or a very unwell infant: urgent/emergency care.", "A clinician can assess duration, age, associated symptoms and local infection risks."),
    "Cough": ("A cough may follow a viral infection or have other causes. Avoid smoke and note how long it has lasted.", "Severe breathlessness, blue/grey lips, chest pain, confusion or coughing blood: urgent assessment.", "Persistent cough, fever, wheeze or underlying illness should be reviewed."),
    "Headache": ("Note onset, duration, triggers and associated symptoms. Rest in a quiet place and drink fluids if appropriate.", "Sudden severe headache, weakness, confusion, fainting, fever with stiff neck, or vision loss: emergency assessment.", "New, worsening or recurring headaches deserve clinical review."),
    "Chest pain": ("Chest pain can have serious causes. Do not use an online tool to rule out a heart or lung emergency.", "Call emergency services now for new/unexplained chest pressure, breathlessness, sweating, faintness or pain spreading to arm/jaw/back.", "Do not drive yourself if a heart or lung emergency is possible."),
    "Abdominal pain": ("Record the location, onset, severity and associated vomiting, bowel or urinary symptoms.", "Severe or worsening pain, rigid abdomen, fainting, blood in vomit/stool, pregnancy with pain, or persistent vomiting: urgent care.", "A clinician may need to examine you; avoid relying on symptom matching."),
    "Diarrhoea": ("Fluids and correctly prepared ORS can help replace losses. Follow the packet mixing instructions.", "Blood/black stool, severe dehydration, confusion, severe pain or inability to keep fluids down: urgent care.", "Young children, older adults and people with chronic illness may need earlier review."),
    "Vomiting": ("Take small, frequent sips of fluid if you can. Note frequency and whether you can keep fluids down.", "Blood or green vomit, severe abdominal pain, confusion, severe dehydration or possible poisoning: urgent care.", "Persistent vomiting needs assessment to identify the cause."),
    "Rash": ("Avoid new products that may irritate the area and note when the rash began or any new medicines/foods.", "Rash with breathing difficulty, facial/tongue swelling, blistering, skin peeling, fever or rapid spread: urgent care.", "A photo and timeline can help a clinician assess the rash."),
    "Breathing difficulty": ("Sit upright and follow an existing clinician-provided action plan if you have one.", "Severe or sudden breathing difficulty, blue/grey lips, inability to speak normally, confusion or collapse: call emergency services now.", "Do not wait for an online result."),
    "Dizziness": ("Sit or lie somewhere safe and note whether it feels like spinning, faintness or imbalance.", "Fainting, chest pain, severe headache, new weakness, trouble speaking or difficulty walking: emergency assessment.", "Persistent or recurrent dizziness needs clinical review."),
    "Back pain": ("Note injury, location, duration and whether pain travels into a leg. Gentle normal movement may be appropriate if comfortable.", "New leg weakness, numbness around the groin, loss of bladder/bowel control, fever or major injury: emergency assessment.", "Persistent pain or pain after injury should be assessed."),
    "Urinary symptoms": ("Record burning, frequency, urgency, urine changes and any fever or back pain.", "Fever with flank pain, vomiting, pregnancy, confusion or feeling very unwell: prompt medical care.", "Testing may be needed; do not use leftover antibiotics."),
}

SPECIALISTS = {
    "Heart or circulation concern": "Cardiologist",
    "Skin, hair or nail concern": "Dermatologist",
    "Bones, joints or injury": "Orthopaedic specialist",
    "Diabetes or thyroid concern": "Endocrinologist",
    "Brain, headache or seizures": "Neurologist",
    "Mental or emotional wellbeing": "Mental-health professional",
    "Eyes or vision": "Ophthalmologist",
    "Ear, nose or throat": "ENT specialist",
    "Stomach or bowel concern": "Gastroenterologist",
    "Kidney or urinary concern": "Urologist / Nephrologist",
    "Child or adolescent health": "Paediatrician",
    "Pregnancy or menstrual concern": "Gynaecologist",
    "General or uncertain concern": "General physician",
}

# ----------------------------- UTILITIES -----------------------------
def init_state():
    defaults = {"health_log": [], "med_list": [], "clinic_list": [], "appointments": []}
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

def hero(kicker, title, subtitle):
    st.markdown(f"""<div class="hero"><div class="hero-kicker">{kicker}</div>
    <div class="hero-title">{title}</div><div class="hero-sub">{subtitle}</div></div>""", unsafe_allow_html=True)

def export_json(data):
    return json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")

def emergency_banner():
    st.error("🚨 **Medical emergency? Call 112 in India now.** For ambulance support, 108/102 may also operate in your state. Do not wait for this app or drive yourself if seriously unwell.")

init_state()

# ----------------------------- SIDEBAR -----------------------------
with st.sidebar:
    st.markdown("## 🩺 CLINIC PRO")
    st.caption("Your healthcare information companion")
    page = st.radio("WORKSPACE", [
        "Overview", "Symptom navigator", "Medicine encyclopedia",
        "Condition library", "Find a specialist", "Health journal",
        "Medication list", "Appointment planner", "About & safety"
    ], label_visibility="visible")
    st.divider()
    st.markdown("**Quick emergency access**")
    st.markdown("### ☎️ 112")
    st.caption("India emergency response number")
    st.caption("Built by Md Dilshad Amir")

# ----------------------------- OVERVIEW -----------------------------
if page == "Overview":
    hero("SMART HEALTHCARE COMPANION", "Care starts with clear information.", "Explore trusted health education, prepare for appointments and keep your personal notes organised — all in one place.")
    c1, c2, c3 = st.columns(3)
    c1.metric("Medicine references", len(MEDICINES))
    c2.metric("Health topics", len(CONDITIONS))
    c3.metric("Symptom guides", len(SYMPTOM_GUIDES))
    st.markdown("### Your workspace")
    tiles = [
        ("🧭", "Symptom navigator", "Understand warning signs and what information to share with a clinician."),
        ("💊", "Medicine encyclopedia", "Search medicine classes, general uses and important safety notes."),
        ("📚", "Condition library", "Browse plain-language information about common health conditions."),
        ("🩺", "Find a specialist", "Identify the type of professional who may assess a concern."),
        ("📝", "Health journal", "Keep a private session-based log of symptoms and measurements."),
        ("📅", "Appointment planner", "Prepare questions and organise upcoming appointments."),
    ]
    cols = st.columns(3)
    for i, (icon, name, desc) in enumerate(tiles):
        with cols[i % 3]:
            st.markdown(f'<div class="panel"><div style="font-size:1.6rem">{icon}</div><b>{name}</b><p class="small-muted">{desc}</p></div>', unsafe_allow_html=True)
    st.info("This app provides education and organisation tools. It does not diagnose, prescribe, replace a clinician, or monitor emergencies.")
    emergency_banner()

# ----------------------------- SYMPTOM NAVIGATOR -----------------------------
elif page == "Symptom navigator":
    hero("SAFETY FIRST", "Symptom navigator", "A structured way to understand warning signs and prepare useful information for a healthcare professional.")
    st.warning("This is not an AI diagnosis or a triage service. Symptoms can have many causes. If you are worried or symptoms are severe, seek medical care.")
    symptom = st.selectbox("Choose the symptom you want to learn about", list(SYMPTOM_GUIDES))
    onset = st.selectbox("When did it start?", ["Just now", "Today", "1–3 days ago", "4–7 days ago", "More than a week ago", "Not sure"])
    severity = st.select_slider("How severe does it feel?", options=["Mild", "Moderate", "Severe"])
    associated = st.multiselect("Are any of these also happening?", ["Breathing difficulty", "Chest pain", "Fainting or confusion", "New weakness or speech difficulty", "High fever", "Severe pain", "Repeated vomiting", "Blood in vomit or stool", "Pregnancy", "None of these"])
    details = st.text_area("Other details (optional)", placeholder="When it happens, what makes it better/worse, relevant history…")
    if st.button("Create appointment notes", use_container_width=True):
        urgent_flags = {"Breathing difficulty", "Chest pain", "Fainting or confusion", "New weakness or speech difficulty", "Blood in vomit or stool"}
        st.session_state["last_symptom_note"] = {
            "symptom": symptom, "onset": onset, "severity": severity,
            "associated": associated, "details": details, "created": datetime.now().isoformat(timespec="minutes")
        }
        if severity == "Severe" or urgent_flags.intersection(associated):
            emergency_banner()
        st.markdown("### Information to share with a clinician")
        st.write(f"**Main symptom:** {symptom}")
        st.write(f"**Started:** {onset} · **Reported severity:** {severity}")
        st.write(f"**Other symptoms:** {', '.join(associated) if associated else 'Not provided'}")
        if details: st.write(f"**Additional details:** {details}")
        st.success("Your notes are saved in this app session. Export them from the Health journal if needed.")
    st.divider()
    info, warning, review = SYMPTOM_GUIDES[symptom]
    st.markdown("#### General information")
    st.write(info)
    st.markdown("#### Warning signs")
    st.error(warning)
    st.markdown("#### When to seek advice")
    st.write(review)

# ----------------------------- MEDICINE ENCYCLOPEDIA -----------------------------
elif page == "Medicine encyclopedia":
    hero("REFERENCE LIBRARY", "Medicine encyclopedia", "Search common generic medicine names, their broad categories and key safety considerations.")
    st.warning("Medicine information is not a recommendation to take a drug. No dose or personal treatment advice is provided. Check the exact product and consult a pharmacist or prescriber.")
    query = st.text_input("Search by generic name or category", placeholder="Try: paracetamol, antibiotic, blood pressure…")
    matches = [(name, data) for name, data in MEDICINES.items() if query.lower() in name.lower() or query.lower() in data[0].lower() or query.lower() in data[1].lower()] if query else list(MEDICINES.items())
    st.caption(f"{len(matches)} reference entries")
    if matches:
        for name, data in matches:
            with st.expander(f"{name}  ·  {data[0]}"):
                st.write(data[1])
                st.markdown("**Important safety notes**")
                st.write(data[2])
                st.markdown("**Safe-use reminder**")
                st.info(data[3])
    else:
        st.info("No matching entry found in this offline reference library.")
    st.caption("The library is a starter reference, not a complete formulary. Brand names, strengths and approved uses vary by country.")

# ----------------------------- CONDITION LIBRARY -----------------------------
elif page == "Condition library":
    hero("HEALTH EDUCATION", "Condition library", "Plain-language overviews of common conditions, typical features and important warning signs.")
    category = st.selectbox("Filter by category", ["All"] + sorted({v[0] for v in CONDITIONS.values()}))
    search = st.text_input("Search condition", placeholder="Search a condition…")
    filtered = [(k, v) for k, v in CONDITIONS.items() if (category == "All" or v[0] == category) and (not search or search.lower() in k.lower() or search.lower() in v[1].lower())]
    st.caption(f"Showing {len(filtered)} of {len(CONDITIONS)} topics")
    for name, (cat, overview, features, redflags, care) in filtered:
        with st.expander(f"{name}  ·  {cat}"):
            st.write(overview)
            st.markdown("**Possible features**")
            st.write(features)
            st.markdown("**Warning signs**")
            st.error(redflags)
            st.markdown("**Care and follow-up**")
            st.write(care)
    st.caption("Symptoms overlap across many conditions. Only a qualified healthcare professional can assess and diagnose.")

# ----------------------------- SPECIALIST FINDER -----------------------------
elif page == "Find a specialist":
    hero("CARE DIRECTORY", "Find the right type of specialist", "Choose a concern to see which kind of healthcare professional commonly evaluates it.")
    concern = st.selectbox("What do you need help with?", list(SPECIALISTS))
    st.markdown(f'<div class="panel"><span class="pill">SUGGESTED SPECIALTY</span><h2 style="margin:.5rem 0">{SPECIALISTS[concern]}</h2><p class="small-muted">This is general navigation, not a diagnosis or referral.</p></div>', unsafe_allow_html=True)
    st.markdown("### Add a clinic or doctor you have independently verified")
    st.caption("This app does not invent or claim to verify provider listings. Enter details from a trusted source, then keep them in this session.")
    with st.form("clinic_form"):
        clinic_name = st.text_input("Clinic / doctor name")
        clinic_city = st.text_input("City / area")
        clinic_phone = st.text_input("Phone number (optional)")
        clinic_address = st.text_area("Address (optional)")
        submitted = st.form_submit_button("Save provider details")
        if submitted:
            if clinic_name.strip() and clinic_city.strip():
                st.session_state.clinic_list.append({"name": clinic_name.strip(), "city": clinic_city.strip(), "phone": clinic_phone.strip(), "address": clinic_address.strip(), "added": datetime.now().strftime("%Y-%m-%d %H:%M")})
                st.success("Provider details saved for this session.")
            else:
                st.error("Please enter at least the provider name and city.")
    if st.session_state.clinic_list:
        st.markdown("### Your saved provider notes")
        for i, item in enumerate(st.session_state.clinic_list):
            with st.expander(f"{item['name']} · {item['city']}"):
                st.write(item.get("address") or "No address entered")
                if item.get("phone"): st.write(f"Phone: {item['phone']}")
                st.caption("User-entered; not independently verified.")
                if st.button("Remove", key=f"remove_clinic_{i}"):
                    st.session_state.clinic_list.pop(i)
                    st.rerun()
    else:
        st.info("No provider details saved yet.")

# ----------------------------- HEALTH JOURNAL -----------------------------
elif page == "Health journal":
    hero("PERSONAL NOTES", "Health journal", "Record observations to help you communicate clearly with your healthcare team.")
    with st.form("journal_form"):
        log_date = st.date_input("Date", value=date.today())
        log_type = st.selectbox("Entry type", ["Symptom", "Temperature", "Blood pressure", "Blood glucose", "Pulse", "Other"])
        value = st.text_input("Observation / value", placeholder="Example: headache after school; 37.8 °C")
        notes = st.text_area("Context or notes", placeholder="Time, activity, meals, medicines already prescribed, questions…")
        save = st.form_submit_button("Add to journal")
        if save:
            if value.strip():
                st.session_state.health_log.append({"date": str(log_date), "type": log_type, "value": value.strip(), "notes": notes.strip()})
                st.success("Entry added to this session's journal.")
            else:
                st.error("Please add an observation or value.")
    st.markdown("### Recent entries")
    if st.session_state.health_log:
        for i, item in enumerate(reversed(st.session_state.health_log)):
            st.markdown(f'<div class="panel"><b>{item["date"]} · {item["type"]}</b><p>{item["value"]}</p><span class="small-muted">{item["notes"]}</span></div>', unsafe_allow_html=True)
        st.download_button("Export journal as JSON", export_json(st.session_state.health_log), "clinic_pro_health_journal.json", "application/json")
    else:
        st.info("Your journal is empty. Entries remain in this browser session unless you export them.")
    st.caption("Do not enter passwords, identity numbers or information you do not want stored in the current app session.")

# ----------------------------- MEDICATION LIST -----------------------------
elif page == "Medication list":
    hero("MEDICINE ORGANISER", "My medication list", "Keep a simple record of medicines that a qualified professional has already recommended or prescribed.")
    st.warning("This is a list organiser, not a prescribing tool or interaction checker. Never start, stop, share or change a medicine based on this page.")
    with st.form("med_form"):
        med_name = st.text_input("Medicine name as written on the package / prescription")
        reason = st.text_input("Reason it was prescribed (optional)")
        instructions = st.text_input("Prescriber / label instructions (optional)", placeholder="Copy exactly; do not guess")
        prescriber = st.text_input("Prescriber or pharmacy (optional)")
        add = st.form_submit_button("Add medicine")
        if add:
            if med_name.strip():
                st.session_state.med_list.append({"name": med_name.strip(), "reason": reason.strip(), "instructions": instructions.strip(), "prescriber": prescriber.strip()})
                st.success("Added to your session list.")
            else:
                st.error("Enter the medicine name.")
    if st.session_state.med_list:
        for i, item in enumerate(st.session_state.med_list):
            with st.expander(item["name"]):
                if item["reason"]: st.write(f"Reason: {item['reason']}")
                if item["instructions"]: st.write(f"Instructions copied from label: {item['instructions']}")
                if item["prescriber"]: st.write(f"Prescriber / pharmacy: {item['prescriber']}")
                if st.button("Remove from list", key=f"remove_med_{i}"):
                    st.session_state.med_list.pop(i)
                    st.rerun()
        st.download_button("Export medication list", export_json(st.session_state.med_list), "clinic_pro_medication_list.json", "application/json")
    else:
        st.info("No medicines added.")

# ----------------------------- APPOINTMENT PLANNER -----------------------------
elif page == "Appointment planner":
    hero("VISIT PREPARATION", "Appointment planner", "Organise your visit, collect questions and remember what you want to discuss.")
    with st.form("appointment_form"):
        appt_date = st.date_input("Appointment date", value=date.today())
        appt_time = st.text_input("Time (optional)", placeholder="e.g. 10:30 AM")
        clinician = st.text_input("Doctor / clinic")
        reason = st.text_input("Main reason for visit")
        questions = st.text_area("Questions to ask", placeholder="1. What could be causing this?\n2. What tests may be needed?\n3. What warning signs should I watch for?")
        docs = st.text_area("Things to bring", placeholder="Previous reports, prescriptions, allergy list…")
        save_appt = st.form_submit_button("Save appointment plan")
        if save_appt:
            st.session_state.appointments.append({"date": str(appt_date), "time": appt_time, "clinician": clinician, "reason": reason, "questions": questions, "bring": docs})
            st.success("Appointment plan saved in this session.")
    if st.session_state.appointments:
        st.markdown("### Saved plans")
        for i, a in enumerate(st.session_state.appointments):
            with st.expander(f"{a['date']} · {a['clinician'] or 'Appointment'}"):
                st.write(f"**Reason:** {a['reason'] or 'Not specified'}")
                st.write(f"**Time:** {a['time'] or 'Not specified'}")
                st.write(f"**Questions:** {a['questions'] or 'None added'}")
                st.write(f"**Bring:** {a['bring'] or 'None added'}")
        st.download_button("Export appointment plans", export_json(st.session_state.appointments), "clinic_pro_appointments.json", "application/json")

# ----------------------------- ABOUT & SAFETY -----------------------------
elif page == "About & safety":
    hero("TRANSPARENCY", "About CLINIC PRO", "A practical healthcare education and organisation project by Md Dilshad Amir.")
    st.markdown("### What this app can do")
    st.markdown("""
    - Provide plain-language educational information about selected conditions.
    - Show general medicine reference information and safety reminders.
    - Help users recognise warning signs that need urgent professional attention.
    - Help prepare notes for a medical appointment.
    - Organise user-entered health observations and medication lists during a session.
    - Help identify the type of specialist who may assess a concern.
    """)
    st.markdown("### What this app cannot do")
    st.markdown("""
    - Diagnose a disease, interpret a scan or laboratory result, or predict an individual's outcome.
    - Prescribe medicines, calculate doses, recommend stopping treatment, or check all drug interactions.
    - Verify doctors, clinics, pharmacies or medical credentials.
    - Replace emergency services or a qualified healthcare professional.
    """)
    st.markdown("### Privacy")
    st.info("This version stores entries in Streamlit session state. They may disappear when the session ends or the app restarts. Export anything you need to keep. Before public deployment, add secure authentication, encrypted database storage, access controls, consent, retention rules and a privacy policy.")
    st.markdown("### Medical content quality")
    st.warning("Before publishing for public use, have all medical content reviewed by licensed clinicians and pharmacists in the target country. Add source citations, review dates, a content owner and a process for correcting errors.")
    st.markdown("### Emergency help in India")
    emergency_banner()
    st.caption("Emergency numbers and service availability can vary by state and location. If 112 is unavailable, use the locally recognised ambulance service.")

st.markdown('<div class="footer">CLINIC PRO · Healthcare information, organisation and appointment preparation<br>Educational use only · Not a substitute for professional medical care · © 2026</div>', unsafe_allow_html=True)
