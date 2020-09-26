from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import firebase_admin
from firebase_admin import credentials, firestore, initialize_app
from datetime import datetime


##TODO
    #firebase setup
    #heroku setup

# Initialize the Flask application
app = Flask(__name__)
CORS(app)
#with Firebase
cred = credentials.Certificate("./key.json")
firebase_admin.initialize_app(cred)
db = firestore.client()
todo_ref = db.collection('todos')
questions = db.collection('questions')


# route http posts to this method
@app.route('/test/', methods=['GET'])
def test():
    response = "it worked"
    response_pickled = jsonpickle.encode(response)

    return Response(response=response_pickled, status=200, mimetype="application/json")

# @app.route('/add', methods=['POST'])
# def create():
#     """
#         create() : Add document to Firestore collection with request body.
#         Ensure you pass a custom ID as part of json body in post request,
#         e.g. json={'id': '1', 'title': 'Write a blog post'}
#     """
#     try:
#         id = request.json['id']
#         todo_ref.document(id).set(request.json)
#         return jsonify({"success": True}), 200
#     except Exception as e:
#         return f"An Error Occured: {e}"


@app.route('/question', methods=['POST'])
def createQuestion():
    """
        createQuestion() : Add document to Firestore collection with request body.
        Ensure you pass a custom ID as part of json body in post request,
        e.g. json={"userName": "Socrates", "questionBody": "is addition just negative subtraction?", "time": "12:32","isViewed": 0}
    """
    try:
        jsonBody = request.json
        jsonBody["time"] = datetime.now()
        jsonBody["isViewed"] = 0
        questions.add(jsonBody)
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error2 Occured: {e}"

@app.route('/question', methods=['GET'])
def getQuestions():
    """
        getQuestions() :gets all questions.
        Ensure you pass a custom ID as part of json body in post request,
        e.g. json={"userName": "Socrates", "questionBody": "is addition just negative subtraction?", "time": "12:32","isViewed": 0}
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
        questionJson['isViewed'] = 1
        print(questionJson)
        questions.document(questionId).update(questionJson)
        return jsonify({"success": True}), 200
    except Exception as e:
        return f"An Error3 Occured: {e}"


    #give me the next question and then delete it
    

#start flask app
if __name__ == '__main__':
    app.run()
#host="localhost", port=5000