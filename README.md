# MediAI Healthcare Portal - README.md

````md
# 🏥 MediAI Healthcare Portal

MediAI Healthcare Portal is an AI-powered healthcare management web application developed using Flask, SQLite, and Machine Learning.  
The system provides patient registration, appointment booking, disease prediction, multilingual medicine recommendations, and emergency healthcare support.

---

# 🚀 Features

## 👤 User Authentication
- Patient Registration
- Secure Login System
- Session Management
- Logout Functionality

## 📅 Appointment Booking
- Book appointments with doctors
- Select department, date, and time
- Store appointment records in database

## 🤖 AI Disease Prediction
- Symptom-based disease assessment
- Diabetes prediction using Machine Learning model
- General condition analysis using intelligent rule-based system

## 💊 Medicine Recommendation System
- Medicine suggestions based on selected disease
- Multi-language support:
  - English
  - Telugu
  - Hindi

## 🚑 Emergency Support
- Emergency healthcare assistance page
- Quick navigation for urgent situations

## 🗄️ Database Management
- SQLite database integration
- Stores:
  - Users
  - Appointments
  - Medicine requests

---

# 🛠️ Technologies Used

| Technology | Purpose |
|------------|---------|
| Python | Backend Development |
| Flask | Web Framework |
| SQLite | Database |
| HTML/CSS | Frontend UI |
| Joblib | ML Model Loading |
| Machine Learning | Diabetes Prediction |

---

# 📂 Project Structure

```bash
MediAI/
│
├── app.py
├── hospital.db
├── requirements.txt
│
├── models/
│   └── diabetes_model.pkl
│
├── templates/
│   ├── index.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── appointment.html
│   ├── prediction.html
│   ├── medicine.html
│   └── emergency.html
│
├── static/
│   ├── style.css
│   └── images/
│
└── README.md
````

---

# ⚙️ Installation Guide

## Step 1: Clone Repository

```bash
git clone https://github.com/yourusername/medi-ai-healthcare.git
cd medi-ai-healthcare
```

---

## Step 2: Install Required Packages

```bash
pip install -r requirements.txt
```

---

# 📦 Required Libraries

```txt
Flask
joblib
scikit-learn
numpy
pandas
```

---

## Step 3: Run Application

```bash
python app.py
```

---

## Step 4: Open Browser

```bash
http://127.0.0.1:5000
```

---

# 🧠 Machine Learning Model

The application uses a trained Diabetes Prediction Model stored in:

```bash
models/diabetes_model.pkl
```

The model predicts diabetes risk based on:

* Glucose Level
* Blood Pressure
* BMI
* Age
* Insulin
* Skin Thickness
* Diabetes Pedigree Function

---

# 🌐 Supported Languages

The medicine recommendation system supports:

* English
* Telugu
* Hindi

---

# 🔒 Security Features

* Session-based authentication
* Unique email registration
* Protected dashboard routes

---

# 📸 Screens Included

* Home Page
* Login/Register
* Dashboard
* Appointment Booking
* Disease Prediction
* Medicine Recommendation
* Emergency Page

---

# 📈 Future Enhancements

* Online Doctor Consultation
* Payment Gateway Integration
* Email Notifications
* AI Chatbot Support
* Hospital Admin Dashboard
* Cloud Deployment
* Voice Assistant Integration

---

# 👨‍💻 Developed By

Kagga Shiva Krishna

---

# 📄 License

This project is developed for educational and academic purposes.

---

# ⭐ Conclusion

MediAI Healthcare Portal demonstrates the integration of Artificial Intelligence and Web Development in healthcare systems.
The project helps improve accessibility, disease prediction, and patient management using modern technologies.

```
```
