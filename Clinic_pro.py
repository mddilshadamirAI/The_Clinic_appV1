import streamlit as st
import sqlite3
import pandas as pd
import requests
import json
import os
from datetime import datetime, date, timedelta

# ============================================================
# CLINIC PRO - HEALTH ORGANISER & EDUCATION APP
# ============================================================

st.set_page_config(
    page_title="Clinic Pro | Health Companion",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

DB_NAME = "clinic_pro.db"

# ---------------------- DATABASE ----------------------------

def db():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    con = db()
    cur = con.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS journal (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entry_date TEXT,
            category TEXT,
            title TEXT,
            notes TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS health_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_date TEXT,
            metric TEXT,
            value TEXT,
            unit TEXT,
            notes TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            prescribed_by TEXT,
            notes TEXT,
            added_date TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            appointment_date TEXT,
            doctor TEXT,
            location TEXT,
            reason TEXT,
            notes TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS profile (
            id INTEGER PRIMARY KEY,
            display_name TEXT,
            age_group TEXT,
            emergency_contact TEXT,
            notes TEXT
        )
    """)

    con.commit()
    con.close()

def read_table(table):
    allowed = {
        "journal", "health_logs", "medicines",
        "appointments", "profile"
    }
    if table not in allowed:
        return pd.DataFrame()

    con = db()
    try:
        return pd.read_sql_query(
            f"SELECT * FROM {table} ORDER BY id DESC",
            con
        )
    finally:
        con.close()

def execute(query, values=()):
    con = db()
    try:
        cur = con.cursor()
        cur.execute(query, values)
        con.commit()
    finally:
        con.close()

init_db()

# ---------------------- DESIGN -------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: linear-gradient(135deg, #071c26 0%, #0b2932 55%, #102e36 100%);
    color: #f1f7f8;
}

section[data-testid="stSidebar"] {
    background: #071720;
    border-right: 1px solid #24444d;
}

section[data-testid="stSidebar"] * {
    color: #e9f5f6;
}

h1, h2, h3 {
    color: #f2ffff;
    font-weight: 800;
}

p, label, span {
    color: #d1e1e5;
}

div[data-testid="stMetric"] {
    background: #12333d;
    border: 1px solid #28505a;
    padding: 18px;
    border-radius: 16px;
}

.stButton button {
    background: #13a89e;
    color: white;
    border: 0;
    border-radius: 11px;
    font-weight: 700;
    padding: 10px 18px;
}

.stButton button:hover {
    background: #0d8c84;
    color: white;
}

div[data-testid="stForm"] {
    background: #102e38;
    padding: 18px;
    border-radius: 15px;
    border: 1px solid #294b55;
}

input, textarea {
    border-radius: 9px !important;
}

div[data-testid="stExpander"] {
    background: #102e38;
    border: 1px solid #294b55;
    border-radius: 12px;
}

hr {
    border-color: #31515b;
}

.small-note {
    color: #a9c5cc;
    font-size: 13px;
}

.hero {
    background: linear-gradient(120deg, #0e726f, #12434f);
    border: 1px solid #277e7a;
    border-radius: 20px;
    padding: 25px;
    margin-bottom: 20px;
}

.hero h1 {
    margin-bottom: 5px;
}

.info-card {
    background: #102e38;
    border: 1px solid #294b55;
    border-radius: 15px;
    padding: 17px;
    margin-bottom: 12px;
}
</style>
""", unsafe_allow_html=True)

# ---------------------- HEALTH TOPICS ------------------------

TOPICS = [
("Common Cold", "A common viral infection affecting the nose and throat. Symptoms may include congestion, sneezing and cough."),
("Influenza", "A viral respiratory illness. Symptoms can include fever, cough, fatigue and body aches."),
("Asthma", "A condition involving inflammation and narrowing of the airways. A clinician can help create an asthma action plan."),
("Diabetes", "A group of conditions affecting blood glucose regulation. Regular professional monitoring is important."),
("High Blood Pressure", "Blood pressure that remains higher than recommended. It often has no obvious symptoms."),
("Low Blood Pressure", "Blood pressure lower than usual. Symptoms such as dizziness should be discussed with a clinician."),
("Anaemia", "A condition involving reduced healthy red blood cells or haemoglobin."),
("Migraine", "A neurological condition that can cause recurring headaches and other symptoms."),
("Tension Headache", "A common headache type often associated with pressure or tightness."),
("Acid Reflux", "Stomach contents moving back towards the food pipe, sometimes causing heartburn."),
("Gastroenteritis", "Inflammation of the stomach and intestines, often causing diarrhoea or vomiting."),
("Constipation", "Difficulty passing stools or having bowel movements less often than usual."),
("Diarrhoea", "Loose or watery stools. Dehydration is an important concern."),
("Urinary Tract Infection", "An infection affecting parts of the urinary system. Medical assessment may be needed."),
("Kidney Stones", "Hard deposits that can form in the kidneys and may cause significant pain."),
("Thyroid Disorders", "Conditions affecting thyroid hormone production and body functions."),
("Arthritis", "A broad term for conditions affecting joints, sometimes causing pain and stiffness."),
("Osteoporosis", "A condition that weakens bones and increases fracture risk."),
("Eczema", "A group of skin conditions that can cause dryness, irritation and itching."),
("Psoriasis", "A long-term inflammatory skin condition that can cause scaly patches."),
("Allergies", "Immune-system reactions to substances that are usually harmless to most people."),
("Sinusitis", "Inflammation of the sinuses, sometimes following a respiratory infection."),
("Pneumonia", "An infection affecting the lungs. Breathing difficulty needs urgent assessment."),
("Tuberculosis", "An infectious disease that most commonly affects the lungs and requires medical treatment."),
("Dengue", "A mosquito-borne viral illness. Warning signs require urgent medical attention."),
("Malaria", "A mosquito-borne infection that can become serious and needs prompt medical assessment."),
("Chickenpox", "A contagious viral illness that commonly causes an itchy rash."),
("Measles", "A contagious viral disease that can cause fever and rash."),
("Conjunctivitis", "Inflammation of the eye's outer membrane, sometimes causing redness or discharge."),
("Ear Infection", "An infection or inflammation affecting parts of the ear."),
("Obesity", "A complex health condition influenced by many biological, environmental and social factors."),
("Vitamin D Deficiency", "Low vitamin D levels can affect bone and muscle health."),
("Vitamin B12 Deficiency", "Low B12 levels can affect blood cells and the nervous system."),
("Iron Deficiency", "Insufficient iron can affect haemoglobin production."),
("Sleep Disorders", "Conditions that affect sleep quality, timing or duration."),
("Anxiety Disorders", "Mental health conditions involving excessive fear or worry that affects daily life."),
("Depression", "A mental health condition that can affect mood, interest, sleep and everyday functioning."),
("Panic Attacks", "Episodes of intense fear or discomfort that can involve physical symptoms."),
("Heart Disease", "A broad group of conditions affecting the heart and blood vessels."),
("Stroke", "A medical emergency involving interrupted blood flow to part of the brain."),
("Heart Attack", "A medical emergency involving reduced blood flow to heart muscle."),
("Chronic Kidney Disease", "Long-term reduction in kidney function requiring professional monitoring."),
("Liver Disease", "A broad term for conditions affecting liver structure or function."),
("Gallstones", "Hardened deposits that can form in the gallbladder."),
("PCOS", "Polycystic ovary syndrome is a hormonal condition requiring individual medical assessment."),
("Endometriosis", "A condition in which tissue similar to the uterine lining grows outside the uterus."),
("Menstrual Health", "Menstrual patterns vary. Severe or disruptive symptoms deserve medical attention."),
("Oral Health", "Healthy teeth and gums are supported by regular dental care and oral hygiene."),
("Dental Cavities", "Damage to tooth structure caused by acids produced by bacteria."),
("Dehydration", "A lack of adequate body fluids. Severe dehydration can be dangerous."),
("Heat Exhaustion", "A heat-related illness that can involve weakness, headache and heavy sweating.")
]

# ---------------------- SYMPTOM GUIDES -----------------------

SYMPTOMS = [
("Fever", "Raised body temperature can occur with infections and other conditions.", "Seek urgent help for confusion, breathing difficulty, seizures or severe deterioration."),
("Headache", "Headaches have many possible causes.", "Sudden extremely severe headache, weakness, confusion or vision changes need urgent assessment."),
("Chest discomfort", "Chest discomfort can have several causes.", "New or severe chest pain, breathlessness, fainting or sweating requires emergency help."),
("Cough", "Cough can occur with respiratory infections, allergies and other conditions.", "Breathing difficulty, blue lips or coughing blood needs urgent assessment."),
("Breathlessness", "Breathing difficulty can have many causes.", "Severe or sudden breathing difficulty is an emergency."),
("Sore throat", "Throat irritation may occur with viral infections or other conditions.", "Difficulty breathing or swallowing saliva needs urgent medical attention."),
("Stomach pain", "Abdominal pain can have digestive or other causes.", "Severe pain, fainting, blood in vomit or a rigid abdomen needs urgent assessment."),
("Vomiting", "Vomiting can occur with infections and other conditions.", "Inability to keep fluids down, confusion or signs of severe dehydration need urgent help."),
("Diarrhoea", "Loose stools can be caused by infections, food and other conditions.", "Blood in stool, severe dehydration or severe abdominal pain needs medical assessment."),
("Dizziness", "Dizziness can relate to many different causes.", "Fainting, chest pain, weakness or difficulty speaking requires urgent help."),
("Rash", "Rashes may result from irritation, allergy or infection.", "A rash with breathing difficulty, facial swelling or serious illness is an emergency."),
("Itching", "Itching can be related to skin irritation, allergy or other conditions.", "Facial or tongue swelling or breathing difficulty requires emergency help."),
("Eye redness", "Red eyes can have several causes.", "Eye pain, vision loss, injury or severe light sensitivity needs urgent assessment."),
("Ear pain", "Ear pain may occur with infection or irritation.", "Swelling behind the ear, severe illness or sudden hearing loss needs urgent assessment."),
("Back pain", "Back pain has many possible causes.", "New leg weakness, loss of bladder or bowel control or major injury needs emergency assessment."),
("Joint pain", "Joint pain may follow injury or occur with inflammatory conditions.", "A hot swollen joint with fever needs prompt medical assessment."),
("Fatigue", "Tiredness can be linked to sleep, stress or medical conditions.", "Fainting, chest pain or severe sudden weakness needs urgent assessment."),
("Palpitations", "A feeling of a racing or irregular heartbeat can have different causes.", "Palpitations with chest pain, fainting or breathlessness need emergency help."),
("Swelling", "Swelling can occur due to injury, inflammation or fluid retention.", "Sudden facial swelling or swelling with breathing difficulty is an emergency."),
("Nosebleed", "Nosebleeds are common and often stop with basic first aid.", "Heavy bleeding, faintness or bleeding that does not stop needs medical help."),
("Toothache", "Tooth pain can result from cavities, infection or injury.", "Facial swelling, fever or difficulty swallowing needs urgent dental or medical care."),
("Burn", "Burns vary in seriousness depending on depth and area.", "Large, deep, chemical or electrical burns need urgent professional care."),
("Injury", "Injuries may affect skin, bones, muscles or other tissues.", "Major injury, severe bleeding, loss of consciousness or breathing difficulty is an emergency."),
("Dehydration signs", "Thirst, dry mouth and reduced urination can be signs of dehydration.", "Confusion, fainting or inability to drink requires urgent medical care."),
("Sleep problems", "Sleep difficulties may relate to routine, stress or health conditions.", "If sleep problems significantly affect daily life, discuss them with a healthcare professional.")
]

# ---------------------- MEDICINE LIBRARY ---------------------

FALLBACK_MEDICINES = [
    "Paracetamol", "Ibuprofen", "Amoxicillin", "Azithromycin",
    "Cetirizine", "Loratadine", "Metformin", "Insulin",
    "Omeprazole", "Pantoprazole", "Amlodipine", "Losartan",
    "Atorvastatin", "Salbutamol", "Montelukast", "ORS",
    "Ferrous sulfate", "Folic acid", "Vitamin B12", "Vitamin D",
    "Calcium carbonate", "Levothyroxine", "Aspirin", "Clopidogrel",
    "Cefixime", "Cefuroxime", "Doxycycline", "Fluconazole",
    "Metronidazole", "Ondansetron", "Loperamide", "Lactulose",
    "Mupirocin", "Hydrocortisone", "Clotrimazole", "Acyclovir",
    "Dextromethorphan", "Guaifenesin", "Chlorpheniramine",
    "Fexofenadine", "Esomeprazole", "Famotidine", "Domperidone",
    "Prednisolone", "Hydroxychloroquine", "Warfarin",
    "Enalapril", "Bisoprolol", "Rosuvastatin", "Sitagliptin"
]

@st.cache_data(ttl=86400, show_spinner=False)
def load_medicines(limit=500):
    results = []
    seen = set()

    # Built-in reference names first
    for name in FALLBACK_MEDICINES:
        key = name.lower()
        if key not in seen:
            seen.add(key)
            results.append({
                "name": name,
                "brand": "",
                "purpose": "",
                "warnings": "",
                "source": "Built-in reference list"
            })

    # Retrieve additional generic names from OpenFDA
    try:
        url = "https://api.fda.gov/drug/label.json"
        skip = 0

        while len(results) < limit and skip < 25000:
            params = {
                "limit": 100,
                "skip": skip,
                "search": "openfda.generic_name:*"
            }

            response = requests.get(
                url, params=params, timeout=15
            )

            if response.status_code != 200:
                break

            payload = response.json()
            batch = payload.get("results", [])

            if not batch:
                break

            for item in batch:
                fda = item.get("openfda", {})
                names = fda.get("generic_name", [])
                brands = fda.get("brand_name", [])

                if not names:
                    continue

                name = str(names[0]).strip()
                key = name.lower()

                if not name or key in seen:
                    continue

                seen.add(key)

                purpose = item.get("purpose", [""])
                warnings = item.get("warnings", [""])

                results.append({
                    "name": name,
                    "brand": str(brands[0]) if brands else "",
                    "purpose": str(purpose[0])[:700] if purpose else "",
                    "warnings": str(warnings[0])[:700] if warnings else "",
                    "source": "US FDA label database"
                })

                if len(results) >= limit:
                    break

            skip += len(batch)

            if len(batch) < 100:
                break

    except Exception:
        pass

    return results[:limit]

# ---------------------- SIDEBAR ------------------------------

with st.sidebar:
    st.markdown("# 🏥 Clinic Pro")
    st.caption("Your health information companion")
    st.divider()

    page = st.radio(
        "NAVIGATION",
        [
            "🏠 Dashboard",
            "💊 Medicine Library",
            "📚 Health Topics",
            "🩺 Symptom Guides",
            "📔 Health Journal",
            "📊 Health Tracker",
            "🗂️ Medicine Organiser",
            "📅 Appointments",
            "👤 My Profile",
            "📥 Export My Data",
            "🚨 Emergency Help",
            "ℹ️ About & Safety"
        ]
    )

    st.divider()
    st.caption("Clinic Pro • Local health organiser")

# ---------------------- DASHBOARD ---------------------------

if page == "🏠 Dashboard":
    st.markdown("""
    <div class="hero">
        <h1>Welcome to Clinic Pro 👋</h1>
        <p>Your personal health organiser and health education companion.</p>
    </div>
    """, unsafe_allow_html=True)

    journals = read_table("journal")
    logs = read_table("health_logs")
    meds = read_table("medicines")
    appointments = read_table("appointments")

    a, b, c, d = st.columns(4)

    a.metric("Journal entries", len(journals))
    b.metric("Health records", len(logs))
    c.metric("Medicine records", len(meds))
    c.metric("Appointments", len(appointments))

    st.markdown("### ✨ Explore your health companion")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
        <div class="info-card">
        <h3>💊 Medicine Library</h3>
        Search medicine reference information and safety labels.
        </div>
        <div class="info-card">
        <h3>📚 Health Education</h3>
        Explore 50 health topics in simple language.
        </div>
        <div class="info-card">
        <h3>🩺 Symptom Guides</h3>
        Learn about common symptoms and warning signs.
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown("""
        <div class="info-card">
        <h3>📊 Health Tracker</h3>
        Record health measurements over time.
        </div>
        <div class="info-card">
        <h3>📅 Appointment Planner</h3>
        Keep your healthcare appointments organised.
        </div>
        <div class="info-card">
        <h3>📔 Health Journal</h3>
        Keep notes to discuss with a healthcare professional.
        </div>
        """, unsafe_allow_html=True)

    st.markdown("### 📅 Upcoming appointments")

    if not appointments.empty:
        upcoming = appointments[
            appointments["appointment_date"] >= date.today().isoformat()
        ]
        if not upcoming.empty:
            st.dataframe(
                upcoming[["appointment_date", "doctor", "reason"]],
                use_container_width=True,
                hide_index=True
            )
        else:
            st.info("No upcoming appointments recorded.")
    else:
        st.info("You have not added any appointments yet.")

    st.markdown("### 🛡️ Important")
    st.warning(
        "Clinic Pro is an educational and organisational tool. "
        "It does not diagnose conditions, prescribe medicines, "
        "or replace a qualified healthcare professional."
    )

# ---------------------- MEDICINE LIBRARY ---------------------

elif page == "💊 Medicine Library":
    st.title("💊 Medicine Reference Library")
    st.write("Search generic medicine names and available label information.")

    with st.spinner("Loading medicine references..."):
        medicines = load_medicines(500)

    st.metric("Available references", len(medicines))

    df = pd.DataFrame(medicines)
    query = st.text_input("🔎 Search medicine name")

    if query:
        filtered = df[
            df["name"].str.contains(query, case=False, na=False)
            | df["brand"].str.contains(query, case=False, na=False)
        ]
    else:
        filtered = df

    st.caption(f"Showing {len(filtered)} matching references")

    page_size = 25
    total_pages = max(1, (len(filtered) - 1) // page_size + 1)

    page_number = st.number_input(
        "Page",
        min_value=1,
        max_value=total_pages,
        value=1,
        step=1
    )

    start = (page_number - 1) * page_size
    visible = filtered.iloc[start:start + page_size]

    for _, item in visible.iterrows():
        with st.expander(str(item["name"])):
            if item["brand"]:
                st.write("**Listed brand:**", item["brand"])

            if item["purpose"]:
                st.write("**Label purpose:**")
                st.write(item["purpose"])

            if item["warnings"]:
                st.write("**Label warnings:**")
                st.write(item["warnings"])

            st.caption("Source: " + str(item["source"]))

    st.download_button(
        "⬇️ Download medicine reference CSV",
        data=filtered.to_csv(index=False).encode("utf-8"),
        file_name="clinic_pro_medicine_references.csv",
        mime="text/csv"
    )

    st.info(
        "Medicine labels may be from the US FDA and may not match "
        "Indian product labels. This library is for education only. "
        "It does not provide doses, prescriptions or interaction checks. "
        "Always verify a medicine with a pharmacist or doctor."
    )

# ---------------------- HEALTH TOPICS -----------------------

elif page == "📚 Health Topics":
    st.title("📚 Health Education Library")
    st.write("Explore 50 introductory health topics.")

    query = st.text_input("Search health topics")

    for title, description in TOPICS:
        if query.lower() in title.lower() or query.lower() in description.lower():
            with st.expander(title):
                st.write(description)
                st.caption(
                    "Educational overview only. A healthcare professional "
                    "can provide advice for an individual situation."
                )

    st.caption(f"{len(TOPICS)} health topics available.")

# ---------------------- SYMPTOM GUIDES -----------------------

elif page == "🩺 Symptom Guides":
    st.title("🩺 Symptom Information Guides")
    st.write("Learn about common symptoms and when to seek help.")

    query = st.text_input("Search a symptom")

    for name, explanation, warning in SYMPTOMS:
        if query.lower() in name.lower() or query.lower() in explanation.lower():
            with st.expander(name):
                st.write("**General information**")
                st.write(explanation)

                st.write("**Warning signs**")
                st.error(warning)

                st.caption(
                    "This guide cannot identify the cause of a symptom. "
                    "Do not delay medical assessment when symptoms are serious."
                )

    st.warning(
        "For a medical emergency in India, call 112 or seek emergency care."
    )

# ---------------------- HEALTH JOURNAL ----------------------

elif page == "📔 Health Journal":
    st.title("📔 Health Journal")
    st.write("Save observations and notes to discuss with a healthcare professional.")

    with st.form("journal_form"):
        entry_date = st.date_input("Date", value=date.today())
        category = st.selectbox(
            "Category",
            ["General", "Symptoms", "Appointment Notes",
             "Questions for Doctor", "Recovery Notes", "Other"]
        )
        title = st.text_input("Entry title")
        notes = st.text_area("Your notes", height=150)

        submitted = st.form_submit_button("💾 Save journal entry")

        if submitted:
            if title.strip() or notes.strip():
                execute(
                    """INSERT INTO journal
                    (entry_date, category, title, notes)
                    VALUES (?, ?, ?, ?)""",
                    (
                        entry_date.isoformat(),
                        category,
                        title.strip(),
                        notes.strip()
                    )
                )
                st.success("Journal entry saved.")
            else:
                st.error("Please enter a title or some notes.")

    st.divider()
    st.subheader("Your saved entries")

    data = read_table("journal")

    if not data.empty:
        for _, row in data.iterrows():
            with st.expander(
                f"{row['entry_date']} — {row['title'] or row['category']}"
            ):
                st.write("Category:", row["category"])
                st.write(row["notes"])

                if st.button("Delete entry", key=f"journal_{row['id']}"):
                    execute(
                        "DELETE FROM journal WHERE id=?",
                        (int(row["id"]),)
                    )
                    st.rerun()
    else:
        st.info("Your journal is currently empty.")

# ---------------------- HEALTH TRACKER ----------------------

elif page == "📊 Health Tracker":
    st.title("📊 Health Tracker")
    st.write("Record measurements that you want to discuss with your clinician.")

    with st.form("tracker_form"):
        log_date = st.date_input("Record date", value=date.today())

        metric = st.selectbox(
            "Measurement",
            [
                "Blood pressure",
                "Pulse",
                "Temperature",
                "Weight",
                "Blood glucose",
                "Oxygen saturation",
                "Other"
            ]
        )

        value = st.text_input(
            "Reading",
            placeholder="Enter the reading shown by your device"
        )

        unit = st.text_input(
            "Unit",
            placeholder="For example: bpm, °C, kg, %"
        )

        notes = st.text_area("Additional notes")

        submitted = st.form_submit_button("Save measurement")

        if submitted:
            if value.strip():
                execute(
                    """INSERT INTO health_logs
                    (log_date, metric, value, unit, notes)
                    VALUES (?, ?, ?, ?, ?)""",
                    (
                        log_date.isoformat(),
                        metric,
                        value.strip(),
                        unit.strip(),
                        notes.strip()
                    )
                )
                st.success("Measurement saved.")
            else:
                st.error("Please enter a reading.")

    st.divider()
    st.subheader("Your recorded measurements")

    data = read_table("health_logs")

    if not data.empty:
        st.dataframe(data, use_container_width=True, hide_index=True)

        selected = st.selectbox(
            "View measurement trend",
            sorted(data["metric"].dropna().unique())
        )

        trend = data[data["metric"] == selected].copy()
        trend["numeric_value"] = pd.to_numeric(
            trend["value"], errors="coerce"
        )
        trend = trend.dropna(subset=["numeric_value"])

        if not trend.empty:
            trend["log_date"] = pd.to_datetime(trend["log_date"])
            trend = trend.sort_values("log_date")
            st.line_chart(
                trend.set_index("log_date")["numeric_value"]
            )
        else:
            st.info("Trend chart needs numeric readings.")

        if st.button("Delete all health records"):
            execute("DELETE FROM health_logs")
            st.rerun()
    else:
        st.info("No measurements have been recorded yet.")

    st.caption(
        "This tracker stores readings; it does not interpret them "
        "or determine whether they are safe."
    )

# ---------------------- MEDICINE ORGANISER -------------------

elif page == "🗂️ Medicine Organiser":
    st.title("🗂️ Medicine Organiser")
    st.write(
        "Keep a private list of medicines that have been prescribed "
        "or recommended by your healthcare professional."
    )

    with st.form("medicine_form"):
        name = st.text_input("Medicine name")
        prescribed_by = st.text_input("Prescribed or recommended by")
        notes = st.text_area(
            "Notes",
            placeholder="Optional notes from your healthcare professional"
        )

        submitted = st.form_submit_button("Add medicine record")

        if submitted:
            if name.strip():
                execute(
                    """INSERT INTO medicines
                    (name, prescribed_by, notes, added_date)
                    VALUES (?, ?, ?, ?)""",
                    (
                        name.strip(),
                        prescribed_by.strip(),
                        notes.strip(),
                        date.today().isoformat()
                    )
                )
                st.success("Medicine record added.")
            else:
                st.error("Enter a medicine name.")

    st.divider()
    data = read_table("medicines")

    if not data.empty:
        st.dataframe(data, use_container_width=True, hide_index=True)

        for _, row in data.iterrows():
            with st.expander(str(row["name"])):
                st.write("Healthcare professional:", row["prescribed_by"])
                st.write("Notes:", row["notes"])

                if st.button("Delete record", key=f"med_{row['id']}"):
                    execute(
                        "DELETE FROM medicines WHERE id=?",
                        (int(row["id"]),)
                    )
                    st.rerun()
    else:
        st.info("No medicine records yet.")

    st.warning(
        "This is an organiser, not a medication reminder or prescription. "
        "Do not start, stop or change a medicine based on this app."
    )

# ---------------------- APPOINTMENTS -------------------------

elif page == "📅 Appointments":
    st.title("📅 Appointment Planner")

    with st.form("appointment_form"):
        appointment_date = st.date_input(
            "Appointment date",
            value=date.today() + timedelta(days=1)
        )
        doctor = st.text_input("Doctor or clinic")
        location = st.text_input("Location")
        reason = st.text_input("Reason for appointment")
        notes = st.text_area("Questions or notes to remember")

        submitted = st.form_submit_button("Save appointment")

        if submitted:
            if doctor.strip() or reason.strip():
                execute(
                    """INSERT INTO appointments
                    (appointment_date, doctor, location, reason, notes)
                    VALUES (?, ?, ?, ?, ?)""",
                    (
                        appointment_date.isoformat(),
                        doctor.strip(),
                        location.strip(),
                        reason.strip(),
                        notes.strip()
                    )
                )
                st.success("Appointment saved.")
            else:
                st.error("Enter a doctor or appointment reason.")

    st.divider()
    data = read_table("appointments")

    if not data.empty:
        st.dataframe(data, use_container_width=True, hide_index=True)

        for _, row in data.iterrows():
            with st.expander(
                f"{row['appointment_date']} — {row['doctor'] or 'Appointment'}"
            ):
                st.write("Location:", row["location"])
                st.write("Reason:", row["reason"])
                st.write("Notes:", row["notes"])

                if st.button("Delete appointment", key=f"appt_{row['id']}"):
                    execute(
                        "DELETE FROM appointments WHERE id=?",
                        (int(row["id"]),)
                    )
                    st.rerun()
    else:
        st.info("No appointments saved.")

# ---------------------- PROFILE ------------------------------

elif page == "👤 My Profile":
    st.title("👤 My Profile")
    st.write("Optional profile information for organising your records.")

    existing = read_table("profile")

    if not existing.empty:
        profile = existing.iloc[0]
        old_name = profile["display_name"] or ""
        old_age = profile["age_group"] or "Prefer not to say"
        old_contact = profile["emergency_contact"] or ""
        old_notes = profile["notes"] or ""
    else:
        old_name = ""
        old_age = "Prefer not to say"
        old_contact = ""
        old_notes = ""

    with st.form("profile_form"):
        display_name = st.text_input("Display name", value=old_name)

        age_group = st.selectbox(
            "Age group",
            [
                "Prefer not to say",
                "Under 18",
                "18–29",
                "30–44",
                "45–59",
                "60+"
            ],
            index=[
                "Prefer not to say",
                "Under 18",
                "18–29",
                "30–44",
                "45–59",
                "60+"
            ].index(old_age) if old_age in [
                "Prefer not to say", "Under 18", "18–29",
                "30–44", "45–59", "60+"
            ] else 0
        )

        emergency_contact = st.text_input(
            "Emergency contact (optional)",
            value=old_contact
        )

        notes = st.text_area("Other notes", value=old_notes)

        submitted = st.form_submit_button("Save profile")

        if submitted:
            execute("""
                INSERT OR REPLACE INTO profile
                (id, display_name, age_group, emergency_contact, notes)
                VALUES (1, ?, ?, ?, ?)
            """, (
                display_name.strip(),
                age_group,
                emergency_contact.strip(),
                notes.strip()
            ))
            st.success("Profile saved.")

    st.warning(
        "Your profile and health records are stored locally in a database "
        "file on this device. Avoid entering passwords, identity numbers "
        "or other highly sensitive information."
    )

# ---------------------- EXPORT DATA --------------------------

elif page == "📥 Export My Data":
    st.title("📥 Export Your Data")
    st.write("Download records saved by this app.")

    tables = [
        "journal",
        "health_logs",
        "medicines",
        "appointments",
        "profile"
    ]

    export_data = {}

    for table in tables:
        export_data[table] = read_table(table).to_dict(orient="records")

    json_data = json.dumps(
        export_data,
        indent=2,
        ensure_ascii=False,
        default=str
    )

    st.download_button(
        "⬇️ Download complete JSON backup",
        data=json_data,
        file_name="clinic_pro_backup.json",
        mime="application/json"
    )

    st.divider()
    st.subheader("Download individual CSV files")

    for table in tables:
        df = read_table(table)

        st.download_button(
            f"Download {table}.csv",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name=f"clinic_pro_{table}.csv",
            mime="text/csv",
            key=f"export_{table}"
        )

    st.divider()
    st.subheader("Delete local records")

    st.warning(
        "Deleting records cannot be undone. Download a backup first "
        "if you may need these records later."
    )

    confirm = st.checkbox("I understand that deleting records is permanent.")

    if st.button("Delete all app records", disabled=not confirm):
        for table in tables:
            execute(f"DELETE FROM {table}")
        st.success("App records deleted.")
        st.rerun()

# ---------------------- EMERGENCY HELP -----------------------

elif page == "🚨 Emergency Help":
    st.title("🚨 Emergency Help")

    st.error(
        "If someone is seriously unwell, do not rely on this app. "
        "Contact emergency services or go to the nearest emergency department."
    )

    st.markdown("### 🇮🇳 India emergency number")
    st.markdown("# 112")
    st.write("112 is India's pan-India emergency response number.")

    st.markdown("### Warning signs that need emergency help")

    warning_signs = [
        "Severe or sudden difficulty breathing",
        "Chest pain with faintness or breathlessness",
        "Unconsciousness or inability to wake someone",
        "Sudden weakness or difficulty speaking",
        "Severe allergic reaction with breathing difficulty",
        "Major injury or uncontrolled bleeding",
        "Seizure or sudden severe confusion"
    ]

    for item in warning_signs:
        st.markdown(f"- {item}")

    st.markdown("### What to tell emergency services")
    st.markdown("""
    - Your location and a callback number.
    - What happened.
    - Whether the person is conscious and breathing normally.
    - Any known immediate danger.
    - Follow the emergency operator's instructions.
    """)

    st.info(
        "Do not delay emergency care to fill in forms or search this app."
    )

# ---------------------- ABOUT & SAFETY -----------------------

elif page == "ℹ️ About & Safety":
    st.title("ℹ️ About Clinic Pro")

    st.markdown("""
    ### What is Clinic Pro?

    Clinic Pro is a health education and personal record organiser.
    It helps users:

    - Explore introductory health information.
    - Search medicine label references.
    - Record health observations.
    - Organise appointments.
    - Maintain a health journal.
    - Export their own records.

    ### Important medical limitations

    Clinic Pro is NOT:

    - A doctor or hospital.
    - A diagnostic system.
    - A prescription service.
    - A medicine dose calculator.
    - A medicine interaction checker.
    - An emergency response service.

    Never start, stop or change medication based on information in this app.
    Ask a qualified healthcare professional or pharmacist.

    ### Data and privacy

    - Records are stored in a local SQLite database.
    - The database is not encrypted by this app.
    - Anyone with access to the device and database file may be able to read it.
    - The medicine library may contact the OpenFDA public API.
    - Do not enter passwords, identity numbers or highly sensitive information.

    ### Medicine data source

    The online medicine reference attempts to retrieve public US FDA drug-label
    information through OpenFDA. It may not represent medicines marketed in India.
    Always verify the actual product label with a pharmacist or clinician.

    ### Educational information

    Health topic and symptom descriptions are introductory summaries.
    They are not a substitute for individual medical advice.
    """)

    st.markdown("---")
    st.caption("Clinic Pro • Personal Health Organiser")

# ---------------------- FOOTER -------------------------------

st.sidebar.divider()
st.sidebar.caption("🛡️ Educational use only")
st.sidebar.caption("Not a substitute for professional medical care.")
