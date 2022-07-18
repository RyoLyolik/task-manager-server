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
    app
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
        user = DB.get_user(phone_number=req['phone'])
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

    return jsonify(response), 201


@app.route('/logout')
def logout():
    response = jsonify({"status": "ok"})
    unset_jwt_cookies(response)
    return response


@app.route("/registration", methods=["POST"])
def registration():
    req = request.json
    response = dict()
    if "password" in req and "password_confirm" in req and "phone" in req:
        user = DB.get_user(phone_number=str(req['phone']))
        if user is None:
            if req["password"] == req["password_confirm"]:
                password_hash = hashing_password(password=req["password"], phone=str(req["phone"]))
                user_id = DB.insert_user(phone_number=str(req["phone"]), password=password_hash)
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
    user = DB.get_user(user_id=ID)
    response = dict()
    if user:
        USER = {
            "user_id": ID,
            "name": user[1],
            "phone_number": user[2],
            "email": user[4],
            "telegram_id": user[5]
        }
        response["user"] = USER
    else:
        response["status"] = "User does not exist"
    return jsonify(response)


@app.route('/user/info', methods=["GET"])
@jwt_required()
def user_info():
    ID = get_jwt_identity()
    req = request.json
    response = dict()
    if "user_id" in req:
        user = DB.get_user(user_id=req["user_id"])
        if user:
            USER = {
                "user_id": ID,
                "name": user[1]
            }
            response["user"] = USER
        else:
            response["status"] = "User does not exist"
    else:
        response["status"] = "Bad request"
    return jsonify(response)


@app.route('/profile/boards', methods=["GET"])
@jwt_required()
def profile_boards():
    ID = get_jwt_identity()
    response = dict()
    boards_ids = DB.get_boards(user_id=ID)
    if boards_ids:
        BOARDS = dict()
        for b_id in boards_ids:
            board = DB.get_board(board_id=b_id)
            if board:
                BOARDS[b_id] = dict(board)
        response["boards"] = BOARDS
    else:
        response["status"] = "User has no boards"
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
            board_user = DB.get_user_board(user_id=ID, board_id=req['board_id'])
            if board_user is not None:
                BOARD = dict(board_user)

                board_tasks = DB.get_tasks(board_id=req["board_id"])
                board_users = DB.get_users_boards(board_id=req["board_id"])
                tasks = dict()
                users = dict()
                if board_tasks:
                    for task in board_tasks:
                        task_users = DB.get_users_tasks(task_id=task[0])
                        tasks[task[0]] = {
                            "name": task[1],
                            "deadline": task[4],
                            "description": task[3],
                            "authors": dict(),
                            "performers": dict(),
                            "supervisors": dict()
                        }
                        for task_user in task_users:
                            user = DB.get_user(user_id=task_user[0])
                            if user:
                                if task_user[2] == "author":
                                    tasks[task[0]]["authors"][user[0]] = {
                                        "user_id": user["user_id"],
                                        "name": user["name"]
                                    }
                                elif task_user[2] == "performer":
                                    tasks[task[0]]["performers"][user[0]] = {
                                        "user_id": user["user_id"],
                                        "name": user["name"]
                                    }
                                elif task_user[2] == "supervisor":
                                    tasks[task[0]]["supervisors"][user[0]] = {
                                        "user_id": user["user_id"],
                                        "name": user["name"]
                                    }
                if board_users:
                    for user in board_users:
                        user_ = DB.get_user(user_id=user[0])
                        if user_:
                            users[user[0]] = {
                                "user_id": user_["user_id"],
                                "name": user_["name"],
                                "position": user[2]
                            }
                BOARD["tasks"] = tasks
                BOARD["users"] = users

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
        task = DB.get_task(task_id=req["task_id"])
        if task:
            board_id = task["board_id"]
            board_user = DB.get_user_board(user_id=ID, board_id=board_id)
            if board_user is not None:
                task_users = DB.get_users_tasks(task_id=req["task_id"])
                TASK = {
                    "name": task[1],
                    "deadline": task[4],
                    "description": task[3],
                    "stage": task[5],
                    "authors": dict(),
                    "performers": dict(),
                    "supervisors": dict(),
                    "comments": dict()
                }

                comments = DB.get_comments(task_id=req["task_id"])
                if comments:
                    for comment in comments:
                        TASK["comments"][comment[0]] = dict(comment)

                for task_user in task_users:
                    user = DB.get_user(user_id=task_user[0])
                    if user:
                        if task_user[2] == "author":
                            TASK["authors"][user[0]] = {
                                "user_id": user["user_id"],
                                "name": user["name"]
                            }
                        elif task_user[2] == "performer":
                            TASK["performers"][user[0]] = {
                                "user_id": user["user_id"],
                                "name": user["name"]
                            }
                        elif task_user[2] == "supervisor":
                            TASK["supervisors"][user[0]] = {
                                "user_id": user["user_id"],
                                "name": user["name"]
                            }
                response["task"] = TASK
            else:
                response["status"] = "Access denied"
        else:
            response["status"] = "Wrong task"
    else:
        response["status"] = "Bad request"
    return jsonify(response)


