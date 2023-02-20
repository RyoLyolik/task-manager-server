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

Then edit `src\solution\config.py`:

```python
from datetime import timedelta
import re


class Config:
    debug = True


class FlaskConfig:
    secret_key = "KEY"
    MAX_CONTENT_LENGTH = 1024 * 1024 * 64
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=48)
    DEBUG = Config.debug


class JWTConfig:
    JWT_SECRET_KEY = "please-remember-to-change-me"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=48)
    jwt_identity = "phone_number"


class CORSConfig:
    pass


class DataBaseConfig:
    dbname = "TaskMan"
    user = "centos"
    password = "centos"
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
    secure = not Config.debug

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

Just run `flask_app.py`
