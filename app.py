from flask import Flask, render_template, request, redirect, url_for, session
import json
import random

app = Flask(__name__)
app.secret_key = "secret"

def load_questions(year):
    with open(f"questions/{year}.json", encoding="utf-8") as f:
        return json.load(f)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/start_quiz", methods=["POST"])
def start_quiz():
    year = request.form.get("year")
    questions = load_questions(year)
    if year == "random":
        questions = random.sample(questions, 40)
    session["questions"] = questions
    session["index"] = 0
    session["score"] = 0
    return redirect(url_for("quiz"))

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    questions = session.get("questions")
    index = session.get("index")
    score = session.get("score")

    if request.method == "POST":
        selected = request.form.get("answer")
        correct = questions[index]["answer"]
        if selected == correct:
            session["score"] += 1
        session["index"] += 1
        index += 1

    if index >= len(questions):
        return render_template("result.html", score=session["score"], total=len(questions))

    return render_template("quiz.html", question=questions[index], index=index + 1, total=len(questions))

if __name__ == "__main__":
    app.run(debug=True)