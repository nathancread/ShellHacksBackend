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
        jsonBody["upVotes"] = 0
        sessionId = jsonBody['sessionId']
        print("STATUS", sessions.document(sessionId).get().exists)
        if sessions.document(sessionId).get().exists == False:
            currentSession = sessions.document(sessionId).set({})
        currentSession = sessions.document(sessionId)
        studentQuestions = currentSession.collection('studentQuestions')
        studentQuestions.add(jsonBody)
        currentSession.set(studentQuestions)
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error2 Occured: {e}"

@app.route('/quiz', methods=['POST'])
def createQuiz():
    """
        createQuiz() : Add document to Firestore collection with request body.
        Ensure you pass a custom ID as part of json body in post request,
        e.g. json={"answers": [...], "question": "??"}
    """
    try:
        jsonBody = request.json
        jsonBody["time"] = datetime.now()
        jsonBody["question_type"] = "poll"
        sessionId = jsonBody['sessionId']

        answers = jsonBody['answers']
        question = jsonBody['question']

        if sessions.document(sessionId).get().exists == False:
            currentSession = sessions.document(sessionId).set({})
        currentSession = sessions.document(sessionId)
        teacherQuestions = currentSession.collection('teacherQuestions')
        # teacherQuestions.add({
        #     "question": question,
        #     "question_type": "poll"
        # })
        teacherQuestionRef = teacherQuestions.document()
        teacherQuestionRef.set({
            "question": question,
            "question_type": "poll"
        })

        '''
        new_city_ref = db.collection(u'cities').document()

        # later...
        new_city_ref.set({
            # ...
        })
        '''
        questionAnswers = teacherQuestionRef.collection('answers')
        for a in answers:
            questionAnswers.add({
                "answer": a,
                "count": 0
            })

        currentSession.set(teacherQuestions)
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error2 Occured: {e}"

@app.route('/question', methods=['GET'])
def getQuestions():
    """
        getQuestions() :gets all questions.
        Ensure you pass a custom ID as part of json body in post request,
        e.g. json={"questionBody": "is addition just negative subtraction?", "time": "12:32","isViewed": 0, "sessionId": 123321, upVotes: 0,"badge": 0}
    """
    try:
        # Check if ID was passed to URL query
        questionId = request.args.get('questionId')
        sessionId = request.args.get('sessionId')
        currentSession = sessions.document(sessionId)
        studentQuestions = currentSession.collection('studentQuestions')

        if questionId:
            question = studentQuestions.document(questionId).get()
            return jsonify(question.to_dict()), 200
        else:
            allQuestions = [q.to_dict() for q in studentQuestions.stream()]
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
        questionId = request.args.get('questionId')
        sessionId = request.args.get('sessionId')
        currentSession = sessions.document(sessionId)
        studentQuestions = currentSession.collection('studentQuestions')

        question = studentQuestions.document(questionId).get()
        questionJson = question.to_dict()
        questionJson['isViewed'] = True
        studentQuestions.document(questionId).update(questionJson)
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error3 Occured: {e}"


@app.route('/nextQuestion', methods=['GET'])
def next():
    """
        next() : gets question, then marks it as deleted
        Ensure you pass a custom ID as part of json body in post request,
        e.g. json={'id': '1', 'title': 'Write a blog post today'}
    """

    try:
        # Check if ID was passed to URL query
        sessionId = request.args.get('sessionId')
        currentSession = sessions.document(sessionId)
        studentQuestions = currentSession.collection('studentQuestions')
        #get question with most upvotes

        allQuestions = [(q.to_dict(),q.id) for q in studentQuestions.stream()]
        mostUpVotes = -1
        nextQuestion = "There are no more questions"
        id = ""
        print(nextQuestion,id,mostUpVotes)

        for q in allQuestions:
            if(q[0]['upVotes'] > mostUpVotes and q[0]['isViewed'] == False):
                if(q[0]['upVotes']>mostUpVotes):
                    mostUpVotes = q[0]['upVotes'] 
                    nextQuestion = q[0]
                    id = q[1]


        #mark as viewed
        if(mostUpVotes != -1):
            nextQuestion['isViewed'] = True
            studentQuestions.document(id).update(nextQuestion)

        return jsonify(nextQuestion), 200
    except Exception as e:
        return f"An Error Occured: {e}"

# @app.route('/nextQuestion', methods=['GET'])
# def next():
#     """
#         next() : gets question, then marks it as deleted
#         Ensure you pass a custom ID as part of json body in post request,
#         e.g. json={'id': '1', 'title': 'Write a blog post today'}
#     """
##give me user id
#return session Id

##give me session id and user id
#store the session is associated with user

#start flask app
if __name__ == '__main__':
    app.run()
#host="localhost", port=5000
