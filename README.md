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