@app.route('/add/board', methods=["POST"])
@jwt_required()
def add_board():
    ID = get_jwt_identity()
    req = request.json
    response = dict()
    if "name" in req:
        board_id = DB.insert_board(**req)
        if board_id:
            DB.insert_users_boards(user_id=ID, board_id=board_id, user_position="admin")
        else:
            response["status"] = "Insertion error"
    else:
        response["status"] = "Bad request"
    return jsonify(response)


@app.route('/add/task', methods=["POST"])
@jwt_required()
def add_task():
    ID = get_jwt_identity()
    req = request.json
    response = dict()

    if "name" in req and "board_id" in req:
        board_user = DB.get_user_board(user_id=ID, board_id=req["board_id"])
        if board_user is not None:
            task_id = DB.insert_task(**req)
            if task_id:
                DB.insert_users_tasks(task_id=task_id, user_id=ID, position="author")
            else:
                response["status"] = "Insertion error"
        else:
            response["status"] = "Access denied"
    else:
        response["status"] = "Bad request"
    return jsonify(response)


@app.route('/board/edit', methods=["POST"])
@jwt_required()
def board_edit():
    ID = get_jwt_identity()
    req = request.json
    response = dict()
    if "board_id" in req:
        boards_user = DB.get_users_boards(user_id=ID, board_id=req["board_id"], user_position="admin")
        if boards_user:
            DB.update_board(**req)
        else:
            response["status"] = "Access denied"
    else:
        response["status"] = "Bad request"
    return jsonify(response)

@app.route('/board/add/user', methods=["POST"])
@jwt_required()
def board_add_user():
    ID = get_jwt_identity()
    req = request.json
    response = dict()
    if "board_id" in req and "user_id" in req and "user_position" in req:
        board = DB.get_board(board_id=req["board_id"])
        if board:
            board_user = DB.get_user_board(user_id=ID, board_id=req["board_id"], user_position="admin")
            if board_user:
                DB.insert_users_boards(**req)
            else:
                response["status"] = "Access denied"
        else:
            response["status"] = "Wrong task"
    else:
        response["status"] = "Bad request"

    return jsonify(response)

@app.route('/task/edit', methods=["POST"])
@jwt_required()
def task_edit():
    ID = get_jwt_identity()
    req = request.json
    response = dict()
    if "task_id" in req:
        task = DB.get_task(task_id=req["task_id"])
        if task is not None:
            board_id = task["board_id"]
            task_user = DB.get_user_task(task_id=req["task_id"], user_id=ID, user_position="author")
            board_user = DB.get_user_board(user_id=ID, board_id=board_id, user_position="admin")
            if task_user or board_user:
                DB.update_task(**req)
            else:
                response["status"] = "Access denied"
        else:
            response["status"] = "Task does not exist"
    else:
        response["status"] = "Bad request"

    return jsonify(response)


@app.route('/task/add/comment', methods=["POST"])
@jwt_required()
def task_add_comment():
    ID = get_jwt_identity()
    req = request.json
    response = dict()
    if "task_id" in req and "content" in req:
        task = DB.get_task(task_id=req["task_id"])
        if task is not None:
            board_id = task["board_id"]
            user_board = DB.get_user_board(user_id=ID, board_id=board_id)
            if user_board:
                req["author_id"] = ID
                req["date_time"] = datetime.now()
                req["board_id"] = board_id
                DB.insert_comment(**req)
            else:
                response["status"] = "Access denied"
        else:
            response["status"] = "Task does not exist"
    else:
        response["status"] = "Bad request"

    return jsonify(response)


