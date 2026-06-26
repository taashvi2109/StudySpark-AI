import os
import fitz
import easyocr
import cv2
import numpy as np

reader = easyocr.Reader(['en'], gpu=False)


def extract_text(file_path):

    extension = os.path.splitext(file_path)[1].lower()

    # =========================
    # IMAGE
    # =========================
    if extension in [".jpg", ".jpeg", ".png"]:

        result = reader.readtext(
            file_path,
            detail=0,
            paragraph=True
        )

        return "\n".join(result)

    # =========================
    # PDF
    # =========================
    elif extension == ".pdf":

        doc = fitz.open(file_path)

        extracted_text = ""

        # ---------- Try Direct Text Extraction ----------
        for page in doc:

            extracted_text += page.get_text()

        # If PDF already has text
        if extracted_text and extracted_text.strip():

            print("✅ Text PDF Detected")

            doc.close()

            return extracted_text

        print("📄 Scanned PDF Detected")

        extracted_text = ""

        # ---------- OCR Only if Needed ----------
        for page in doc:

            pix = page.get_pixmap(dpi=120)

            img = np.frombuffer(
                pix.samples,
                dtype=np.uint8
            )

            img = img.reshape(
                pix.height,
                pix.width,
                pix.n
            )

            if pix.n == 4:
                img = cv2.cvtColor(
                    img,
                    cv2.COLOR_RGBA2RGB
                )

            result = reader.readtext(
                img,
                detail=0,
                paragraph=True
            )

            extracted_text += "\n".join(result)
            extracted_text += "\n"

        doc.close()

        return extracted_text

    # =========================
    else:

        return ""