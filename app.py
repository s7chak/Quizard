from flask import Flask, request, jsonify, session
from flask_cors import CORS
from ops.opapp import Util
from datetime import timedelta
from flask_session import Session

app = Flask(__name__)
app.secret_key = 'quizardapi_sc'
app.config['SESSION_PERMANENT'] = True
app.config['SESSION_TYPE'] = 'filesystem'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)
app.config['SESSION_COOKIE_NAME'] = 'quizard_session'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
CORS(app, supports_credentials=True)
Session(app)

@app.route("/getText", methods=["POST"])
def get_text():
    """
        Endpoint to extract text from given links.
        Expects a JSON payload: { "links": ["link1", "link2", ...] }
    """
    try:
        data = request.get_json()
        if not data or "links" not in data:
            return jsonify({"error": "Invalid input. 'links' field is required."}), 400
        links = data["links"]
        if not isinstance(links, list) or not all(isinstance(link, str) for link in links):
            return jsonify({"error": "Invalid 'links'. Must be a list of strings."}), 400
        util = Util()
        util.extract_text(links)
        extracted_text = session[session.sid]['corpus']
        return jsonify({"text": extracted_text}), 200

    except Exception as e:
        return jsonify({"error": f"An error occurred: {str(e)}"}), 500

@app.route("/generateQuiz", methods=["POST"])
def generate_quiz():
    """
        Endpoint to generate quiz using Open AI credentials
        Expects a JSON payload: { "ai_key": "" }
    """
    try:
        data = request.get_json()
        if not data or "aiKey" not in data:
            return jsonify({"error": "Invalid input. 'links' field is required."}), 400
        ai_key = data["aiKey"]
        difficulties = data["difficulties"]

        util = Util()
        util.generate_quiz(ai_key, difficulties)
        generated_quiz = session[session.sid]['quiz']
        return jsonify({"quiz": generated_quiz}), 200
    except Exception as e:
        return jsonify({"quiz": f"An error occurred: {str(e)}"}), 500

@app.route("/clearSessionz", methods=["GET"])
def clear_sessions():
    session.clear()
    return jsonify({"message": "Done"}), 200

@app.route("/health", methods=["GET"])
def running():
    return "Quizard API Running."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=1000)