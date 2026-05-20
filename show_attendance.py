import csv
import os
import sys
from functools import reduce
from pathlib import Path

import pandas as pd
import tkinter as tk
from tkinter import *

BASE_DIR = Path(__file__).resolve().parent
ATTENDANCE_DIR = BASE_DIR / "Attendance"


def _open_in_file_manager(path: Path) -> None:
    try:
        if sys.platform.startswith("win"):
            os.startfile(str(path))  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            os.system(f"open \"{path}\"")
        else:
            os.system(f"xdg-open \"{path}\"")
    except Exception:
        pass


def subjectchoose(text_to_speech):
    def calculate_attendance():
        subject_name = (tx.get() or "").strip()
        if subject_name == "":
            text_to_speech("Please enter the subject name.")
            return

        subject_dir = ATTENDANCE_DIR / subject_name
        if not subject_dir.exists():
            text_to_speech("No attendance records found for this subject yet.")
            return

        session_files = sorted(subject_dir.glob(f"{subject_name}_*.csv"))
        if not session_files:
            text_to_speech("No attendance CSV files found for this subject.")
            return

        dfs = []
        for f in session_files:
            try:
                df = pd.read_csv(f)
            except Exception:
                continue

            if "Enrollment" not in df.columns or "Name" not in df.columns:
                continue

            # The 'present' column is whatever comes after Enrollment/Name.
            extra_cols = [c for c in df.columns if c not in ("Enrollment", "Name")]
            if not extra_cols:
                continue

            present_col = extra_cols[0]
            session_col = f.stem  # unique per file
            df = df[["Enrollment", "Name", present_col]].rename(columns={present_col: session_col})
            dfs.append(df)

        if not dfs:
            text_to_speech("Attendance files were found, but none had the expected columns.")
            return

        merged = reduce(lambda left, right: pd.merge(left, right, on=["Enrollment", "Name"], how="outer"), dfs)
        merged.fillna(0, inplace=True)

        session_cols = [c for c in merged.columns if c not in ("Enrollment", "Name")]
        merged["Attendance%"] = (merged[session_cols].mean(axis=1) * 100).round().astype(int).astype(str) + "%"
        merged.sort_values(by=["Enrollment"], inplace=True)

        out_csv = subject_dir / "attendance_summary.csv"
        merged.to_csv(out_csv, index=False)

        _show_csv_in_table(out_csv, title=f"Attendance Summary - {subject_name}")

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
                        width=18,
                        height=1,
                        fg="yellow",
                        font=("times", 12, "bold"),
                        bg="black",
                        text=value,
                        relief=tk.RIDGE,
                    )
                    label.grid(row=r, column=c, sticky="nsew")

        root.mainloop()

    subject = Tk()
    subject.title("Subject")
    subject.geometry("580x320")
    subject.resizable(0, 0)
    subject.configure(background="black")

    titl = tk.Label(subject, bg="black", relief=RIDGE, bd=10, font=("arial", 30))
    titl.pack(fill=X)

    titl = tk.Label(
        subject,
        text="Which Subject?",
        bg="black",
        fg="green",
        font=("arial", 25),
    )
    titl.place(x=200, y=12)

    def open_folder():
        sub = (tx.get() or "").strip()
        if sub == "":
            text_to_speech("Please enter the subject name.")
            return
        target = ATTENDANCE_DIR / sub
        target.mkdir(parents=True, exist_ok=True)
        _open_in_file_manager(target)

    btn_open = tk.Button(
        subject,
        text="Open Folder",
        command=open_folder,
        bd=7,
        font=("times new roman", 15),
        bg="black",
        fg="yellow",
        height=2,
        width=12,
        relief=RIDGE,
    )
    btn_open.place(x=360, y=170)

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

    btn_summary = tk.Button(
        subject,
        text="View Summary",
        command=calculate_attendance,
        bd=7,
        font=("times new roman", 15),
        bg="black",
        fg="yellow",
        height=2,
        width=12,
        relief=RIDGE,
    )
    btn_summary.place(x=195, y=170)

    subject.mainloop()
