import cv2
import numpy as np
from deepface import DeepFace

MODEL = "Facenet512"
DIM = 512


# --------------------
# Utils
# --------------------

def _img_from_file(file):

    data = file.read()
    arr = np.frombuffer(data, np.uint8)

    return cv2.imdecode(arr, cv2.IMREAD_COLOR)


def normalize(v):

    return v / np.linalg.norm(v)


# --------------------
# Single embedding
# --------------------

def _get_single_embedding(img):

    reps = DeepFace.represent(
        img_path=img,
        model_name=MODEL,
        enforce_detection=False
    )

    if not reps:
        return None

    emb = np.array(reps[0]["embedding"])

    if emb.shape[0] != DIM:
        return None

    return normalize(emb)


# --------------------
# Multiple frames → One embedding
# --------------------

def get_average_embedding(files):

    embeddings = []

    for f in files:

        img = _img_from_file(f)

        if img is None:
            continue

        emb = _get_single_embedding(img)

        if emb is not None:
            embeddings.append(emb)

    if len(embeddings) < 5:
        return None

    avg = np.mean(embeddings, axis=0)

    return normalize(avg)


# --------------------
# Recognition
# --------------------

def recognize_live(image_file, students, threshold=0.9):

    img = _img_from_file(image_file)

    if img is None:
        return None

    live_emb = _get_single_embedding(img)

    if live_emb is None:
        return None


    best = float("inf")
    match = None


    for s in students:

        if s.face_embedding is None:
            continue

        db_emb = np.array(s.face_embedding)

        if db_emb.shape[0] != DIM:
            continue

        db_emb = normalize(db_emb)

        dist = np.linalg.norm(db_emb - live_emb)

        print("DIST:", dist)

        if dist < best:
            best = dist
            match = s


    print("BEST:", best)


    if best < threshold:
        return match

    return None
