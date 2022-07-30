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

start_mappers()


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
    phone_number = get_jwt_identity()
    response = get_object(obj=User, phone_number=phone_number)

    return jsonify(response)


@app.route('/user/info', methods=["GET"])
@jwt_required()
def user_info():
    req = request.json


if __name__ == '__main__':
    app.config.from_object('src.solution.config.FlaskConfig')
    app.run(port=8010, host='127.0.0.1', debug=True)
