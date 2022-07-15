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
    app
    # resources=CORSConfig.resources
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
        "telegram_id": user[5]
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
                if board_tasks:
                    for task in board_tasks:
                        task_users = DB.get_users_tasks(task_id=task[0])
                        tasks[task[0]] = {
                            "name": task[1],
                            "deadline": task[4],
                            "description": task[3],
                            "authors": [],
                            "performers": [],
                            "supervisors": []
                        }
                        for pos in task_users:
                            if pos[2] == "author":
                                tasks[task[0]]["authors"].append(pos[0])
                            elif pos[2] == "performer":
                                tasks[task[0]]["performers"].append(pos[0])
                            elif pos[2] == "supervisor":
                                tasks[task[0]]["supervisors"].append(pos[0])
                BOARD["tasks"] = tasks

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
        if task:
            board_id = task[2]
            board_user = DB.get_users_boards_by_user_board(user_id=ID, board_id=board_id)
            if board_user is not None:
                task_users = DB.get_users_tasks(task_id=req["task_id"])
                TASK = {
                    "name": task[1],
                    "deadline": task[4],
                    "description": task[3],
                    "authors": [],
                    "performers": [],
                    "supervisors": [],
                    "comments": dict()
                }

                comments = DB.get_comments(task_id=req["task_id"])

                for comment in comments:
                    TASK["comments"][comment[0]] = {
                        "author": comment[4],
                        "content": comment[2],
                        "task_id": comment[1],
                        "date_time": comment[3]
                    }


                for pos in task_users:
                    if pos[2] == "author":
                        TASK["authors"].append(pos[0])
                    elif pos[2] == "performer":
                        TASK["performers"].append(pos[0])
                    elif pos[2] == "supervisor":
                        TASK["supervisors"].append(pos[0])
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
    if not ({"name", "deadline", "color", "description"} - req.keys()):
        board_id = DB.insert_board(req["name"], req["color"], req["deadline"], req["description"])
        DB.insert_users_boards(ID, board_id, user_position="admin")
    else:
        response["status"] = "Bad request"
    return jsonify(response)


@app.route('/add/task', methods=["POST"])
@jwt_required()
def add_task():
    ID = get_jwt_identity()
    req = request.json
    response = dict()

    if not ({"name", "board_id", "description", "deadline"} - req.keys()):
        board_user = DB.get_users_boards_by_user_board(user_id=ID, board_id=req["board_id"])
        if board_user is not None:
            task_id = DB.insert_task(name=req["name"], board_id=req["board_id"], description=req["description"],
                                     deadline=req["deadline"])
            DB.insert_users_tasks(task_id=task_id, user_id=ID, position="author")
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
    if not ({"board_id", "new_name", "new_color", "new_deadline", "new_description", "new_user_id", "new_user_position",
             "delete_user"} - req.keys()):
        board_user = DB.get_users_boards_by_user_board(user_id=ID, board_id=req["board_id"])
        board_user.sort(key=lambda x: x[2])
        new_user = DB.get_user(ID=ID)
        req["new_user_id"] = req["new_user_id"] if new_user is not None else False
        if board_user is not None and board_user[0][2] == "admin" and ID != req["board_id"]:
            DB.update_board(
                req["board_id"],
                new_name=req["new_name"],
                new_color=req["new_color"],
                new_deadline=req["new_deadline"],
                new_description=req["new_description"],
                new_user_id=req["new_user_id"],
                new_user_position=req["new_user_position"],
                delete_user=req["delete_user"]
            )
        else:
            response["status"] = "Access denied"
    else:
        response["status"] = "Bad request"
    return jsonify(response)


@app.route('/task/edit', methods=["POST"])
@jwt_required()
def task_edit():
    ID = get_jwt_identity()
    req = request.json
    response = dict()
    if not ({"task_id", "new_name", "new_deadline", "new_description", "new_stage", "new_performer",
             "new_supervisor"} - req.keys()):
        task = DB.get_task(task_id=req["task_id"])
        if task is not None:
            board_id = task[2]
            task_user = DB.get_users_tasks(task_id=req["task_id"], user_id=ID)
            task_user.sort(key=lambda x: x[2])
            board_user = DB.get_users_boards_by_user_board(user_id=ID, board_id=board_id)
            board_user.sort(key=lambda x: x[2])

            new_performer = DB.get_user(ID=req["new_performer"])
            new_supervisor = DB.get_user(ID=req["new_supervisor"])

            req["new_performer"] = req["new_performer"] if new_performer is not None else False
            req["new_supervisor"] = req["new_supervisor"] if new_supervisor is not None else False

            if board_user[0][2] == "admin" or task_user[0][2] == "author":
                DB.update_task(
                    task_id=req["task_id"],
                    new_name=req["new_name"],
                    new_deadline=req["new_deadline"],
                    new_description=req["new_description"],
                    new_stage=req["new_stage"],
                    new_performer=req["new_performer"],
                    new_supervisor=req["new_supervisor"]
                )
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
    if not ({"task_id", "content"} - req.keys()):
        task = DB.get_task(task_id=req["task_id"])
        if task is not None:
            board_id = task[2]
            user_board = DB.get_users_boards_by_user_board(user_id=ID, board_id=board_id)
            if user_board:
                DB.insert_comment(
                    task_id=req["task_id"],
                    author_id=ID,
                    content=req["content"],
                    date_time=datetime.now()
                )
            else:
                response["status"] = "Access denied"
        else:
            response["status"] = "Task does not exist"
    else:
        response["status"] = "Bad request"

    return jsonify(response)


