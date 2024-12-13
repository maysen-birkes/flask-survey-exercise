from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from surveys import satisfaction_survey as survey

RESPONSES_KEY = "responses"

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top-secret'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)


@app.route('/')
def show_start_survey():
    """Shows the start of the survey and allows users to select the survey"""

    return render_template("start_survey.html", survey=survey)


@app.route('/start', methods=["POST"])
def start_survey():
    """Reset the session responses."""

    session[RESPONSES_KEY] = []

    return redirect("questions/0")


@app.route('/answer', methods=["POST"])
def process_question():
    """Store the response and proceed to the next question"""

    choice = request.form['answer']

    responses = session[RESPONSES_KEY]
    responses.append(choice)
    session[RESPONSES_KEY] = responses

    if (len(responses) == len(survey.questions)):
        return redirect("/complete")

    else: 
        return redirect(f"/questions/{len(responses)}")


@app.route("/questions/<int:qid>")
def show_question(qid):
    """Display the current question"""

    responses = session.get(RESPONSES_KEY)

    if (responses is None):
        return redirect("/")

    if (len(responses) == len(survey.questions)):
        return redirect("/complete")

    if (len(responses) != qid):
        flash(f"Invalid question id: {qid}")
        return redirect(f"/questions/{len(responses)}")

    question = survey.questions[qid]
    return render_template("questions.html", question_num=qid, question=question)


@app.route("/complete")
def completed():
    """Survey completed. Show survey completion page"""

    return render_template("completed.html")