from flask import Flask, render_template, request, send_file
import os
import json
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet

from utils.ocr import extract_text
from utils.summarizer import summarize_text

app = Flask(__name__)

UPLOAD_FOLDER = "uploads"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ===========================
# Home
# ===========================

@app.route("/")
def home():

    return render_template("index.html")


# ===========================
# Upload File
# ===========================

@app.route("/upload", methods=["POST"])
def upload():

    if "file" not in request.files:

        return "No file uploaded!"

    file = request.files["file"]

    if file.filename == "":

        return "Please select a file."

    filepath = os.path.join(

        app.config["UPLOAD_FOLDER"],
        file.filename

    )

    file.save(filepath)

    # OCR

    extracted_text = extract_text(filepath)

    print("\n========== OCR OUTPUT ==========\n")

    print(extracted_text)

    if not extracted_text or extracted_text.strip() == "":
          return "OCR could not extract any text."
    # Go to Preview Page

    return render_template(

        "preview.html",

        extracted_text=extracted_text

    )
# ===========================
# Generate Study Material
# ===========================

@app.route("/generate", methods=["POST"])
def generate():

    text = request.form["edited_text"]

    summary = "summary" in request.form
    key_points = "key_points" in request.form
    flashcards = "flashcards" in request.form
    mcqs = "mcqs" in request.form

    try:
        mcq_count = int(request.form["mcq_count"])
    except:
        mcq_count = 10

    mcq_count = max(1, min(mcq_count, 50))

    difficulty = request.form["difficulty"]

    ai_data = summarize_text(

        text=text,
        summary=summary,
        key_points=key_points,
        flashcards=flashcards,
        mcqs=mcqs,
        mcq_count=mcq_count,
        difficulty=difficulty

    )

    return render_template(

        "result.html",

        extracted_text=text,

        summary=ai_data.get("summary", []),

        key_points=ai_data.get("key_points", []),

        mcqs=ai_data.get("mcqs", []),

        flashcards=ai_data.get("flashcards", []),

        easy_explanation=ai_data.get(
            "easy_explanation",
            ""
        )

    )


# ===========================
# Download PDF
# ===========================
@app.route("/download_pdf", methods=["POST"])
def download_pdf():

    summary = request.form["summary"]
    easy_explanation = request.form["easy_explanation"]

    key_points = json.loads(request.form["key_points"])
    mcqs = json.loads(request.form["mcqs"])
    flashcards = json.loads(request.form["flashcards"])

    pdf_file = "Study_Material.pdf"

    styles = getSampleStyleSheet()

    doc = SimpleDocTemplate(pdf_file)

    story = []

    # ================= TITLE =================

    story.append(
        Paragraph(
            "<b><font size='20'>StudySpark AI</font></b>",
            styles["Title"]
        )
    )

    story.append(
        Paragraph(
            "<b>AI Generated Study Material</b>",
            styles["Heading2"]
        )
    )

    story.append(
        Paragraph("<br/><br/>", styles["BodyText"])
    )

    # ================= SUMMARY =================

    story.append(
        Paragraph("<b>AI Summary</b>", styles["Heading2"])
    )

    story.append(
        Paragraph(summary.replace("\n", "<br/>"), styles["BodyText"])
    )

    story.append(
        Paragraph("<br/><br/>", styles["BodyText"])
    )

    # ================= KEY POINTS =================

    if key_points:

        story.append(
            Paragraph("<b>Key Points</b>", styles["Heading2"])
        )

        for point in key_points:

            story.append(
                Paragraph(f"• {point}", styles["BodyText"])
            )

        story.append(
            Paragraph("<br/><br/>", styles["BodyText"])
        )

    # ================= MCQs =================

    if mcqs:

        story.append(
            Paragraph("<b>Practice MCQs</b>", styles["Heading2"])
        )

        for i, mcq in enumerate(mcqs, start=1):

            story.append(
                Paragraph(
                    f"<b>Q{i}. {mcq['question']}</b>",
                    styles["BodyText"]
                )
            )

            for option in mcq["options"]:

                story.append(
                    Paragraph(option, styles["BodyText"])
                )

            story.append(
                Paragraph(
                    f"<b>Answer:</b> {mcq['answer']}",
                    styles["BodyText"]
                )
            )

            story.append(
                Paragraph("<br/>", styles["BodyText"])
            )

    # ================= FLASHCARDS =================

    if flashcards:

        story.append(
            Paragraph("<b>Flashcards</b>", styles["Heading2"])
        )

        for card in flashcards:

            story.append(
                Paragraph(
                    f"<b>Q.</b> {card['question']}",
                    styles["BodyText"]
                )
            )

            story.append(
                Paragraph(
                    f"<b>A.</b> {card['answer']}",
                    styles["BodyText"]
                )
            )

            story.append(
                Paragraph("<br/>", styles["BodyText"])
            )

    # ================= EASY EXPLANATION =================

    if easy_explanation:

        story.append(
            Paragraph("<b>Easy Explanation</b>", styles["Heading2"])
        )

        story.append(
            Paragraph(
                easy_explanation.replace("\n", "<br/>"),
                styles["BodyText"]
            )
        )

    doc.build(story)

    return send_file(
        pdf_file,
        as_attachment=True
    )

# ===========================
# Run App
# ===========================

if __name__ == "__main__":

    app.run(
        debug=True
    )