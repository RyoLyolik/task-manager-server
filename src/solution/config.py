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
