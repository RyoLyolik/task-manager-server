import requests
from flask import *
from flask_jwt_extended import *
import json
from flask_cors import CORS
from datetime import datetime, timedelta, timezone
import db
from ADDITIONAL import hashing_password
from config import *

DB = db.MainDB()
app = Flask(__name__)
app.secret_key = FlaskConfig.secret_key
JWT = JWTManager(app)
cors = CORS(
    app,
    resources=CORSConfig.resources
)


@app.after_request
def refresh_expiring_jwts(response):
    try:
        exp_timestamp = get_jwt()['exp']
        now = datetime.now(timezone.utc)
        target_timestamp = datetime.timestamp(now + JWTConfig.JWT_ACCESS_TOKEN_EXPIRES)
        if target_timestamp > exp_timestamp:
            access_token = create_access_token(identity=get_jwt_identity())
            data = response.get_json()
            if type(data) is dict:
                data["access_token"] = access_token
                response.data = json.dumps(data)
        return response
    except (RuntimeError, KeyError):
        # Case where there is not a valid JWT. Just return the original response
        return response


@app.route('/login', methods=["POST"])
def login():
    req = request.json
    response = dict()

    if "phone" in req and "password" in req:
        user = DB.get_user(phone=req['phone'])
        if user is not None:
            password_verification = hashing_password(password=req["password"], phone=req["phone"]) == user[3]
            if password_verification:
                access_token = create_access_token(identity=user[0])
                response["access_token"] = access_token
            else:
                response["status"] = "Wrong password"
        else:
            response["status"] = "User does not exist"
    else:
        response["status"] = "Bad request"

    return jsonify(response)


@app.route('/logout')
def logout():
    response = jsonify({"status": "ok"})
    unset_jwt_cookies(response)
    return response


@app.route("/registration", methods=["POST"])
def registration():
    req = request.json
    response = dict()
    if not ({"password", "password_confirm", "phone"} - req.keys()):
        user = DB.get_user(phone=req['phone'])
        if user is None:
            if req["password"] == req["password_confirm"]:
                password_hash = hashing_password(password=req["password"], phone=req["phone"])
                user_id = DB.insert_user(phone=req["phone"], password=password_hash)
                access_token = create_access_token(identity=user_id)
                response["access_token"] = access_token
            else:
                response["status"] = "Password missmatch"
        else:
            response["status"] = "User already exists"
    else:
        response["status"] = "Bad request"

    return jsonify(response)


@app.route('/profile/info', methods=["GET"])
@jwt_required()
def profile_info():
    ID = get_jwt_identity()
    user = DB.get_user(ID=ID)
    USER = {
        "id": ID,
        "name": user[1],
        "phone_number": user[2],
        "email": user[4],
        "yandex_email": user[5],
        "telegram_id": user[6]
    }
    response = {
        'user_info': USER
    }
    return jsonify(response)


@app.route('/profile/boards', methods=["GET"])
@jwt_required()
def profile_boards():
    ID = get_jwt_identity()
    boards_ids = DB.get_boards_by_user(user_id=ID)
    boards_info = [DB.get_board(ID) for ID in boards_ids]
    BOARDS = dict()
    for i in range(len(boards_ids)):
        BOARDS[boards_ids[i]] = {
            "name": boards_info[i][1],
            "deadline": boards_info[i][2],
            "color": boards_info[i][3],
            "description": boards_info[i][4]
        }
    response = {
        'boards': BOARDS
    }
    return jsonify(response)


@app.route('/board/info', methods=["GET"])
@jwt_required()
def board_info():
    ID = get_jwt_identity()
    req = request.json
    response = dict()
    if "board_id" in req:
        board = DB.get_board(board_id=req["board_id"])
        if board is not None:
            board_user = DB.get_users_boards_by_user_board(user_id=ID, board_id=req['board_id'])
            if board_user is not None:
                BOARD = {
                    "name": board[1],
                    "deadline": board[2],
                    "color": board[3],
                    "description": board[4]
                }

                board_tasks = DB.get_tasks_by_board(req["board_id"])
                tasks = dict()
                print(board_tasks)
                if board_tasks:
                    for task in board_tasks:
                        task_users = DB.get_users_tasks(task_id=task[0])
                        task_users.sort(key=lambda x: x[2])

                        tasks[task[0]] = {
                            "name": task[1],
                            "deadline": task[4],
                            "description": task[3],
                            "author": task_users[0][0],
                            "performer": task_users[1][0],
                            "supervisor": task_users[2][0]
                        }
                BOARD["board"]["tasks"] = tasks

                response["board"] = BOARD
            else:
                response["status"] = "Board does not contain this user"
        else:
            response["status"] = "Board does not exist"
    else:
        response["status"] = "Bad request"

    return jsonify(response)


@app.route('/task/info', methods=["GET"])
@jwt_required()
def task_info():
    ID = get_jwt_identity()
    req = request.json
    response = dict()
    if "task_id" in req:
        task = DB.get_task(req["task_id"])
        task_users = DB.get_users_tasks(task_id=req["task_id"])
        TASK = {
            "id": task[0],
            "name": task[1],
            "deadline": task[4],
            "description": task[3],
            "author": task_users[0][0],
            "performer": task_users[1][0],
            "supervisor": task_users[2][0]
        }
        response["task"] = TASK
    else:
        response["status"] = "Bad request"
    return jsonify(response)

@app.route('/add/board', methods=["POST"])
@jwt_required()
def add_board():
    ID = get_jwt_identity()
    req = request.json
    response = dict()
    if not ({"name", "deadline", "color", "description"} - req.keys()):
        board_id = DB.insert_board(req["name"], req["color"], req["deadline"], req["description"])
        DB.insert_users_boards(ID, board_id, user_position="admin")
    else:
        response["status"] = "Bad request"
    return jsonify(response)

@app.route('/add/task')
@jwt_required()
def add_task():
    ID = get_jwt_identity()
    req = request.json
    response = dict()

    if not ({"name", "board_id", "description", "deadline"} - req.keys()):
        board_user = DB.get_users_boards_by_user_board(user_id=ID, board_id=req["board_id"])
        if board_user is not None:
            task_id = DB.insert_task(name=req["name"], board_id=req["board_id"], description=req["description"], deadline=req["deadline"])
            DB.insert_users_tasks(task_id=task_id, user_id=ID, position="author")
        else:
            response["status"] = "Board does not contain this user"
    else:
        response["status"] = "Bad request"
    return jsonify(response)



if __name__ == '__main__':
    app.config.from_object('config.FlaskConfig')
    app.run(port=8010, host='127.0.0.1', debug=True)
