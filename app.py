from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3
import joblib
from datetime import datetime
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = "mediai_secret_key"
DATABASE = "hospital.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE, check_same_thread=False)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT UNIQUE,
        password TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient TEXT,
        doctor TEXT,
        department TEXT,
        date TEXT,
        time TEXT,
        reason TEXT
    )
    """)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS medicine_requests(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        patient TEXT,
        disease TEXT,
        language TEXT,
        requested_at TEXT
    )
    """)
    conn.commit()
    conn.close()


init_db()

@app.context_processor
def inject_user():
    return {"current_user": session.get("user")}

CONDITION_OPTIONS = [
    "Fever",
    "Cold",
    "Headache",
    "Cough",
    "Asthma",
    "Hypertension",
    "Diabetes",
    "Gastric Pain",
    "Skin Rash",
    "Allergy",
    "Back Pain",
    "Pediatric Infection",
]

MEDICINE_PRESCRIPTIONS = {
    "Fever": {
        "english": "Medicine: Paracetamol 500mg. Usage: Take one tablet twice daily after food, drink plenty of fluids, and rest. If fever stays above 102°F or lasts more than 3 days, consult your physician.",
        "telugu": "మందు: పారాసెటమాల్ 500mg. ఉపయోగం: భోజనం తర్వాత రోజుకు రెండు సార్లు టాబ్లెట్ తీసుకోండి, తగినంత ద్రవాలు తాగండి మరియు విశ్రాంతి తీసుకోండి. జ్వరం 102°F పైగా ఉంటే లేదా 3 రోజులకు మించి కొనసాగితే వైద్యుడిని సంప్రదించండి.",
        "hindi": "दवा: पैरासिटामोल 500mg. उपयोग: भोजन के बाद दिन में दो बार टैबलेट लें, पर्याप्त तरल पदार्थ पिएं और आराम करें। बुखार 102°F से ऊपर रहे या 3 दिनों से अधिक हो जाए तो चिकित्सक से संपर्क करें।",
    },
    "Cold": {
        "english": "Medicine: Cetirizine 10mg. Usage: Take one tablet daily in the evening, use steam inhalation twice a day, and keep hydrated to ease congestion.",
        "telugu": "మందు: సిటిరిజీన్ 10mg. ఉపయోగం: సాయంత్రం రోజుకు ఒక టాబ్లెట్ తీసుకోండి, రోజు రెండు సార్లు ఆవిరి శ్వాస తీసుకోండి మరియు జలుబు ఉపశమనం కోసం తగినంత ద్రవాలు తాగండి.",
        "hindi": "दवा: सेटिरिज़िन 10mg. उपयोग: शाम को दिन में एक बार टैबलेट लें, दिन में दो बार स्टीम इनहेलेशन करें और जकड़न को कम करने के लिए हाइड्रेटेड रहें।",
    },
    "Headache": {
        "english": "Medicine: Ibuprofen 200mg. Usage: Take one tablet after meals, up to three times a day. Apply a cold compress and rest if pain persists.",
        "telugu": "మందు: ఐబుప్రొఫెన్ 200mg. ఉపయోగం: భోజనం తర్వాత ఒక టాబ్లెట్ తీసుకోండి, రోజుకు ఎక్కువగా మూడు సార్లు వరకు. నొప్పి ఉంటే చల్లని కంప్రెస్ పెట్టండి మరియు విశ్రాంతి తీసుకోండి.",
        "hindi": "दवा: आइबुप्रोफेन 200mg. उपयोग: भोजन के बाद एक टैबलेट लें, दिन में अधिकतम तीन बार। दर्द बना रहे तो ठंडी पट्टी लगाकर आराम करें।",
    },
    "Cough": {
        "english": "Medicine: Dextromethorphan cough syrup. Usage: Take 10ml at bedtime and sip warm fluids throughout the day. Avoid irritants and keep the throat moist.",
        "telugu": "మందు: డెక్స్ట్రోమెథార్ఫాన్ దగ్గు సిరప్. ఉపయోగం: నిద్రకు ముందు 10ml తీసుకోండి మరియు రోజంతా వేడి ద్రవాలు తాగండి. జీర్ణకోశాలను దూరంగా ఉంచండి మరియు గొంతును తేమగా ఉంచండి.",
        "hindi": "दवा: डेक्सट्रोमेथोर्फ़न कफ सिरप. उपयोग: सोने से पहले 10ml लें और दिन भर गर्म तरल पदार्थ पीएं। जलन से बचें और गले को नम रखें।",
    },
    "Asthma": {
        "english": "Medicine: Use your prescribed inhaler. Usage: Take 1-2 puffs as directed when symptoms start, usually twice daily for maintenance. Seek urgent review if wheezing or shortness of breath worsens.",
        "telugu": "మందు: మీ సూచించిన ఇన్హేలర్ ఉపయోగించండి. ఉపయోగం: లక్షణాలు మొదలవగానే 1-2 పఫ్స్ తీసుకోండి, సాధారణంగా నిర్వహణ కోసం రోజులో రెండు సార్లు. ఊపిరిత్యాగం లేదా శ్వాసలో ఇబ్బంది పెరిగితే వెంటనే వైద్యుడిని సంప్రదించండి.",
        "hindi": "दवा: अपने निर्धारित इनहेलर का उपयोग करें। उपयोग: लक्षण शुरू होते ही 1-2 पफ्स लें, आमतौर पर रखरखाव के लिए दिन में दो बार। यदि वींझिंग या सांस लेने में कठिनाई बढ़े तो तुरंत चिकित्सक से मिलें।",
    },
    "Hypertension": {
        "english": "Medicine: Continue prescribed blood pressure medication. Usage: Take daily at the same time, monitor your blood pressure regularly, and report dizziness or headache to your doctor.",
        "telugu": "మందు: మీ సూచించిన రక్తపోటు మందును కొనసాగించండి. ఉపయోగం: ప్రతిరోజూ ఒకే సమయంలో తీసుకోండి, మీ రక్తపోటును పర్యవేక్షించండి, మరియు తలనొప్పి లేదా తిమ్మిరాలు ఉన్నట్లయితే వైద్యుడికి తెలియజేయండి.",
        "hindi": "दवा: निर्धारित उच्च रक्तचाप की दवा जारी रखें। उपयोग: रोज़ एक ही समय पर लें, अपने रक्तचाप की नियमित रूप से निगरानी करें, और चक्कर या सिरदर्द होने पर अपने डॉक्टर को बताएं।",
    },
    "Diabetes": {
        "english": "Medicine: Follow your prescribed diabetes treatment. Usage: Monitor fasting and post-meal blood sugar, take medication exactly as directed, maintain a balanced diet, and review results with your physician.",
        "telugu": "మందు: మీ సూచించిన డయాబెటిస్ చికిత్సను పాటించండి. ఉపయోగం: ఉపవాసపు మరియు భోజనానంతర బ్లడ్ షుగర్‌ను పర్యవేక్షించండి, మందును నిష్కర్షగా తీసుకోండి, సమతుల్య ఆహారాన్ని పాటించండి, మరియు ఫలితాలను వైద్యుడితో సమీక్షించండి.",
        "hindi": "दवा: अपनी निर्धारित मधुमेह चिकित्सा का पालन करें। उपयोग: उपवास और भोजन के बाद रक्त शर्करा की निगरानी करें, दवा को ठीक उसी तरह लें जैसा निर्देशित किया गया है, संतुलित आहार बनाए रखें, और परिणामों की समीक्षा अपने चिकित्सक के साथ करें।",
    },
    "Gastric Pain": {
        "english": "Medicine: Antacid tablets or syrup. Usage: Take after meals, avoid spicy and fried foods, and drink small amounts of water often.",
        "telugu": "మందు: యాంటాసిడ్ టాబ్లెట్లు లేదా సిరప్. ఉపయోగం: భోజనం తర్వాత తీసుకోండి, మసాలా మరియు వేగించిన ఆహారాన్ని తప్పించండి, మరియు తరచుగా చిన్న మొత్తంలో నీళ్లు తాగండి.",
        "hindi": "दवा: एंटासिड टैबलेट या सिरप। उपयोग: भोजन के बाद लें, मसालेदार और तली हुई चीजों से बचें, और अक्सर थोड़ा पानी पिएं।",
    },
    "Skin Rash": {
        "english": "Medicine: Mild topical cream or lotion. Usage: Apply to clean, dry skin twice daily, avoid scratching, and consult dermatology if rash persists.",
        "telugu": "మందు: మృదువైన టాపికల్ క్రీమ్ లేదా లోషన్. ఉపయోగం: శుభ్రం చేసిన, ఎడారి చర్మంపై రోజుకు రెండు సార్లు వరలాగే వేయండి, కొట్టుకోకుండా ఉండండి, మరియు ర్యాష్ నిలిచితే డెర్మటాలజీని సంప్రదించండి.",
        "hindi": "दवा: हल्का टॉपिकल क्रीम या लोशन। उपयोग: साफ, सूखी त्वचा पर दिन में दो बार लगाएँ, खुजलाने से बचें, और अगर रैश बना रहता है तो त्वचा विशेषज्ञ से परामर्श करें।",
    },
    "Allergy": {
        "english": "Medicine: Antihistamine tablet. Usage: Take once daily, avoid known allergens, and seek medical care if breathing becomes difficult.",
        "telugu": "మందు: యాంటీహిస్టామిన్ టాబ్లెట్. ఉపయోగం: రోజుకు ఒకసారి తీసుకోండి, తెలిసిన అలెర్జెన్లను దూరంగా ఉంచండి, మరియు శ్వాస తీసుకోవడంలో ఇబ్బంది ఉంటే వైద్య సహాయం తీసుకోండి.",
        "hindi": "दवा: एंटीहिस्टामाइन टैबलेट। उपयोग: दिन में एक बार लें, ज्ञात एलर्जी से बचें, और यदि सांस लेने में कठिनाई हो तो चिकित्सा सहायता लें।",
    },
    "Back Pain": {
        "english": "Medicine: Pain relief tablet. Usage: Take one tablet after food up to three times daily, use a warm compress, and perform gentle stretches. Seek care if pain worsens or lasts more than a week.",
        "telugu": "మందు: నొప్పి నిరోధక టాబ్లెట్. ఉపయోగం: భోజనం తర్వాత ఒక టాబ్లెట్ తీసుకోండి, రోజుకు ఎక్కువగా మూడు సార్లు వరకు; వేడి కంప్రెస్ ఉపయోగించండి మరియు మృదువుగా వ్యాయామాలు చేయండి. నొప్పి పెరిగితే లేదా ఒక వారానికి మించి కొనసాగితే వైద్యుడిని సంప్రదించండి.",
        "hindi": "दवा: दर्द निवारक टैबलेट। उपयोग: भोजन के बाद एक टैबलेट लें, दिन में अधिकतम तीन बार, गर्म सेक का उपयोग करें और हल्के स्ट्रेच करें। यदि दर्द बढ़े या एक सप्ताह से अधिक रहता है तो देखभाल लें।",
    },
    "Pediatric Infection": {
        "english": "Medicine: Pediatric fever reducer and hydration support. Usage: Give the child fluids often, use the medicine per weight-based dosing, monitor temperature regularly, and contact pediatric care if fever persists.",
        "telugu": "మందు: పిల్లల జ్వర తగ్గించే మందు మరియు హైడ్రేషన్ మద్దతు. ఉపయోగం: పిల్లకు తరచుగా ద్రవాలు ఇవ్వండి, బరువు ఆధారిత డోసింగ్ ప్రకారం మందును ఉపయోగించండి, జ్వరాన్ని తరచుగా పర్యవేక్షించండి, మరియు జ్వరం నిలిచితే పిల్లల వైద్యునిని సంప్రదించండి.",
        "hindi": "दवा: शिशु बुखार घटाने वाली दवा और हाइड्रेशन सहयोग। उपयोग: बच्चे को बार-बार तरल पदार्थ दें, वजन आधारित खुराक के अनुसार दवा दें, तापमान नियमित रूप से जांचें, और बुखार जारी रहने पर बाल रोग देखभाल से संपर्क करें।",
    },
}