@app.route('/task/add/file', methods=["POST"])
@jwt_required()
def task_add_file():
    return jsonify(
        {"status": "Я тут ничего не сделал"}
    ), 404


@app.route('/profile/edit', methods=["POST"])
@jwt_required()
def profile_edit():
    ID = get_jwt_identity()
    req = request.json
    response = dict()
    if not ({"old_password", "new_name", "new_phone", "new_email", "new_telegram", "new_password"} - req.keys()):
        user = DB.get_user(ID=ID)
        if user is not None:
            old_password_hash = user[3]
            hash_check = hashing_password(password=req["old_password"], phone=user[2])
            if hash_check == old_password_hash:
                if req["new_password"]:
                    req["new_phone"] = req["new_phone"] if req["new_phone"] else user[2]
                    req["new_password"] = hashing_password(password=req["new_password"], phone=req["new_phone"])
                DB.update_user(
                    user_id=ID,
                    new_name=req["new_name"],
                    new_phone=req["new_phone"],
                    new_email=req["new_email"],
                    new_telegram=req["new_telegram"],
                    new_password=req["new_password"]
                )
            else:
                response["status"] = "Wrong password"
        else:
            response["status"] = "User does not exist"
    else:
        response["status"] = "Bad request"
    return jsonify(response)


@app.route('/task/delete/performer', methods=["POST"])
@jwt_required()
def task_delete_performer():
    ID = get_jwt_identity()
    req = request.json
    response = dict()
    if not ({"user_id", "task_id"} - req.keys()):
        user = DB.get_user(ID=ID)
        performer = DB.get_user(ID=req["user_id"])
        task = DB.get_task(task_id=req["task_id"])
        if user and performer and task:
            board_id = task[2]
            board_user = DB.get_users_boards_by_user_board(user_id=ID, board_id=board_id)
            task_user = DB.get_users_tasks(task_id=req["task_id"], user_id=ID)
            t1 = False
            for U in board_user:
                if U[2] == "admin":
                    t1 = True
                    break
            t2 = False
            for U in task_user:
                if U[2] == "author":
                    t2 = True
                    break
            if t1 or t2:
                DB.delete_users_tasks(user_id=req["user_id"], task_id=req["task_id"], position="performer")
            else:
                response["status"] = "Access denied"
        else:
            response["status"] = "Wrong parameters"
    else:
        response["status"] = "Bad request"
    return jsonify(response)


@app.route('/task/delete/supervisor', methods=["POST"])
@jwt_required()
def task_delete_supervisor():
    ID = get_jwt_identity()
    req = request.json
    response = dict()
    if not ({"user_id", "task_id"} - req.keys()):
        user = DB.get_user(ID=ID)
        supervisor = DB.get_user(ID=req["user_id"])
        task = DB.get_task(task_id=req["task_id"])
        if user and supervisor and task:
            board_id = task[2]
            board_user = DB.get_users_boards_by_user_board(user_id=ID, board_id=board_id)
            task_user = DB.get_users_tasks(task_id=req["task_id"], user_id=ID)
            t1 = False
            for U in board_user:
                if U[2] == "admin":
                    t1 = True
                    break
            t2 = False
            for U in task_user:
                if U[2] == "author":
                    t2 = True
                    break
            if t1 or t2:
                DB.delete_users_tasks(user_id=req["user_id"], task_id=req["task_id"], position="supervisor")
            else:
                response["status"] = "Access denied"
        else:
            response["status"] = "Wrong parameters"
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
        if comment and comment[4] == ID:
            DB.delete_comment(req["comment_id"])
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
        board = DB.get_board(board_id=req["board_id"])
        if board:
            board_user = DB.get_users_boards_by_user_board(user_id=ID, board_id=req["board_id"])
            user_test = False
            for us_bo in board_user:
                if us_bo[2] == "admin":
                    user_test = True
            board_user.sort(key=lambda x: x[2])
            if user_test:
                DB.delete_users_boards(board_id=req["board_id"])
                DB.delete_board(board_id=req["board_id"])
                board_tasks = DB.get_tasks_by_board(board_id=req["board_id"])
                if board_tasks:
                    for task in board_tasks:
                        DB.delete_users_tasks(task_id=task[0])
                        DB.delete_task(task[0])
                        task_comments = DB.get_comments(task_id=task[0])
                        if task_comments:
                            for comment in task_comments:
                                DB.delete_comment(comment[0])
            else:
                response["status"] = "Access denied"
        else:
            response["status"] = "Board does not exist"
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
        task = DB.get_task(task_id=req["task_id"])
        if task:
            board_id = task[2]
            board_user = DB.get_users_boards_by_user_board(user_id=ID, board_id=board_id)
            task_user = DB.get_users_tasks(task_id=req["task_id"], user_id=ID)
            if board_user and task_user:
                board_user.sort(key=lambda x:x[2])
                task_user.sort(key=lambda x:x[2])
                if board_user[0][2] == "admin" or task_user[0][2] == "author":
                    task_comments = DB.get_comments(task_id=req["task_id"])
                    DB.delete_users_tasks(task_id=req["task_id"])
                    DB.delete_task(req["task_id"])
                    for comment in task_comments:
                        DB.delete_comment(comment[0])
                else:
                    response["status"] = "Access denied"
            else:
                response["status"] = "Wrong task"
        else:
            response["status"] = "Wrong task"
    else:
        response["status"] = "Bad request"

    return jsonify(response)


if __name__ == '__main__':
    app.config.from_object('config.FlaskConfig')
    app.run(port=8010, host='127.0.0.1', debug=True)
