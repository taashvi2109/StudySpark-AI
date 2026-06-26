import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-2.5-flash")


def summarize_text(
    text,
    summary=True,
    key_points=True,
    flashcards=False,
    mcqs=True,
    mcq_count=10,
    difficulty="Medium"
):

    prompt = """

You are an AI Study Assistant.

Read the COMPLETE notes carefully.

Use the complete notes while generating the response.

Return ONLY valid JSON.

Do NOT use markdown.

Generate ONLY the sections selected by the user.

"""

    # ---------- Summary ----------

    if summary:

        prompt += """

Generate "summary".

summary must cover the entire notes from beginning to end.

Do NOT summarize only the introduction.

Cover ALL important topics, headings and sub-headings present in the notes.

Do not skip any major concept.

Write a detailed summary in 5-8 well-structured paragraphs.

The summary should represent the entire document, not just the first few pages.

Avoid unnecessary details and examples unless important for understanding.

"""

    # ---------- Key Points ----------

    if key_points:

        prompt += """

Generate "key_points".

Return 8-12 important points.

Return as a JSON array.

"""

    # ---------- MCQs ----------

    if mcqs:

        prompt += f"""

Generate EXACTLY {mcq_count} {difficulty} level MCQs.

Each MCQ should contain:

question

options

answer

Return options like:

[
"A. ...",
"B. ...",
"C. ...",
"D. ..."
]

"""

    # ---------- Flashcards ----------

    if flashcards:

        prompt += """

Generate 10 flashcards.

Each flashcard should contain:

question

answer

"""

    # ---------- Easy Explanation ----------

    prompt += """

Generate "easy_explanation".

Explain the topic in simple language.

Return ONLY JSON in this format:

{

"summary":"",

"key_points":[],

"mcqs":[],

"flashcards":[],

"easy_explanation":""

}

Notes:

"""

    prompt += text

        # Generate response from Gemini
    response = model.generate_content(prompt)
    print("========== GEMINI RESPONSE ==========")
    print(response.text)

    json_text = response.text.strip()

    # Remove markdown if Gemini returns ```json
    if json_text.startswith("```"):

        json_text = (
            json_text
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

    # Convert JSON string to Python dictionary
    try:

        data = json.loads(json_text)

    except Exception as e:

         print("JSON Parsing Error:", e)
         print("---------------")
         print(json_text)
         print("---------------")
        

    # Make sure every key exists
    data.setdefault("summary", "")
    data.setdefault("key_points", [])
    data.setdefault("mcqs", [])
    data.setdefault("flashcards", [])
    data.setdefault("easy_explanation", "")

    return data