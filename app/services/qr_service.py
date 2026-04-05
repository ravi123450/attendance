import qrcode
import uuid
import os

QR_DIR = "uploads/qr"
os.makedirs(QR_DIR, exist_ok=True)


def generate_qr(roll):

    code = f"ATT_{roll}_{uuid.uuid4().hex[:6]}"

    img = qrcode.make(code)

    path = f"{QR_DIR}/{roll}.png"

    img.save(path)

    return code, path
