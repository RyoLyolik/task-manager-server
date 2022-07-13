from datetime import timedelta
import re

class FlaskConfig:
    secret_key = "KEY"
    DEBUG = True

class JWTConfig:
    JWT_SECRET_KEY = "please-remember-to-change-me"
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=48)

class CORSConfig:
    resources = {
        r"/*":{ # куда будут приходить запросы (в данном случае на любой адрес сервера)
            "origins": r"https://localhost:3000/*" # откуда будут приходить запросы
        }
    }

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
