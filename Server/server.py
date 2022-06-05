# Тут обработка запросов сервером

from flask import *
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, \
    unset_jwt_cookies, jwt_required, JWTManager
import json
from flask_cors import CORS
from datetime import datetime, timedelta, timezone
import db
from ADDITIONAL import hashing_password
from statuses import StatusBuilder

DB = db.MainDB()
app = Flask(__name__)
app.secret_key = 'KEY'

cors = CORS(app,
            resources={
                r"/*": {  # куда будут приходить запросы (в данном случае на любой адрес сервера)
                    "origins": "http://localhost:3000/*"  # адрес, откуда будут приходить запросы
                }
            })


def build_user(user):
    USER = dict()
    USER["phone"] = user[2]
    USER["id"] = user[0]
    board_ids = DB.get_boards_by_user(user[0])
    boards_info = [DB.get_board(ID) for ID in board_ids]
    BOARDS = dict()
    for i in range(len(board_ids)):
        BOARDS[board_ids[i]] = {
            "name": boards_info[i][1],
            "deadline": boards_info[i][2],
            "color": boards_info[i][3],
            "description": boards_info[i][4]
        }
    USER["boards"] = BOARDS
    return USER


@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()["exp"]
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            data = response.get_json()
            if type(data) is dict:
                data["access_token"] = access_token
                response.data = json.dumps(data)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original respone
        return response


@app.route('/login', methods=['POST'])
def login():
    status = StatusBuilder.login(request.json)
    response = dict()
    if status == StatusBuilder.OK:
        user = build_user(DB.get_user(phone=request.json["phone"]))
        session["user"] = user
        access_token = create_access_token(identity=user["id"])
        response = {
            "status": status,
            "session": session,
            "access_token": access_token
        }
    else:
        response["status"] = status
    return jsonify(response)


@app.route('/logout')
def logout():
    response = jsonify({"status": "ok"})
    unset_jwt_cookies(response)
    return response


@app.route('/registration', methods=["POST"])
def registration():
    status = StatusBuilder.registration(request.json)
    response = dict()
    if status == StatusBuilder.OK:
        user = DB.get_user(phone="phone")
        if not user:
            user = build_user(
                DB.get_user(ID=DB.insert_user(phone=request.json['phone'], password=request.json['password'])))
            session["user"] = user
            access_token = create_access_token(identity=user["id"])
            response = {
                "status": status,
                "session": session,
                "access_token": access_token
            }
        else:
            response["status"] = "User already exists"
    else:
        response["status"] = status
    return jsonify(response)


@app.route('/add_board', methods=['GET', 'POST'])
@jwt_required()
def add_board():
    req = request.json
    status = StatusBuilder.add_board(req)
    response = dict()
    if status == StatusBuilder.OK:
        board_id = DB.insert_board(req["name"], req["color"], req["deadline"], req["description"])
        for user_id in req['users']:
            DB.insert_users_boards(user_id, board_id)
        response["status"] = "ok"
    else:
        response["status"] = status

    return jsonify(response)


@app.route('/project', methods=['POST'])
@jwt_required()
def project():
    req = request.json
    status = StatusBuilder.project(req)
    response = dict()
    if status:
        user = DB.get_user(ID=req["user"]["id"])
        if user:
            USER = build_user(user)
            session['user'] = USER

            response = {
                "status": "ok",
                "session": session
            }
        else:
            response["status"] = "User does not exist"
    else:
        response["status"] = status
    return jsonify(response)


@app.route('/add_task', methods=["POST"])
@jwt_required()
def add_task():
    req = request.json
    response = dict()
    status = StatusBuilder.add_task(req)
    if status == StatusBuilder.OK:
        task_id = DB.insert_task(req["name"], req["board_id"], req["description"], req["deadline"])
        for user_id in req['performers']:
            DB.insert_users_tasks(task_id, user_id, "performer")
        DB.insert_users_tasks(task_id, req["author"], "author")
        DB.insert_users_tasks(task_id, req["supervisor"], "supervisor")
        response["status"] = "ok"
    else:
        response["status"] = status
    return jsonify(response)


@app.route('/profile')
@jwt_required()
def profile():
    """
    Аналогично добываем инфу о челе и возвращаем её форнтам
    """
    return dict()


if __name__ == '__main__':
    app.config.from_object('config.FlaskConfig')
    JWT = JWTManager(app)
    app.run(port=8010, host='127.0.0.1', debug=True)