def assess_general_condition(condition, age, temperature, duration, pain_level, cough_level, breath_difficulty, nausea_level):
    age = int(age or 0)
    temperature = float(temperature or 0)
    duration = int(duration or 0)
    pain_level = int(pain_level or 0)
    cough_level = int(cough_level or 0)
    breath_difficulty = int(breath_difficulty or 0)
    nausea_level = int(nausea_level or 0)

    if condition == "Diabetes":
        if model:
            return None
        return "Diabetes assessment model is unavailable. Please consult a specialist for an accurate diagnosis."

    if condition == "Fever":
        if temperature >= 100.4 or duration >= 3:
            return "High likelihood of fever. See a doctor if temperature stays elevated or symptoms persist beyond 48 hours."
        return "Mild fever symptoms. Rest, hydration, and monitoring should help recovery."

    if condition == "Cold":
        if cough_level >= 5 or temperature >= 100.4:
            return "Active cold infection likely. Keep hydrated, rest, and consult if cough worsens."
        return "Mild cold symptoms. Home care is usually effective with rest and fluids."

    if condition == "Headache":
        if pain_level >= 6 and duration >= 2:
            return "Persistent headache likely requires medical review. Please seek consultation if pain does not improve."
        return "Tension headache symptoms are low to moderate. Rest and hydration are recommended."

    if condition == "Cough":
        if cough_level >= 6 or breath_difficulty >= 4:
            return "Severe cough symptoms detected. Please consult your doctor, especially if breathing is affected."
        return "Mild cough signs. Keep airways clear and stay hydrated."

    if condition == "Asthma":
        if breath_difficulty >= 5 or cough_level >= 5:
            return "Asthma flare-up likely. Use your inhaler and seek urgent review if breathing difficulty persists."
        return "Stable asthma symptoms. Continue prescribed asthma care and avoid triggers."

    if condition == "Hypertension":
        if age >= 40 and pain_level >= 4 and duration >= 2:
            return "Possible blood pressure concerns. Monitor readings and consult your physician for a check-up."
        return "General hypertension risk is low to moderate. Maintain healthy diet and regular monitoring."

    if condition == "Gastric Pain":
        if nausea_level >= 5 or duration >= 3:
            return "Gastric distress is likely. Avoid spicy foods, eat small meals, and consult if pain persists."
        return "Mild gastric discomfort. Simple dietary adjustments and hydration should help."

    if condition == "Skin Rash":
        if duration >= 4 or pain_level >= 5:
            return "Persistent rash detected. Dermatology consultation is advised if symptoms do not improve."
        return "Mild skin irritation. Keep the area clean and avoid irritants."

    if condition == "Allergy":
        if cough_level >= 4 or breath_difficulty >= 3:
            return "Allergic reaction likely. Use an antihistamine and seek medical guidance if symptoms worsen."
        return "Mild allergy signs. Avoid triggers and consider an antihistamine."

    if condition == "Back Pain":
        if pain_level >= 6 or duration >= 5:
            return "Severe back pain may need clinical review. Use gentle mobility and consult if pain persists."
        return "Moderate back pain. Gentle movement and rest should support recovery."

    if condition == "Pediatric Infection":
        if temperature >= 100.4 or duration >= 2:
            return "Possible pediatric infection. Keep the child hydrated and seek pediatric review if fever continues."
        return "Mild childhood illness symptoms. Monitor closely and maintain fluid intake."

    return "Condition assessment complete. If you feel unwell, see a medical professional for personalized care."

