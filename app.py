from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app
from datetime import datetime
import os

##TODO
    #firebase setup
    #heroku setup

# Initialize the Flask application
app = Flask(__name__)
CORS(app)

#with Firebase
credential = {
    "type": os.environ.get("type"),
    "project_id": os.environ.get("project_id"),
    "private_key_id": os.environ.get("private_key_id"),
    "private_key": os.environ.get("private_key").replace("\\n","\n"),
    "client_email": os.environ.get("client_email"),
    "client_id": os.environ.get("client_id"),
    "auth_uri": os.environ.get("auth_uri"),
    "token_uri": os.environ.get("token_uri"),
    "auth_provider_x509_cert_url": os.environ.get("auth_provider_x509_cert_url"),
    "client_x509_cert_url": os.environ.get("client_x509_cert_url")
}

cred = credentials.Certificate(credential)
firebase_admin.initialize_app(cred)
db = firestore.client()
todo_ref = db.collection('todos')
questions = db.collection('questions')
sessions = db.collection('sessions')

@app.route('/question', methods=['POST'])
def createQuestion():
    """
        createQuestion() : Add document to Firestore collection with request body.
        Ensure you pass a custom ID as part of json body in post request,
        e.g. json={"questionBody": "is addition just negative subtraction?", "time": "12:32","isViewed": 0, "sessionId": 123321, upVotes: 0}
    """
    try:
        jsonBody = request.json
        jsonBody["time"] = datetime.now()
        jsonBody["isViewed"] = False
        sessionId = jsonBody['sessionId']
        print("Session ID", sessionId)
        currentSession = sessions.document(sessionId)
        print("Current Session", currentSession)
        studentQuestions = currentSession.collection('studentQuestions')

        studentQuestions.add(jsonBody)
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error2 Occured: {e}"

@app.route('/question', methods=['GET'])
def getQuestions():
    """
        getQuestions() :gets all questions.
        Ensure you pass a custom ID as part of json body in post request,
        e.g. json={"questionBody": "is addition just negative subtraction?", "time": "12:32","isViewed": 0, "sessionId": 123321, upVotes: 0}
    """
    try:
        # Check if ID was passed to URL query
        questionId = request.args.get('id')
        if questionId:
            question = questions.document(questionId).get()
            return jsonify(question.to_dict()), 200
        else:
            allQuestions = [q.to_dict() for q in questions.stream()]
            return jsonify(allQuestions), 200
    except Exception as e:
        return f"An Error Occured: {e}"

@app.route('/question', methods=['DELETE'])
def view():
    """
        view() : soft delete by marking as viewed
        Ensure you pass a custom ID as part of json body in post request,
        e.g. json={'id': '1', 'title': 'Write a blog post today'}
    """
    try:
        questionId = request.args.get('id')
        question = questions.document(questionId).get()
        questionJson = question.to_dict()
        print(questionJson)
        questionJson['isViewed'] = True
        print(questionJson)
        questions.document(questionId).update(questionJson)
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error3 Occured: {e}"


    #give me the next question and then delete it
    # @app.route('/question/next', methods=['GET'])
    # def next():
    #     """
    #         next() : gets question, then marks it as deleted
    #         Ensure you pass a custom ID as part of json body in post request,
    #         e.g. json={'id': '1', 'title': 'Write a blog post today'}
    #     """
    #     try:
    #         allQuestions = [q.to_dict() for q in questions.stream()]

    #         questionId = request.args.get('id')
    #         question = questions.document(questionId).get()
    #         questionJson = question.to_dict()
    #         print(questionJson)
    #         questionJson['isViewed'] = 1
    #         print(questionJson)
    #         questions.document(questionId).update(questionJson)
    #         return jsonify({"success": True}), 200
    #     except Exception as e:
    #         return f"An Error3 Occured: {e}"

#start flask app
if __name__ == '__main__':
    app.run()
#host="localhost", port=5000
