# Server

Flask server, which handles request from Client

**Versions**:

- [_Python_](https://www.python.org/downloads/): 3.8-3.9
- [_PostgreSQL_](https://www.postgresql.org/download/): 14
- [_MinIO_](https://min.io/download#/kubernetes): RELEASE.2022-05-08T23-50-31Z

## How to install
***

Install _Python_, _PostgreSQL_, _Minio_. Download the project.
Install `requirements.txt`: `pip install -r requirements.txt`

## How to run
***
### Preparation
Find and edit next row in `alembic.ini`:
```
sqlalchemy.url = postgresql://%USERNAME%:%PASSWORD%@%HOST%/%DB_NAME%
```

Write in console: `alembic upgrade head`

Then edit `Server\config.py`:

```python
from datetime import timedelta
import re


class Config:
    debug = True


class FlaskConfig:
    secret_key = "KEY"
    MAX_CONTENT_LENGTH = 1024 * 1024 * 64
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=48)
    DEBUG = True


class JWTConfig:
    JWT_SECRET_KEY = "please-remember-to-change-me"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=48)
    jwt_identity = "phone_number"


class CORSConfig:
    pass


class DataBaseConfig:
    dbname = "Ivnix"
    user = "postgres"
    password = "user"
    port = '5432'
    if Config.debug:
        host = "localhost"
    else:
        host = str()

    @classmethod
    def get_database_uri(cls):
        return f"postgresql://{cls.user}:{cls.password}@{cls.host}:{cls.port}/{cls.dbname}"


class MinioConfig:
    host = "localhost"
    port = "9000"
    access_key = 'minioadmin'
    secret_key = 'minioadmin'
    main_bucket = "files"
    if Config.debug:
        secure = False
    else:
        secure = True

    @classmethod
    def get_minio_config(cls):
        return {
            "endpoint": f"{cls.host}:{cls.port}",
            "access_key": cls.access_key,
            "secret_key": cls.secret_key,
            "secure": cls.secure
        }
```
### Run
 > Make sure, that previous steps completed. 

**Run _MinIO_:**

**Windows**

Go to the project folder, open _cmd_ and write:
`<MinIO_Folder>/minio server /Data`

**Linux**

Go to the project folder, open _cmd_ and write:
`<Minio_Folder>/minio server /Data`

**Run _server_**:

Just run `server.py`

# How API works

**Default port -** `8010`<br>
**Requests type -** raw JSON
## Routes:
**[User requests](#user-requests)**<br>
 - **[/registration](#registration)**<br>
 - **[/login](#login)**<br>
 - **[/profile/info](#profileinfo)**<br>
 - **[/user/info](#userinfo)**<br>
 - **[/profile/edit](#profileedit)**<br>
 - **[/profile/boards](#profileboards)**<br>

## Requests ans responses
### User requests
### /registration
**Method:** POST<br>
**Accepts**: JSON<br>
Received parameters:
 - phone_number: <_str, REQUIRED_>
 - password: <_str, REQUIRED_>
 - password_confirm: <_str, REQUIRED_>

_Request example_:
```json
{
  "phone_number": "111",
  "password": "qwe123",
  "password_confirm": "qwe123"
}
```
**Response**: JSON<br>
Responses:
 - status
 - access_token

_Response example_:
```json
{
  "access_token": "%TOKEN%",
  "status": "ok"
}
```

### /login
**Method:** POST<br>
**Accepts**: JSON<br>
Received parameters:
 - phone_number: <_str, REQUIRED_>
 - password: <_str, REQUIRED_>

_Request example_:
```json
{
  "phone_number": "111",
  "password": "qwe123"
}
```
**Response**: JSON<br>
Responses:
 - status
 - access_token

_Response example_:
```json
{
  "access_token": "%TOKEN%",
  "status": "ok"
}
```

### /profile/info
**Method:** GET<br>
**Accepts**: JSON<br>
Received headers:
 - Authorization: Bearer: <str, REQUIRED>
 
**Response**: JSON<br>
Responses:
 - access_token
 - data
 - status

_Response example_:
```json
{
    "access_token": "%TOKEN%",
    "data": {
        "profile": {
            "email": "new_email@mail.ru",
            "phone_number": "111",
            "user_id": 20,
            "username": "New name"
        }
    },
    "status": "ok"
}
```

### /user/info
**Method:** GET<br>
**Accepts**: JSON<br>
Received parameters:
 - user_id

Received headers:
 - Authorization: Bearer: <str, REQUIRED>

_Request example_:
```json
{
  "user_id": 21
}
```
**Response**: JSON<br>
Responses:
 - access_token

_Response example_:
```json
{
    "access_token": "%TOKEN%",
    "data": {
        "user": {
            "user_id": 21,
            "username": null
        }
    },
    "status": "ok"
}
```

### /profile/edit
**Method:** POST<br>
**Accepts**: JSON<br>
Received parameters:
 - old_password: <str, REQUIRED>
 - changes: <str, REQUIRED>
   - username: <str, OPTIONAL>
   - phone_number: <str, OPTIONAL>
   - email: <str, OPTIONAL>
   - telegram_id: <str, OPTIONAL>
   - password: <str, OPTIONAL>

_Request example_:
```json
{
    "changes":
    {
        "username":"New name",
        "email": "new_email@mail.ru"
    },
    "old_password": "111"
}
```
**Response**: JSON<br>
Responses:
 - access_token
 - status

_Response example_:
```json
{
  "access_token": "%TOKEN%",
  "status": "ok"
}
```

### /profile/boards
**Method:** GET<br>
**Accepts**: JSON<br>
Received headers:
 - Authorization: Bearer: <str, REQUIRED>

**Response**: JSON<br>
Responses:
 - access_token
 - data
 - status

_Response example_:
```json
{
    "access_token": "%TOKEN%",
    "data": {
        "boards": [
            {
                "board_id": 13,
                "boardname": "New board(POSTMAN|REDESIGN)",
                "color": "blue(IDK)",
                "description": "This board added after porject redesign",
                "user_id": 20,
                "user_position": "admin"
            }
        ]
    },
    "status": "ok"
}
```