# Тут обработка запросов сервером

from flask import *
# from flask_session import Session
from flask_jwt_extended import create_access_token, get_jwt, get_jwt_identity, \
    unset_jwt_cookies, jwt_required, JWTManager
import json
from flask_cors import CORS, cross_origin
from datetime import datetime, timedelta, timezone
import db
import _sha3

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


def hashing_password(password, phone):
    hash_ = _sha3.sha3_256((str(password)+str(phone)).encode("utf-8")).hexdigest()
    return hash_


def corsify_actual_response(response):
    response.headers.add("Access-Control-Allow-Origin", "*")
    return response


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
    req = request.json
    if "phone" in req:
        user = DB.get_user(phone=req["phone"])
        req["password"] = hashing_password(req["password"], req["phone"])
        if user:
            if user[3] == req["password"]:
                USER = build_user(user)
                session['user'] = USER

                access_token = create_access_token(identity=user[0])
                response = {
                    "status": "ok",
                    "session": session,
                    "access_token": access_token
                }
            else:
                response = {
                    "status": "not ok",
                    "message": "wrong password"
                }
        else:
            response = {
                "status": "not ok",
                "message": "user does not exist"
            }
    else:
        response = {
            "status": "not ok",
            "message": "bad request"
        }
    print(response)
    return jsonify(response)


@app.route('/logout')
def logout():
    response = jsonify({"status": "ok"})
    unset_jwt_cookies(response)
    return response


@app.route('/registration', methods=["POST"])
def registration():
    req = request.json
    print(req)
    if not ({"password", "password_confirm", "phone"} - req.keys()):
        response = {"status": "ok"},
        if req['password'] == req['password_confirm']:
            q = DB.insert_user(req['phone'], req['password'])
            if q == "ok":
                USER = build_user(DB.get_user(req["phone"]))
                session["user"] = USER
                response = {
                    "status": q,
                    "session": session
                }
            else:
                response = {
                    "status": q
                }
    else:
        response = {"status": "bad request"}
    return jsonify(response)


@app.route('/add_board', methods=['GET', 'POST'])
@jwt_required()
def add_board():
    req = request.json
    if not ({"name", "color", "deadline", "description", "users", "author"} - req.keys()):
        if req["author"]:
            board_id = DB.insert_board(req["name"], req["color"], req["deadline"], req["description"])
            for user_id in req['users']:
                DB.insert_users_boards(user_id, board_id)
            response = {
                "status": "ok"
            }
        else:
            response = {
                "status": "unauthorized request"
            }
    else:
        response = {
            "status": "bad request"
        }
    return jsonify(response)


@app.route('/project', methods=['POST'])
@jwt_required()
def project():
    req = request.json
    if "user" in req:
        user = DB.get_user(ID=req["id"])
        if user:
            USER = build_user(user)
            session['user'] = USER

            access_token = create_access_token(identity=user[0])
            response = {
                "status": "ok",
                "session": session,
                "access_token": access_token
            }
        else:
            response = {
                "status": "not ok",
                "message": "user does not exist"
            }
    else:
        response = {
            "status": "not ok",
            "message": "bad request"
        }
    print(response)
    return jsonify(response)


@app.route('/add_task', methods=["POST"])
@jwt_required()
def add_task():
    req = request.json
    if not ({"name", "board_id", "deadline", "description", "performers", "author", "supervisor"} - req.keys()):
        if req["author"]:
            task_id = DB.insert_task(req["name"], req["board_id"], req["description"], req["deadline"])
            for user_id in req['performers']:
                DB.insert_users_tasks(task_id, user_id, "performer")
            DB.insert_users_tasks(task_id, req["author"], "author")
            DB.insert_users_tasks(task_id, req["supervisor"], "supervisor")
            response = {
                "status": "ok"
            }
        else:
            response = {
                "status": "unauthorized request"
            }
    else:
        response = {
            "status": "bad request"
        }
    return jsonify(response)


@app.route('/profile')
@jwt_required()
def profile():
    """
    Аналогично добываем инфу о челе и возвращаем её форнтам
    """
    return dict()


if __name__ == '__main__':
    app.config["JWT_SECRET_KEY"] = "please-remember-to-change-me"
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=24)
    JWT = JWTManager(app)
    app.run(port=8010, host='127.0.0.1', debug=True)
