from datetime import timedelta
import re


class Config:
    debug = True


class FlaskConfig:
    secret_key = "KEY"
    MAX_CONTENT_LENGTH = 1024 * 1024 * 64
    DEBUG = True


class JWTConfig:
    JWT_SECRET_KEY = "please-remember-to-change-me"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=48)


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
    if Config.debug:
        secure = False
    else:
        secure = True

db = DataBaseConfig()
u = db.get_database_uri()
