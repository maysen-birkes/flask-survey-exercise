from flask import Flask, session, request, render_template, redirect, make_response, flash
from flask_debugtoolbar import DebugToolbarExtension
from surveys import surveys

CURRENT_SURVEY_KEY = 'current_survey'
RESPONSE_KEY = 'responses'

app = Flask(__name__)
app.config['SECRET_KEY'] = 'top-secret'
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)


@app.route('/')
def enable_pick_survey_form():
    """Shows the form for user to pick a survey"""

    return render_template("pick-survey.html", surveys=surveys)


@app.route('/', methods=["POST"])
def select_survey():
    """Pick a survey"""

    survey_id = request.form['survey_code']

    if request.cookies.get(f"completed_{survey_id}"):
        return render_template("done.html")
    
    survey = surveys[survey_id]
    session[CURRENT_SURVEY_KEY] = survey_id

    return render_template("start_survey.html", survey=survey)


@app.route('/begin', methods=["POST"])
def begin_survey():
    """Reset the session response."""

    session[RESPONSE_KEY] = []

    return redirect("/questions/0")


@app.route('/answer', methods=["POST"])
def process_question():
    """Store the response and proceed to the next question"""

    choice = request.form['answer']
    text = request.form.get("text", "")

    responses = session[RESPONSE_KEY]
    responses.append({"choice": choice, "text": text})

    session[RESPONSE_KEY] = responses
    survey_code = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_code]

    if (len(responses) == len(survey.questions)):
        return redirect("/complete")
    
    else:
        return redirect(f"/questions/{len(responses)}")
    

@app.route("/questions/<int:qid>")
def show_question(qid):
    """Display the current quesiton"""

    responses = session.get(RESPONSE_KEY)
    survey_code = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_code]

    if (responses is None):
        return redirect('/')
    
    if (len(responses) == len(survey.questions)):
        return redirect("/complete")
    
    if (len(responses) != qid):
        flash(f"Invalid question id:{qid}.")
        return redirect(f"/questions/{len(responses)}")
    
    question = survey.questions[qid]

    return render_template(
        "questions.html", question_num=qid, question=question)


@app.route("/complete")
def say_thank_you():
    """Thank the user for completing the survey. List their responses."""

    survey_id = session[CURRENT_SURVEY_KEY]
    survey = surveys[survey_id]
    responses = session[RESPONSE_KEY]

    html = render_template("completed.html", survey=survey, responses=responses)

    response = make_response(html)
    response.set_cookie(f"completed_{survey_id}", "yes", max_age=60)
    return response