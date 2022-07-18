import json
import re
import requests
from random import choice

HOST = "http://127.0.0.1:8010"

USER = {
    "phone": "89605187783",
    "password": "123123",
    "password_confirm": "123123"
}


def test(test_params: dict):
    url = HOST + test_params["address"]
    request = test_params["request"]
    method = test_params["method"]
    if "headers" in test_params:
        hdrs = test_params["headers"]
    else:
        hdrs = dict()
    resp_str = requests.request(method, url, json=request, headers=hdrs).content
    resp = json.loads(resp_str)
    return resp


def test_registration():
    Q = {
        "request":
            {
                "phone": ''.join([str(choice(range(10))) for _ in range(16)]),
                "password": "qwe123",
                "password_confirm": "qwe123"
            },
        "address": "/registration",
        "method": "POST"
    }
    answer = test(Q)
    print(f"Usual registration test: {answer['status']}")
    Q["request"]["password"] = "qwe12"
    answer = test(Q)
    print(f"Password missmatch registration: {answer['status']}")
    Q["request"]["phone"] = "123"
    Q["request"]["password"] = "qwe123"
    answer = test(Q)
    print(f"Registration existing user test: {answer['status']}")


def test_login():
    Q = {
        "request":
            {
                "phone": ''.join([str(choice(range(10))) for _ in range(16)]),
                "password": "qwe1233"
            },
        "address": "/login",
        "method": "POST"
    }
    answer = test(Q)
    print(f"Not existing user log in: {answer['status']}")
    Q["request"]["phone"] = '123'
    answer = test(Q)
    print(f"Wrong password log in test: {answer['status']}")
    Q["request"]["phone"] = "123"
    Q["request"]["password"] = "qwe123"
    answer = test(Q)
    print(f"Alright log in test: {answer['status']}")


def test_add_board():
    prepare_req = {
        "request":
            {
                "phone": '123',
                "password": "qwe123"
            },
        "address": "/login",
        "method": "POST"
    }
    answer = test(prepare_req)
    access_token = answer["access_token"]
    Q = {
        "request":
            {
                "name": "Unit_test board",
                "color": "blue",
                "description": "this is board that added with tests",
                "author": "1",
                "users": [],
                "deadline": None
            },
        "address": "/add/board",
        "method": "POST",
        "headers":
            {
                'Authorization': 'Bearer ' + access_token
            }
    }
    answer = test(Q)
    print(f"Add board test: {answer['status']}")


def test_projects():
    prepare_req = {
        "request":
            {
                "phone": '123',
                "password": "qwe123"
            },
        "address": "/login",
        "method": "POST"
    }
    answer = test(prepare_req)
    access_token = answer["access_token"]
    Q = {
        "request":
            {
                "user":
                    {
                        "id": "1"
                    }
            },
        "address": "/projects",
        "method": "POST",
        "headers":
            {
                'Authorization': 'Bearer ' + access_token
            }
    }
    answer = test(Q)
    print(f"Project test: {answer['status']}")


def test_add_task():
    prepare_req = {
        "request":
            {
                "phone": '123',
                "password": "qwe123"
            },
        "address": "/login",
        "method": "POST"
    }
    answer = test(prepare_req)
    access_token = answer["access_token"]
    Q = {
        "request":
            {
                "name": "Test task",
                "board_id": "2",
                "deadline": None,
                "description": "This is test task added with tests",
                "author": "1",
                "supervisor": "1",
                "performers": "1"
            },
        "address": "/add/task",
        "method": "POST",
        "headers":
            {
                'Authorization': 'Bearer ' + access_token
            }
    }
    answer = test(Q)
    print(f"Add task test: {answer['status']}")


def test_profile():
    prepare_req = {
        "request":
            {
                "phone": '123',
                "password": "qwe123"
            },
        "address": "/login",
        "method": "POST"
    }
    answer = test(prepare_req)
    access_token = answer["access_token"]
    Q = {
        "request":
            {
                "name": "Test task",
                "board_id": "2",
                "deadline": None,
                "description": "This is test task added with tests",
                "author": "1",
                "supervisor": "1",
                "performers": "1"
            },
        "address": "/profile",
        "method": "POST",
        "headers":
            {
                'Authorization': 'Bearer ' + access_token
            }
    }
def test_all():
    test_registration()
    test_login()
    test_add_board()
    test_projects()
    test_add_task()


def main(test_=None):
    if test_ is None:
        test_all()

    else:
        test_()


if __name__ == "__main__":
    main()
