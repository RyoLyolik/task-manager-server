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


class FlaskConfig:
    secret_key = "KEY"
    DEBUG = True


class JWTConfig:
    JWT_SECRET_KEY = "please-remember-to-change-me"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=48) # session lifetime


class CORSConfig:
    pass


class DataBaseConfig:
    dbname = "Ivnix"
    user = "postgres"
    password = "user"
    host = "localhost"


class MinioConfig:
    host = "localhost:9000"
    access_key = 'minioadmin'
    secret_key = 'minioadmin'
    secure = False
```
### Run
Make sure, that previous steps completed. 

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
**[/registration](#registration)**<br>
**[/login](#login)**<br>
**[/profile/info](#profileinfo)**<br>
**[/profile/boards](#profileboards)**<br>
**[/user/info](#userinfo)**<br>
**[/profile/edit](#profileedit)**<br>
**[/board/info](#boardinfo)**<br>
**[/add/board](#addboard)**<br>
**[/board/edit](#boardedit)**<br>
**[/delete/board](#deleteboard)**<br>
**[/board/add/user](#boardadduser)**<br>
**[/board/delete/user](#boarddeleteuser)**<br>
**[/task/info](#taskinfo)**<br>
**[/add/task](#addtask)**<br>
**[/task/edit](#taskedit)**<br>
**[/task/add/comment](#taskaddcomment)**<br>
**[/task/delete/comment](#taskdeletecomment)**<br>
**[/delete/task](#deletetask)**<br>
**[/task/add/user](#taskadduser)**<br>
## Requests ans responses

### /registration
_Use it in registration_<br>
**Method:** POST

**Receives:**
 - phone_number
 - password
 - password_confirm

**Responses:**
 - access_token

### /login
_Use it in login_<br>
**Method:** POST

**Receives:**
 - phone_number
 - password

**Responses:**
 - access_token

### /profile/info
_Use it find out info about user_<br>
**Method:** GET

**Receives:**
 - access_token

**Responses:**
 - access_token
 - user_id
 - name
 - phone_number
 - email
 - telegram_id

### /user/info
_Use it to find out info about some user_<br>
**Method:** GET

**Receives:**
 - access_token

**Responses:**
 - access_token
 - user_id
 - name
 
### /profile/edit
_Use it to edit user profile_<br>
**Method:** POST

**Receives:**
 - access_token
 - changes
   - name
   - phone_number
   - password
   - email
   - telegram_id
 - old_password

**Responses:**
 - access_token

### /profile/boards
_Use it to find out user boards_<br>
**Method:** GET

**Receives:**
 - access_token

**Responses:**
 - access_token
 - boards
   - board_id
     - board_id
     - name
     - deadline
     - color
     - description





### /board/info
_Use it to find out board info_<br>
**Method:** GET

**Receives:**
 - access_token
 - board_id

**Responses:**
 - access_token
 - board
   - board_id
   - name
   - deadline
   - color
   - description
   - tasks
     - task_id
       - name
       - deadline
       - description
       - authors
         - user_id
           - user_id
           - name
       - performers
         - user_id
           - user_id
           - name
       - supervisors
         - user_id
           - user_id
           - name
 
### /add/board
_Use it to add new board_<br>
**Method:** POST

**Receives:**
 - access_token
 - name
 - deadline
 - color
 - description

**Responses:**
 - access_token

### /board/edit
_Use it to edit board_<br>
**Method:** POST

**Receives:**
 - access_token
 - name
 - deadline
 - color
 - description

**Responses:**
 - access_token

### /delete/board
_Use it to delete board_<br>
**Method:** POST

**Receives:**
 - access_token
 - board_id

**Responses:**
 - access_token

### /board/add/user
_Use it to add new user on board_<br>
**Method:** POST

**Receives:**
 - access_token
 - board_id
 - user_id
 - user_position

**Responses:**
 - access_token

### /board/delete/user
_Use it to delete user from board_<br>
**Method:** POST

**Receives:**
 - access_token
 - board_id
 - user_id

**Responses:**
 - access_token

### /task/info
_Use it to find out info about task_<br>
**Method:** GET

**Receives:**
 - access_token
 - task_id

**Responses:**
 - access_token
 - name
 - deadline
 - description
 - authors
   - user_id
     - user_id
     - name
 - performers
   - user_id
     - user_id
     - name
 - supervisors
   - user_id
     - user_id
     - name
 - comments
   - comment_id
     - comment_id
     - task_id
     - content
     - date_time
     - author_id
     - board_id
   
### /add/task
_Use it to add new task_<br>
**Method:** POST

**Receives:**
 - access_token
 - name
 - board_id
 - description
 - deadline
 - stage

**Responses:**
 - access_token

### /task/edit
_Use it to edit task_<br>
**Method:** POST

**Receives:**
 - access_token
 - name
 - description
 - deadline
 - stage

**Responses:**
 - access_token

### /task/add/comment
_Use it to add task new comment_<br>
**Method:** POST

**Receives:**
 - access_token
 - task_id
 - content

**Responses:**
 - access_token

### /task/delete/comment
_Use it to delete task comment_<br>
**Method:** POST

**Receives:**
 - access_token
 - comment_id

**Responses:**
 - access_token

### /delete/task
_Use it to delete task_<br>
**Method:** POST

**Receives:**
 - access_token
 - task_id

**Responses:**
 - access_token

### /task/add/user
_Use it to add new author/performer/supervisor for the task_<br>
**Method:** POST

**Receives:**
 - access_token
 - task_id
 - user_id
 - user_position

**Responses:**
 - access_token

### /task/delete/user
_Use it to delete user from task_<br>
**Method:** POST

**Receives:**
 - access_token
 - task_id
 - user_id

**Responses:**
 - access_token
