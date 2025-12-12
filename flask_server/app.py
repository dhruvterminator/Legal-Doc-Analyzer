from flask import Flask, request, jsonify
from textblob import TextBlob
from paraphrase import paraphrase
from predict import run_prediction
from flask_cors import CORS
import json
import pdfplumber
import io

app = Flask(__name__)
CORS(app)

# -------------------------------------
# Load questions
# -------------------------------------
def load_questions_short():
    with open('data/questions_short.txt', encoding="utf8") as f:
        return [q.strip() for q in f.readlines()]

questions_short = load_questions_short()


@app.route('/questionsshort')
def getQuestionsShort():
    return jsonify(questions_short)



# -------------------------------------
# Sentiment Analysis
# -------------------------------------
def getContractAnalysis(selected_response):
    if selected_response == "":
        return "No answer found in document"

    polarity = TextBlob(selected_response).sentiment.polarity

    if polarity > 0:
        return "Positive"
    elif polarity < 0:
        return "Negative"
    return "Neutral"


# -------------------------------------
# Main Contract QA API
# -------------------------------------
@app.route('/contracts', methods=["POST"])
def getContractResponse():

    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"]
    question = request.form.get("question", "")

    file_bytes = file.read()

    # --------- Extract text from PDF ---------
    pdf_text = ""
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                txt = page.extract_text()
                if txt:
                    pdf_text += txt + "\n"
    except Exception as e:
        return jsonify({"error": "Error reading PDF", "details": str(e)}), 500

    paragraph = pdf_text.strip()

    if not paragraph or not question:
        return jsonify({"error": "Need both PDF and question"}), 400

    # --------- Run CUAD prediction ---------
    predictions = run_prediction(
        [question],
        paragraph,
        'marshmellow77/roberta-base-cuad',
        n_best_size=5
    )

    answers = []

    if predictions['0'] == "":
        answers.append({
            "answer": "No answer found in document",
            "probability": "",
            "analyse": "Neutral"
        })
    else:
        with open("nbest.json", encoding="utf8") as jf:
            data = json.load(jf)

        for i in range(5):
            answers.append({
                "answer": data['0'][i]['text'],
                "probability": f"{round(data['0'][i]['probability'] * 100, 1)}%",
                "analyse": getContractAnalysis(data['0'][i]['text'])
            })

    return jsonify(answers)



# -------------------------------------
# Paraphraser
# -------------------------------------
@app.route('/contracts/paraphrase/<path:selected_response>', methods=['GET'])
def getContractParaphrase(selected_response):

    if selected_response == "":
        return jsonify(["No answer found in document"])

    result = paraphrase(selected_response)
    return jsonify(result)



# -------------------------------------
# Stored Q&A
# -------------------------------------
@app.route('/get_response', methods=['POST'])
def get_response():

    question = request.form.get('selected_response', "")

    with open('responses.json', 'r', encoding="utf8") as file:
        responses = json.load(file)

    for entry in responses:
        if entry['question'] == question:
            return jsonify(entry['answer'])

    return jsonify("Response not found")



# -------------------------------------
# Run App
# -------------------------------------
if __name__ == '__main__':
    app.run(debug=True)
