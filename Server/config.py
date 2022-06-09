from datetime import timedelta


class FlaskConfig:
    JWT_SECRET_KEY = "please-remember-to-change-me"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)
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
