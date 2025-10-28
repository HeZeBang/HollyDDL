import flask
from utils import egateHandler, hydroHandler
from utils.gsUtils import *
import urllib3

app = flask.Flask(__name__)


# Allow local CORS for debugging
@app.after_request
def add_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST"
    return response


@app.route("/api/gradescope", methods=["POST"])
def gsHandler() -> flask.Response:
    # Get payload from request
    payload = flask.request.get_json()

    # Login
    gs = Gradescope(payload["email"], payload["password"])
    if not gs.logged_in:
        return flask.jsonify({"status": "error", "message": "Invalid email or password"})

    # Format response
    data = []

    for course in gs.get_courses(role=Role.STUDENT):
        # print(course)
        for assignment in gs.get_assignments(course):
            due = [None, None]
            if assignment["dueDate"]:
                due = assignment["dueDate"]
            data.append(
                {
                    "title": assignment["title"],
                    "course": course.full_name,
                    "url": assignment["url"],
                    "due": due[0],
                    "latedue": due[1] if len(due) > 1 else None,
                    "status": assignment["status"],
                    "submitted": assignment["status"] != "No Submission",
                    "raw": assignment,
                }
            )

    return flask.jsonify({"status": "success", "data": data})

@app.route("/api/exam", methods=["POST"])
def eamsExamHandler() -> flask.Response:
    # Get payload from request
    urllib3.disable_warnings()
    payload = flask.request.get_json()

    # Login
    session = egateHandler.login(payload["studentid"], payload["password"])
    # if (not bb.logged_in):
    #     return {
    #         'status': 'error',
    #         'message': 'Invalid username or password'
    #     }

    # Format response
    data = egateHandler.getBB(session)

    # urllib3.warnings.simplefilter("always", urllib3.exceptions.InsecureRequestWarning)

    return flask.jsonify({"status": "success", "data": data})

@app.route("/api/blackboard", methods=["POST"])
def bbHandler() -> flask.Response:
    # Get payload from request
    urllib3.disable_warnings()
    payload = flask.request.get_json()

    # Login
    session = egateHandler.login(payload["studentid"], payload["password"])
    # if (not bb.logged_in):
    #     return {
    #         'status': 'error',
    #         'message': 'Invalid username or password'
    #     }

    # Format response
    data = egateHandler.getBB(session)

    # urllib3.warnings.simplefilter("always", urllib3.exceptions.InsecureRequestWarning)

    return flask.jsonify({"status": "success", "data": data})


@app.route("/api/hydro", methods=["POST"])
def ojHandler() -> flask.Response:
    # Get payload from request
    payload = flask.request.get_json()

    # Login
    session = hydroHandler.login(payload["url"], payload["username"], payload["password"])

    # Format response
    data = hydroHandler.getHomework(payload["url"], session)

    return flask.jsonify({"status": "success", "data": data})


# Handle Not Found
@app.errorhandler(404)
def page_not_found(e):
    return flask.jsonify({"status": "error", "message": "Not Found: " + flask.request.url})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