# =========================
# LOAD MODEL
# =========================

try:
    model = joblib.load("models/diabetes_model.pkl")
except Exception:
    model = None

# =========================
# HOME PAGE
# =========================

@app.route('/')
def home():
    return render_template("index.html", title="MediAI Healthcare Portal")

# =========================
# REGISTER
# =========================

@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ""

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE email = ?", (email,))
        existing = cursor.fetchone()

        if existing:
            message = "Email already registered. Please login."
        else:
            hashed_password = generate_password_hash(password)
            cursor.execute(
                "INSERT INTO users(name,email,password) VALUES(?,?,?)",
                (name, email, hashed_password),
            )
            conn.commit()
            conn.close()
            return redirect(url_for('login'))

        conn.close()

    return render_template(
        "register.html",
        title="Patient Registration",
        message=message,
        back_url=url_for('home'),
    )

# =========================
# LOGIN
# =========================

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ""

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE email=?",
            (email,),
        )
        user = cursor.fetchone()

        if user:
            stored_password = user['password']
            password_valid = False

            if stored_password.startswith('pbkdf2:sha256:'):
                password_valid = check_password_hash(stored_password, password)
            elif stored_password == password:
                password_valid = True
                cursor.execute(
                    "UPDATE users SET password = ? WHERE id = ?",
                    (generate_password_hash(password), user['id']),
                )
                conn.commit()

            if password_valid:
                session['user'] = user['name']
                conn.close()
                return redirect(url_for('dashboard'))

        conn.close()
        message = "Invalid email or password."

    return render_template(
        "login.html",
        title="Secure Login",
        message=message,
        back_url=url_for('home'),
    )

