from __future__ import annotations

from pathlib import Path
import cv2
import numpy as np
from PIL import Image


# Train Image
def TrainImage(haarcasecade_path, trainimage_path, trainimagelabel_path, message, text_to_speech):
    """Train an LBPH face recognizer on the captured face crops."""

    # opencv-contrib is required for cv2.face
    if not hasattr(cv2, "face"):
        msg = "OpenCV 'face' module not found. Install opencv-contrib-python."
        if hasattr(message, "configure"):
            message.configure(text=msg)
        text_to_speech(msg)
        return

    train_dir = Path(trainimage_path)
    if not train_dir.exists():
        msg = "TrainingImage folder not found. Please register at least one student first."
        if hasattr(message, "configure"):
            message.configure(text=msg)
        text_to_speech(msg)
        return

    faces, ids = getImagesAndLabels(train_dir)
    if not faces:
        msg = "No training images found. Please capture images first."
        if hasattr(message, "configure"):
            message.configure(text=msg)
        text_to_speech(msg)
        return

    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.train(faces, np.array(ids))

    model_path = Path(trainimagelabel_path)
    model_path.parent.mkdir(parents=True, exist_ok=True)
    recognizer.save(str(model_path))

    res = f"Model trained successfully ({len(faces)} images, {len(set(ids))} students)."
    if hasattr(message, "configure"):
        message.configure(text=res)
    text_to_speech(res)


def getImagesAndLabels(train_dir: Path):
    """Load grayscale face crops and labels from TrainingImage/*/*.jpg"""

    image_paths = list(train_dir.glob("*/*.jpg")) + list(train_dir.glob("*/*.png"))

    faces: list[np.ndarray] = []
    ids: list[int] = []

    for img_path in image_paths:
        try:
            pil_img = Image.open(img_path).convert("L")
            img_np = np.array(pil_img, "uint8")

            # Expected filename pattern: <Name>_<Enrollment>_<N>.jpg
            parts = img_path.stem.split("_")
            if len(parts) < 3:
                continue
            enrollment = int(parts[1])

            faces.append(img_np)
            ids.append(enrollment)
        except Exception:
            # Skip unreadable/bad files
            continue

    return faces, ids
