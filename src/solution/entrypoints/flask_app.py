import io

from flask import *
from flask_jwt_extended import *
from flask_cors import CORS
from src.solution.service_layer.services import *
from src.solution.config import *
from src.solution.adapters.repository import *
from src.solution.adapters.specification import *
from src.solution.service_layer.handlers import *
from datetime import datetime, timezone

app = Flask(__name__)
JWT = JWTManager(app)
app.secret_key = FlaskConfig.secret_key
cors = CORS(
    app,
    supports_credentials=True  # <- maybe delete this later
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
        return response


@app.route('/login', methods=["POST"])
def login():
    req = request.json
    response = login_warden(**req)

    return jsonify(response)


@app.route('/registration', methods=["POST"])
def registration():
    req = request.json
    response = registration_warden(**req)

    return jsonify(response)


@app.route('/logout')
def logout():
    response = unset_session()
    return jsonify(response)


@app.route('/profile/info', methods=["GET"])
@jwt_required()
def profile_info():
    identity = get_jwt_identity()
    req = {JWTConfig.jwt_identity: identity}
    response = profile_info_warden(**req)

    return jsonify(response)


@app.route('/user/info', methods=["GET"])
@jwt_required()
def user_info():
    req = request.json
    response = user_info_warden(**req)

    return jsonify(response)


@app.route('/profile/boards', methods=["GET"])
@jwt_required()
def profile_boards():
    identity = get_jwt_identity()
    req = {JWTConfig.jwt_identity: identity}
    response = profile_boards_warden(**req)

    return jsonify(response)


@app.route('/profile/edit', methods=["POST"])
@jwt_required()
def profile_edit():
    req = request.json
    identity = get_jwt_identity()
    req[JWTConfig.jwt_identity] = identity
    response = profile_edit_warden(**req)

    return jsonify(response)


@app.route('/board/info', methods=["GET"])
@jwt_required()
def board_info():
    req = request.json
    identity = get_jwt_identity()
    req[JWTConfig.jwt_identity] = identity
    response = board_info_warden(**req)

    return jsonify(response)


@app.route('/board/tasks', methods=["GET"])
@jwt_required()
def board_tasks():
    identity = get_jwt_identity()
    req = request.json
    req[JWTConfig.jwt_identity] = identity
    response = board_tasks_warden(**req)

    return jsonify(response)


@app.route('/board/users', methods=["GET"])
@jwt_required()
def board_users():
    req = request.json
    identity = get_jwt_identity()
    req[JWTConfig.jwt_identity] = identity
    response = board_users_warden(**req)

    return jsonify(response)


@app.route('/task/info', methods=["GET"])
@jwt_required()
def task_info():
    req = request.json
    identity = get_jwt_identity()
    req[JWTConfig.jwt_identity] = identity
    response = task_info_warden(**req)

    return jsonify(response)


@app.route('/task/users', methods=["GET"])
@jwt_required()
def task_users():
    req = request.json
    identity = get_jwt_identity()
    req[JWTConfig.jwt_identity] = identity
    response = task_users_warden(**req)

    return jsonify(response)


@app.route('/task/comments', methods=["GET"])
@jwt_required()
def task_comments():
    req = request.json
    identity = get_jwt_identity()
    req[JWTConfig.jwt_identity] = identity
    response = task_comments_warden(**req)

    return jsonify(response)

@app.route('/task/files', methods=["GET"])
@jwt_required()
def task_files():
    req = request.json
    identity = get_jwt_identity()
    req[JWTConfig.jwt_identity] = identity
    response = task_files_warden(**req)

    return jsonify(response)


@app.route('/add/board', methods=["POST"])
@jwt_required()
def add_board():
    req = request.json
    identity = get_jwt_identity()
    req[JWTConfig.jwt_identity] = identity
    response = add_board_warden(**req)

    return jsonify(response)


@app.route('/add/task', methods=["POST"])
@jwt_required()
def add_task():
    req = request.json
    identity = get_jwt_identity()
    req[JWTConfig.jwt_identity] = identity
    response = add_task_warden(**req)

    return jsonify(response)


@app.route('/board/edit', methods=["POST"])
@jwt_required()
def board_edit():
    req = request.json
    identity = get_jwt_identity()
    req[JWTConfig.jwt_identity] = identity
    response = board_edit_warden(**req)

    return jsonify(response)


@app.route('/board/add/user', methods=["POST"])
@jwt_required()
def board_add_user():
    req = request.json
    identity = get_jwt_identity()
    req[JWTConfig.jwt_identity] = identity
    response = board_add_user_warden(**req)

    return jsonify(response)


@app.route('/board/delete/user', methods=["POST"])
@jwt_required()
def board_delete_user():
    req = request.json
    identity = get_jwt_identity()
    req[JWTConfig.jwt_identity] = identity
    response = board_delete_user_warden(**req)

    return jsonify(response)


@app.route('/task/edit', methods=["POST"])
@jwt_required()
def task_edit():
    req = request.json
    identity = get_jwt_identity()
    req[JWTConfig.jwt_identity] = identity
    response = task_edit_warden(**req)

    return jsonify(response)


@app.route('/task/add/comment', methods=["POST"])
@jwt_required()
def task_add_comment():
    req = request.json
    identity = get_jwt_identity()
    req[JWTConfig.jwt_identity] = identity
    response = task_add_comment_warden(**req)

    return jsonify(response)


@app.route('/task/delete/comment', methods=["POST"])
@jwt_required()
def task_delete_comment():
    req = request.json
    identity = get_jwt_identity()
    req[JWTConfig.jwt_identity] = identity
    response = task_delete_comment_warden(**req)

    return jsonify(response)


@app.route('/task/add/user', methods=["POST"])
@jwt_required()
def task_add_user():
    req = request.json
    identity = get_jwt_identity()
    req[JWTConfig.jwt_identity] = identity
    response = task_add_user_warden(**req)

    return jsonify(response)


@app.route('/task/delete/user', methods=["POST"])
@jwt_required()
def task_delete_user():
    req = request.json
    identity = get_jwt_identity()
    req[JWTConfig.jwt_identity] = identity
    response = task_delete_user_warden(**req)

    return jsonify(response)


@app.route('/delete/board', methods=["POST"])
@jwt_required()
def delete_board():
    req = request.json
    identity = get_jwt_identity()
    req[JWTConfig.jwt_identity] = identity
    response = delete_board_warden(**req)

    return jsonify(response)


@app.route('/delete/task', methods=["POST"])
@jwt_required()
def delete_task():
    req = request.json
    identity = get_jwt_identity()
    req[JWTConfig.jwt_identity] = identity
    response = delete_task_warden(**req)

    return jsonify(response)


@app.route('/task/add/file', methods=["POST"])
@jwt_required()
def task_add_file():
    files = request.files
    values = request.values
    identity = get_jwt_identity()
    req = {
        "files": files,
        "values": values,
        JWTConfig.jwt_identity: identity
    }
    response = task_add_file_warden(**req)

    return jsonify(response)

@app.route('/task/get/file', methods=["GET"])
@jwt_required()
def task_get_file():
    req = request.json
    identity = get_jwt_identity()
    req[JWTConfig.jwt_identity] = identity
    response = task_get_file_warden(**req)
    if response["status"] == "ok":
        response = send_file(io.BytesIO(response["data"]["filedata"]), download_name=response["data"]["filename"])
        response = make_response(response)
        print(response.get_json())
    return jsonify(response)


@app.route('/task/delete/file', methods=["POST"])
@jwt_required()
def task_delete_file():
    req = request.json
    identity = get_jwt_identity()
    req[JWTConfig.jwt_identity] = identity
    response = task_delete_file_warden(**req)

    return jsonify(response)


@app.route('/trashcan/add/task', methods=["POST"])
@jwt_required()
def trashcan_add_task():
    req = request.json
    identity = get_jwt_identity()
    req[JWTConfig.jwt_identity] = identity
    response = trashcan_add_task_warden(**req)

    return jsonify(response)

@app.route('/trashcan/get/tasks', methods=["GET"])
@jwt_required()
def trashcan_get_tasks():
    req = request.json
    identity = get_jwt_identity()
    req[JWTConfig.jwt_identity] = identity
    response = trashcan_get_tasks_warden(**req)
    return jsonify(response)

@app.route('/trashcan/restore/task', methods=["POST"])
@jwt_required()
def trashcan_restore_task():
    req = request.json
    identity = get_jwt_identity()
    req[JWTConfig.jwt_identity] = identity
    response = trashcan_restore_task_warden(**req)

    return jsonify(response)


@app.route('/trashcan/delete/task', methods=["POST"])
@jwt_required()
def trashcan_delete_task():
    req = request.json
    identity = get_jwt_identity()
    req[JWTConfig.jwt_identity] = identity
    response = trashcan_delete_task_warden(**req)

    return jsonify(response)

if __name__ == '__main__':
    app.config.from_object('src.solution.config.FlaskConfig')
    runs()
    app.run(port=8010, host='127.0.0.1', debug=True)