# =========================
# DASHBOARD
# =========================

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    cursor = conn.cursor()
    appointments = cursor.execute(
        "SELECT * FROM appointments WHERE patient = ? ORDER BY date, time",
        (session['user'],),
    ).fetchall()
    conn.close()

    return render_template(
        "dashboard.html",
        title="Patient Dashboard",
        appointments=appointments,
        back_url=url_for('home'),
    )

# =========================
# APPOINTMENT
# =========================

@app.route('/appointment', methods=['GET', 'POST'])
def appointment():
    if 'user' not in session:
        return redirect(url_for('login'))

    message = ""
    patient = session['user']

    if request.method == 'POST':
        patient = request.form['patient']
        doctor = request.form['doctor']
        department = request.form['department']
        date = request.form['date']
        time = request.form['time']
        reason = request.form['reason']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO appointments(patient, doctor, department, date, time, reason)
            VALUES(?,?,?,?,?,?)
            """,
            (patient, doctor, department, date, time, reason),
        )
        conn.commit()
        conn.close()

        message = f"Appointment confirmed with {doctor} on {date} at {time}."

    return render_template(
        "appointment.html",
        title="Consultation Booking",
        message=message,
        patient=patient,
        back_url=url_for('dashboard'),
    )

# =========================
# DISEASE PREDICTION
# =========================

@app.route('/prediction', methods=['GET', 'POST'])
def prediction():
    result = ""
    selected_condition = "Fever"

    if request.method == 'POST':
        selected_condition = request.form.get('condition', 'Fever')
        age = request.form.get('age', 0)
        temperature = request.form.get('temperature', 0)
        duration = request.form.get('duration', 0)
        pain_level = request.form.get('pain_level', 0)
        cough_level = request.form.get('cough_level', 0)
        breath_difficulty = request.form.get('breath_difficulty', 0)
        nausea_level = request.form.get('nausea_level', 0)

        if selected_condition == "Diabetes" and model:
            try:
                values = [
                    float(request.form.get('pregnancies', 0) or 0),
                    float(request.form.get('glucose', 0) or 0),
                    float(request.form.get('bloodpressure', 0) or 0),
                    float(request.form.get('skinthickness', 0) or 0),
                    float(request.form.get('insulin', 0) or 0),
                    float(request.form.get('bmi', 0) or 0),
                    float(request.form.get('dpf', 0) or 0),
                    float(request.form.get('age', 0) or 0),
                ]
                prediction = model.predict([values])
                result = (
                    "High risk of diabetes. Please consult your physician promptly."
                    if prediction[0] == 1
                    else "Low risk of diabetes. Maintain a healthy diet and regular exercise."
                )
            except ValueError:
                result = "Please enter valid numeric values for the diabetes-specific inputs."
        else:
            result = assess_general_condition(
                selected_condition,
                age,
                temperature,
                duration,
                pain_level,
                cough_level,
                breath_difficulty,
                nausea_level,
            )

    return render_template(
        "prediction.html",
        title="Clinical Assessment",
        result=result,
        condition=selected_condition,
        conditions=CONDITION_OPTIONS,
        back_url=url_for('dashboard') if 'user' in session else url_for('home'),
    )

# =========================
# MEDICINE RECOMMENDATION
# =========================

@app.route('/medicine', methods=['GET', 'POST'])
def medicine():
    output = ""
    selected_disease = "Fever"

    if request.method == 'POST':
        selected_disease = request.form['disease']
        language = request.form['language']
        output = MEDICINE_PRESCRIPTIONS.get(selected_disease, {}).get(
            language,
            "Please choose a valid condition and language.",
        )

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO medicine_requests(patient, disease, language, requested_at)
            VALUES(?,?,?,?)
            """,
            (session.get('user', 'Guest'), selected_disease, language, datetime.now().isoformat()),
        )
        conn.commit()
        conn.close()

    return render_template(
        "medicine.html",
        title="Medication Guidance",
        output=output,
        diseases=CONDITION_OPTIONS,
        selected_disease=selected_disease,
        back_url=url_for('dashboard') if 'user' in session else url_for('home'),
    )

# =========================
# EMERGENCY

@app.route('/emergency')
def emergency():
    if 'user' not in session:
        return redirect(url_for('login'))

    return render_template(
        "emergency.html",
        title="Emergency Response",
        back_url=url_for('dashboard'),
    )

# =========================
# LOGOUT
# =========================

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('home'))

# =========================
# RUN
# =========================

if __name__ == '__main__':
    app.run(debug=True)