@app.route('/task/add/user', methods=["POST"])
@jwt_required()
def task_add_user():
    ID = get_jwt_identity()
    req = request.json
    response = dict()
    if "task_id" in req and "user_id" in req and "user_position" in req:
        task = DB.get_task(task_id=req["task_id"])
        if task:
            task_user = DB.get_user_task(user_id=ID, task_id=req["task_id"], user_position="author")
            board_user = DB.get_user_board(user_id=ID, board_id=task["board_id"], user_position="admin")
            if task_user or board_user:
                DB.insert_users_tasks(**req)
            else:
                response["status"] = "Access denied"
        else:
            response["status"] = "Wrong task"
    else:
        response["status"] = "Bad request"

    return jsonify(response)

@app.route('/task/add/file', methods=["POST"])
@jwt_required()
def task_add_file():
    return jsonify(
        {"status": "Я тут ничего не сделал :/"}
    ), 404


@app.route('/profile/edit', methods=["POST"])
@jwt_required()
def profile_edit():
    ID = get_jwt_identity()
    req = request.json
    response = dict()
    if "changes" in req and "old_password" in req and isinstance(req["changes"], dict):
        user = DB.get_user(ID=ID)
        if user is not None:
            old_password_hash = user["password"]
            hash_check = hashing_password(password=req["old_password"], phone=user["phone_number"])
            if hash_check == old_password_hash:
                if "password" in req["changes"]:
                    if "phone_number" not in req["changes"]:
                        req["changes"]["phone_number"] = user["phone_number"]
                    if "password" in req["changes"]:
                        req["changes"]["password"] = hashing_password(password=req["changes"]["password"],
                                                                      phone=req["changes"]["phone_number"])
                    else:
                        req["changes"]["password"] = hashing_password(password=req["old_password"],
                                                                      phone=req["changes"]["phone_number"])
                DB.update_user(**req["changes"])
            else:
                response["status"] = "Wrong password"
        else:
            response["status"] = "User does not exist"
    else:
        response["status"] = "Bad request"
    return jsonify(response)


@app.route('/task/delete/user', methods=["POST"])
@jwt_required()
def task_delete_performer():
    ID = get_jwt_identity()
    req = request.json
    response = dict()
    if "position" in req and "user_id" in req and "task_id" in req:
        task = DB.get_task(task_id=req["task_id"])
        board = DB.get_board(board_id=task["board_id"])
        task_user = DB.get_user_task(task_id=req["task_id"], user_id=ID, user_position="author")
        board_user = DB.get_user_board(board_id=board["board_id"], user_id=ID, user_position="admin")
        if task and board and (task_user or board_user):
            DB.delete_users_tasks(**req)
        else:
            response["status"] = "Access denied"
    else:
        response["status"] = "Bad request"
    return jsonify(response)


@app.route('/task/delete/comment', methods=["POST"])
@jwt_required()
def task_delete_comment():
    ID = get_jwt_identity()
    req = request.json
    response = dict()
    if "comment_id" in req:
        comment = DB.get_comment(comment_id=req["comment_id"])
        if comment and comment["author_id"] == ID:
            DB.delete_comment(**req)
        else:
            response["status"] = "Access denied"
    else:
        response["status"] = "Bad request"
    return jsonify(response)


@app.route('/delete/board', methods=["POST"])
@jwt_required()
def delete_board():
    ID = get_jwt_identity()
    req = request.json
    response = dict()
    if "board_id" in req:
        board_user = DB.get_user_board(user_id=ID, board_id=req["board_id"], user_position="admin")
        if board_user:
            DB.delete_users_boards(board_id=req["board_id"])
            DB.delete_board(board_id=req["board_id"])
            DB.delete_comment(board_id=req["board_id"])
            DB.delete_task(board_id=req["board_id"])
        else:
            response["status"] = "Access denied"
    else:
        response["status"] = "Bad request"
    return jsonify(response)


@app.route('/delete/task', methods=["POST"])
@jwt_required()
def delete_task():
    ID = get_jwt_identity()
    req = request.json
    response = dict()

    if "task_id" in req:
        task_user = DB.get_user_task(user_id=ID, task_id=req["task_id"], user_position="author")
        if task_user:
            DB.delete_task(task_id=req["task_id"])
        else:
            response["status"] = "Access denied"
    else:
        response["status"] = "Bad request"

    return jsonify(response)


if __name__ == '__main__':
    app.config.from_object('config.FlaskConfig')
    app.run(port=8010, host='127.0.0.1', debug=True)
