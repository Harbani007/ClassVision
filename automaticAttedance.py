import csv
import os
import sys
import time
import datetime
from pathlib import Path

import cv2
import pandas as pd
import tkinter as tk
from tkinter import *

BASE_DIR = Path(__file__).resolve().parent

haarcasecade_path = str(BASE_DIR / "haarcascade_frontalface_default.xml")
trainimagelabel_path = str(BASE_DIR / "TrainingImageLabel" / "Trainner.yml")
trainimage_path = str(BASE_DIR / "TrainingImage")
studentdetail_path = str(BASE_DIR / "StudentDetails" / "studentdetails.csv")
attendance_path = str(BASE_DIR / "Attendance")


def _open_in_file_manager(path: Path) -> None:
    """Open a folder in the OS file explorer (cross-platform)."""
    try:
        if sys.platform.startswith("win"):
            os.startfile(str(path))  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            os.system(f"open \"{path}\"")
        else:
            os.system(f"xdg-open \"{path}\"")
    except Exception:
        pass


# for choose subject and fill attendance
def subjectChoose(text_to_speech):
    def FillAttendance():
        subject_name = (tx.get() or "").strip()
        if subject_name == "":
            text_to_speech("Please enter the subject name.")
            return

        # opencv-contrib is required for cv2.face
        if not hasattr(cv2, "face"):
            msg = "OpenCV 'face' module not found. Install opencv-contrib-python."
            Notifica.configure(text=msg)
            text_to_speech(msg)
            return

        model_path = Path(trainimagelabel_path)
        if not model_path.exists():
            msg = "Model not found. Please train the model first (Train Image)."
            Notifica.configure(text=msg)
            text_to_speech(msg)
            return

        student_csv = Path(studentdetail_path)
        if not student_csv.exists():
            msg = "Student details not found. Please register at least one student first."
            Notifica.configure(text=msg)
            text_to_speech(msg)
            return

        try:
            df_students = pd.read_csv(student_csv)
        except Exception:
            msg = "Could not read StudentDetails/studentdetails.csv"
            Notifica.configure(text=msg)
            text_to_speech(msg)
            return

        recognizer = cv2.face.LBPHFaceRecognizer_create()
        recognizer.read(str(model_path))

        face_cascade = cv2.CascadeClassifier(haarcasecade_path)

        cam = cv2.VideoCapture(0)
        if not cam.isOpened():
            msg = "Could not access the camera. Please check permissions or camera index."
            Notifica.configure(text=msg)
            text_to_speech(msg)
            return

        col_names = ["Enrollment", "Name"]
        attendance_df = pd.DataFrame(columns=col_names)

        start = time.time()
        duration_sec = 20
        font = cv2.FONT_HERSHEY_SIMPLEX

        try:
            while True:
                ret, frame = cam.read()
                if not ret:
                    break

                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                faces = face_cascade.detectMultiScale(gray, 1.2, 5)

                for (x, y, w, h) in faces:
                    student_id, conf = recognizer.predict(gray[y : y + h, x : x + w])

                    if conf < 70:
                        # Lookup name
                        matches = df_students.loc[df_students["Enrollment"] == student_id, "Name"]
                        student_name = matches.iloc[0] if len(matches) else "Unknown"

                        attendance_df.loc[len(attendance_df)] = [student_id, student_name]

                        label = f"{student_id}-{student_name}"
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 260, 0), 3)
                        cv2.putText(frame, label, (x, y - 10), font, 0.8, (255, 255, 0), 2)
                    else:
                        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 25, 255), 3)
                        cv2.putText(frame, "Unknown", (x, y - 10), font, 0.8, (0, 25, 255), 2)

                attendance_df.drop_duplicates(["Enrollment"], keep="first", inplace=True)

                cv2.imshow("Filling Attendance... (ESC to exit)", frame)
                key = cv2.waitKey(30) & 0xFF
                if key == 27:  # ESC
                    break

                if time.time() - start > duration_sec:
                    break

        finally:
            cam.release()
            cv2.destroyAllWindows()

        if attendance_df.empty:
            msg = "No recognized faces. Try again in better lighting or register more samples."
            Notifica.configure(text=msg)
            text_to_speech(msg)
            return

        ts = time.time()
        date_str = datetime.datetime.fromtimestamp(ts).strftime("%Y-%m-%d")
        time_str = datetime.datetime.fromtimestamp(ts).strftime("%H-%M-%S")

        attendance_df[date_str] = 1

        subject_dir = Path(attendance_path) / subject_name
        subject_dir.mkdir(parents=True, exist_ok=True)

        csv_path = subject_dir / f"{subject_name}_{date_str}_{time_str}.csv"
        attendance_df.to_csv(csv_path, index=False)

        msg = f"Attendance saved: {csv_path.name}"
        Notifica.configure(text=msg)
        text_to_speech("Attendance filled successfully.")

        # Show attendance table
        _show_csv_in_table(csv_path, title=f"Attendance of {subject_name}")

    def _show_csv_in_table(csv_path: Path, title: str):
        root = tk.Tk()
        root.title(title)
        root.configure(background="black")

        with csv_path.open(newline="", encoding="utf-8") as file:
            reader = csv.reader(file)
            for r, row in enumerate(reader):
                for c, value in enumerate(row):
                    label = tk.Label(
                        root,
                        width=14,
                        height=1,
                        fg="yellow",
                        font=("times", 14, "bold"),
                        bg="black",
                        text=value,
                        relief=tk.RIDGE,
                    )
                    label.grid(row=r, column=c, sticky="nsew")

        root.mainloop()

    # --- UI for subject chooser ---
    subject = Tk()
    subject.title("Subject")
    subject.geometry("580x320")
    subject.resizable(0, 0)
    subject.configure(background="black")

    title_bar = tk.Label(subject, bg="black", relief=RIDGE, bd=10, font=("arial", 30))
    title_bar.pack(fill=X)

    titl = tk.Label(
        subject,
        text="Enter the Subject Name",
        bg="black",
        fg="green",
        font=("arial", 25),
    )
    titl.place(x=150, y=12)

    global Notifica
    Notifica = tk.Label(
        subject,
        text="",
        bg="black",
        fg="yellow",
        width=45,
        height=2,
        font=("times", 12, "bold"),
    )
    Notifica.place(x=20, y=250)

    def Attf():
        sub = (tx.get() or "").strip()
        if sub == "":
            text_to_speech("Please enter the subject name.")
            return
        target_dir = Path(attendance_path) / sub
        target_dir.mkdir(parents=True, exist_ok=True)
        _open_in_file_manager(target_dir)

    attf = tk.Button(
        subject,
        text="Open Folder",
        command=Attf,
        bd=7,
        font=("times new roman", 15),
        bg="black",
        fg="yellow",
        height=2,
        width=12,
        relief=RIDGE,
    )
    attf.place(x=360, y=170)

    sub_lbl = tk.Label(
        subject,
        text="Enter Subject",
        width=10,
        height=2,
        bg="black",
        fg="yellow",
        bd=5,
        relief=RIDGE,
        font=("times new roman", 15),
    )
    sub_lbl.place(x=50, y=100)

    global tx
    tx = tk.Entry(
        subject,
        width=15,
        bd=5,
        bg="black",
        fg="yellow",
        relief=RIDGE,
        font=("times", 30, "bold"),
    )
    tx.place(x=190, y=100)

    fill_a = tk.Button(
        subject,
        text="Fill Attendance",
        command=FillAttendance,
        bd=7,
        font=("times new roman", 15),
        bg="black",
        fg="yellow",
        height=2,
        width=12,
        relief=RIDGE,
    )
    fill_a.place(x=195, y=170)

    subject.mainloop()
