# ClassVision — AI-Powered Face Recognition Attendance Platform

ClassVision is a smart attendance management system that uses **computer vision and facial recognition** to automate classroom attendance.  
The project includes:

- a **stable desktop application** built with **Tkinter + OpenCV**
- an **experimental web platform** using **Flask + Next.js + MongoDB + DeepFace**

---

# Features

## Desktop Application (Recommended)
- Student registration using webcam image capture
- Face recognition–based attendance marking
- LBPH face recognizer using OpenCV
- Automatic attendance CSV generation
- Subject-wise attendance summaries
- Lightweight and works offline

## Web Platform (Experimental)
- Student and teacher dashboards
- AI-powered face recognition using DeepFace + MTCNN
- Session-based attendance workflows
- MongoDB-based student and attendance storage
- REST API backend with Flask
- Modern frontend built with Next.js

---

# Tech Stack

## Desktop App
- Python
- Tkinter
- OpenCV
- NumPy
- Pandas

## Web App

### Backend
- Flask
- MongoDB
- DeepFace
- TensorFlow
- MTCNN
- OpenCV

### Frontend
- Next.js
- TypeScript
- Tailwind CSS

---

# Screenshots

## Main Dashboard

![Main UI](Project%20Snap/1.PNG)

---

# Getting Started — Desktop Application

## Prerequisites
- Python 3.9+
- Webcam

---

## Setup

```bash
# Create virtual environment
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Run the Desktop App

```bash
python attendance.py
```

---

# How to Use

## 1. Register Student
Enter:
- Enrollment Number
- Student Name

Then capture multiple face samples using the webcam.

Press:

```text
q
```

to stop image capture early.

---

## 2. Train the Model

Click:

```text
Train Image
```

This generates:

```text
TrainingImageLabel/Trainner.yml
```

---

## 3. Take Attendance

Click:

```text
Take Attendance
```

Enter the subject name.

Attendance CSV files are automatically saved under:

```text
Attendance/<subject>/
```

---

## 4. View Attendance Summary

The system generates:

```text
attendance_summary.csv
```

containing attendance percentage calculations per student.

---

# Troubleshooting

## `cv2.face` Not Found

Install OpenCV contrib package:

```bash
pip install opencv-contrib-python
```

---

## Camera Not Opening

Close applications using the webcam:
- Zoom
- Google Meet
- Microsoft Teams

Then restart the application.

---

## Poor Recognition Accuracy

- Capture more training images
- Ensure proper lighting
- Use multiple face angles
- Keep face clearly visible to the webcam

---

# Web Application (Experimental)

The repository also includes a full-stack web version.

---

# Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate environment

# Windows
.venv\Scripts\activate

# macOS/Linux
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
```

Edit `.env` and add your MongoDB URI:

```env
MONGODB_URI=your_mongodb_uri
```

Then run:

```bash
python app.py
```

Backend runs on:

```text
http://127.0.0.1:5000
```

---

# Frontend Setup

```bash
cd frontend

npm install
npm run dev
```

Frontend runs on:

```text
http://localhost:3000
```

---

# Security Notes

- Never commit `.env` files to GitHub
- Never expose MongoDB credentials publicly
- Training images and generated attendance data are excluded using `.gitignore`

---

# Future Improvements

- Real-time classroom attendance analytics
- Cloud deployment support
- Face anti-spoofing detection
- Multi-camera support
- Admin analytics dashboard
- Email attendance reports

---

# Built By

**Harbani Kaur**

GitHub:  
https://github.com/harbani007