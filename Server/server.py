#Тут обработка запросов сервером

from flask import *
import json
app = Flask(__name__)

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "POST":
        """
        Обрабатываем логин форму
        ...
        Сверяем с бд
        ...
        Фигачим ответ
        """
        return dict() # возвращаем json для фронтов
@app.route('/registration', methods=["GET", "POST"])
def registration():
    if request.method == "POST":
        """
        Регаем чела со всеми проверками
        """
        return dict() # возвращаем json для фронтов

@app.route('/project')
def project():
    """
    Добываем инфу о проектах чела исходя из текущей сессии пользователя
    И возвращаем её фронтам в json
    """
    return dict()

@app.route('/profile')
def profile():
    """
    Аналогично добываем инфу о челе и возвращаем её форнтам
    """
    return dict()