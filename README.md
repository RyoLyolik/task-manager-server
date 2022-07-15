# Server

Flask server, which handles request from Client

**Versions**:

- [_Python_](https://www.python.org/downloads/): 3.8-3.9
- [_PostgreSQL_](https://www.postgresql.org/download/): 14
- [_MinIO_](https://min.io/download#/kubernetes): RELEASE.2022-05-08T23-50-31Z

## How to install
***

Install _Python_, _PostgreSQL_, _Minio_. Download the project.
Install `_requirements.txt_`: `pip install -r requirements.txt`

## How to run
***
### Preparation
Find and edit next row in `alembic.ini`:
```
sqlalchemy.url = postgresql://%USERNAME%:%PASSWORD%@%HOST%/%DB_NAME%
```

Then edit `Server\config.py`:

```python
from datetime import timedelta


class FlaskConfig:
    JWT_SECRET_KEY = "YOUR_SECRET_KEY"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)  # session life time
    DEBUG = True


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
**[/profile/edit](#profileedit)**<br>
**[/add/board](#addboard)**<br>
**[/add/task](#addtask)**<br>
**[/board/info](#boardinfo)**<br>
**[/board/edit](#boardedit)**<br>
**[/task/info](#taskinfo)**<br>
**[/task/edit](#taskedit)**<br>
**[/task/add/comment](#taskaddcomment)**<br>
**[/task/delete/performer](#taskdeleteperformer)**<br>
**[/task/delete/supervisor](#taskdeletesupervisor)**<br>
**[/task/delete/comment](#taskdeletecomment)**<br>
**[/delete/board](#deleteboard)**<br>
**[/delete/task](#deletetask)**<br>
**[/user/info](#userinfo)**<br>
## Requests ans responses
### /registration
**Method**: POST

**Receives**:
 - phone_number
 - password
 - password_confirm

**Responses**:
 - access_token

### /login
**Method**: POST

**Recieves**:
 - phone_number
 - password
 - password_confirm

**Responses**
 - access_token

### /profile/info
**Method**: GET

**Receives**
 - access_token

**Responses**
 - access_token
 - user_info
   - id
   - name
   - phone_number
   - email
   - telegram_id
 
### /profile/boards

**Method**: GET

**Receives**
 - access_token

**Responses**
 - access_token
 - board_id
   - name
   - deadline
   - color
   - description

### /profile/edit

**Method**: POST

**Receives**
 - access_token
 - old_password
 - new_name
 - new_phone
 - new_password
 - new_email
 - new_telegram

**Responses**
 - access_token

### /add/board

**Method**: POST

**Receives**
 - access_token
 - name
 - deadline
 - color
 - description

**Responses**
 - access_token

### /add/task

**Method**: POST

**Receives**
 - access_token
 - name
 - board_id
 - description
 - deadline

**Responses**
 - access_token

### /board/info

**Method**: GET

**Receives**
 - access_token
 - board_id

**Responses**
 - access_token
 - board
   - name
   - deadline
   - color
   - description
   - users
     - user_id
       - position
   - tasks
     - task_id
       - name
       - deadline
       - stage
       - description
       - author
       - performer
       - supervisor

### /board/edit

**Method**: POST

**Receives**
 - access_token
 - board_id
 - new_name
 - new_color
 - new_deadline
 - new_description
 - new_user_id
 - new_user_position
 - delete_user

**Responses**
 - access_token

### /task/info

**Method**: GET

**Receives**
 - access_token
 - task_id

**Responses**
 - access_token
 - task
   - name
   - board_id
   - description
   - deadline
   - stage
   - authors
   - performers
   - comments
     - comment_id
       - author
       - content

### /task/edit

**Method**: POST

**Receives**
 - access_token
 - task_id
 - new_name
 - new_deadline
 - new_performer
 - new_supervisor
 - new_description
 - new_stage

**Responses**
 - access_token

### /task/add/comment

**Method**: POST

**Receives**
 - access_token
 - task_id
 - content

**Responses**
 - access_token

### /task/delete/performer

**Method**: POST

**Receives**
 - access_token
 - task_id
 - user_id

**Responses**
 - access_token

### /task/delete/supervisor

**Method**: POST

**Receives**
 - access_token
 - task_id
 - user_id

**Responses**
 - access_token

### /task/delete/comment

**Method**: POST

**Receives**
 - access_token
 - comment_id

**Responses**
 - access_token

### /delete/board

**Method**: POST

**Receives**
 - access_token
 - board_id

**Responses**
 - access_token

### /delete/task

**Method**: POST

**Receives**
 - access_token
 - task_id

**Responses**
 - access_token

### /user/info

**Method**: GET

**Receives**
 - access_token
 - user_id

**Responses**
 - user_info
   - id
   - name