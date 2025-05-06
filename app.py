import os
import json
import random
from flask import Flask, render_template, request, session, redirect, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "dev_secret_key")

QUESTIONS_DIR = os.path.join(os.path.dirname(__file__), "questions")

def load_questions_from_file(filename: str):
    path = os.path.join(QUESTIONS_DIR, filename)
    with open(path, encoding="utf-8") as f:
        return json.load(f)

@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/start_quiz", methods=["POST"])
def start_quiz():
    # 途中から再開フラグ
    if request.form.get("resume"):
        year   = request.form["year"]
        qtype  = request.form["type"]
        period = request.form["period"]
        session.clear()
        session["filename"] = f"{year}_{qtype}_{period}.json"
        session["index"]    = int(request.form.get("resume_index", 0))
        session["score"]    = int(request.form.get("resume_score", 0))
    else:
        year   = request.form["year"]
        qtype  = request.form["type"]
        period = request.form["period"]
        session.clear()
        session["filename"] = f"{year}_{qtype}_{period}.json"
        session["index"]    = 0
        session["score"]    = 0

    return redirect(url_for("quiz"))

@app.route("/random_quiz", methods=["POST"])
def random_quiz():
    all_questions = []
    for fname in os.listdir(QUESTIONS_DIR):
        if fname.endswith(".json"):
            all_questions += load_questions_from_file(fname)
    questions = random.sample(all_questions, 40)

    session.clear()
    session["questions"] = questions
    session["index"]     = 0
    session["score"]     = 0

    return redirect(url_for("quiz"))

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if "filename" not in session and "questions" not in session:
        return redirect(url_for("index"))

    if "questions" in session:
        questions = session["questions"]
    else:
        questions = load_questions_from_file(session["filename"])

    if request.method == "POST":
        idx      = session["index"]
        selected = request.form.get("answer")
        q        = questions[idx]
        correct  = (selected == q["answer"])
        if correct:
            session["score"] += 1
        return render_template(
            "answer.html",
            number=idx+1,
            total=len(questions),
            question=q,
            selected=selected,
            correct=correct
        )

    idx = session.setdefault("index", 0)
    if idx >= len(questions):
        return redirect(url_for("result"))

    return render_template(
        "quiz.html",
        number=idx+1,
        total=len(questions),
        question=questions[idx]
    )

@app.route("/answer_next", methods=["POST"])
def answer_next():
    session["index"] += 1
    return redirect(url_for("quiz"))

@app.route("/result")
def result():
    score = session.get("score", 0)
    if "questions" in session:
        total = len(session["questions"])
    else:
        total = len(load_questions_from_file(session.get("filename","")))
    session.clear()
    return render_template("result.html", score=score, total=total)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)