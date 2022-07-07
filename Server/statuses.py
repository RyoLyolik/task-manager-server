from ADDITIONAL import hashing_password


class StatusBuilder:
    RESPONSES = {
        "ok": "ok",
        "wp": "Wrong Password",
        "udne": "User does not exist",
        "br": "Bad request",
        "ur": "Unauthorized request"
    }
    OK = "ok"
    WP = "Wrong Password"
    UDNE = "User does not exist",
    BR = "Bad Request"
    UR = "Unauthorized request"

    @classmethod
    def login(cls, req):
        if "phone" in req:
            if "password" in req:
                return cls.OK
            return "Password field is empty"
        return "Phone field is empty"

    @classmethod
    def registration(cls, req):
        if not ({"password", "password_confirm", "phone"} - req.keys()):
            if req['password'] == req['password_confirm']:
                return cls.OK
            return "Passwords missmatch"
        return cls.BR

    @classmethod
    def add_board(cls, req):
        if not ({"name", "color", "deadline", "description", "users", "author"} - req.keys()):
            if req["author"]:
                return cls.OK
            else:
                return cls.BR
        else:
            return cls.BR

    @classmethod
    def project(cls, req):
        if "user" in req:
            if isinstance(req["user"], dict) and "id" in req["user"]:
                return cls.OK
            return cls.BR
        return cls.BR

    @classmethod
    def add_task(cls, req):
        if not ({"name", "board_id", "deadline", "description", "performers", "author", "supervisor"} - req.keys()):
            if req["author"]:
                return cls.OK
            return cls.UR
        return cls.BR

    @classmethod
    def get_profile(cls, req):
        if "user" in req and isinstance(req["user"], dict):
            if "id" in req["user"] and isinstance(req["user"]["id"], int):
                return cls.OK
            return cls.BR
        return cls.UR
