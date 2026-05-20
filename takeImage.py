import csv
import re
from pathlib import Path
import cv2

BASE_DIR = Path(__file__).resolve().parent


def _safe_slug(value: str) -> str:
    """Keep folder/file names predictable across OSes."""
    value = value.strip()
    value = re.sub(r"\s+", "_", value)
    value = re.sub(r"[^A-Za-z0-9_-]", "", value)
    return value or "unknown"


def _ensure_student_csv(csv_path: Path) -> None:
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    if not csv_path.exists():
        csv_path.write_text("Enrollment,Name\n", encoding="utf-8")


def _upsert_student(csv_path: Path, enrollment: str, name: str) -> None:
    """Insert or update a student row (Enrollment is the unique key)."""
    _ensure_student_csv(csv_path)

    rows: list[list[str]] = []
    with csv_path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        if header is None or len(header) < 2:
            header = ["Enrollment", "Name"]
        for r in reader:
            if not r:
                continue
            # Keep only 2 columns
            rows.append([r[0].strip(), (r[1].strip() if len(r) > 1 else "")])

    updated = False
    for r in rows:
        if r[0] == enrollment:
            r[1] = name
            updated = True
            break

    if not updated:
        rows.append([enrollment, name])

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Enrollment", "Name"])
        writer.writerows(rows)


# take Image of user
def TakeImage(l1, l2, haarcasecade_path, trainimage_path, message, err_screen, text_to_speech):
    enrollment = (l1 or "").strip()
    name = (l2 or "").strip()

    if not enrollment and not name:
        text_to_speech("Please enter your Enrollment Number and Name.")
        return
    if not enrollment:
        text_to_speech("Please enter your Enrollment Number.")
        return
    if not name:
        text_to_speech("Please enter your Name.")
        return

    cascade_path = Path(haarcasecade_path)
    if not cascade_path.exists():
        text_to_speech("Face detector file not found. Please check haarcascade path.")
        return

    train_dir = Path(trainimage_path)
    train_dir.mkdir(parents=True, exist_ok=True)

    safe_name = _safe_slug(name)
    user_dir = train_dir / f"{enrollment}_{safe_name}"

    try:
        user_dir.mkdir(parents=True, exist_ok=False)
    except FileExistsError:
        text_to_speech("Student data already exists. Try a new Enrollment, or delete the existing folder.")
        return

    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        text_to_speech("Could not access the camera. Please check permissions or camera index.")
        return

    detector = cv2.CascadeClassifier(str(cascade_path))
    sample_num = 0
    max_samples = 50

    try:
        while True:
            ret, frame = cam.read()
            if not ret:
                text_to_speech("Failed to read from camera.")
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (255, 0, 0), 2)
                sample_num += 1

                img_path = user_dir / f"{safe_name}_{enrollment}_{sample_num:03d}.jpg"
                cv2.imwrite(str(img_path), gray[y : y + h, x : x + w])

            cv2.imshow("Registering - Press 'q' to stop", frame)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break
            if sample_num >= max_samples:
                break

    finally:
        cam.release()
        cv2.destroyAllWindows()

    # Save/update student details
    student_csv = BASE_DIR / "StudentDetails" / "studentdetails.csv"
    _upsert_student(student_csv, enrollment, name)

    res = f"Images saved for Enrollment: {enrollment} | Name: {name}"
    if hasattr(message, "configure"):
        message.configure(text=res)
    text_to_speech(res)
