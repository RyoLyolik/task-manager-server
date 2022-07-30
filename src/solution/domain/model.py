from dataclasses import dataclass

class User(object):
    classname = "User"
    def __init__(self, user_id: int = None, name: str = None, phone_number: str = None, password: str = None, email: str = None, telegram_id: int = None, **kwargs):
        self.user_id = user_id
        self.name = name
        self.phone_number = phone_number
        self.password = password
        self.email = email
        self.telegram_id = telegram_id

        self._ref = self.user_id

    def __hash__(self):
        return hash(self._ref)

    def __eq__(self, other):
        if isinstance(other, User):
            return (self.user_id == other.user_id or self.phone_number == other.phone_number) and self.password == other.password
        return False

    def dict(self):
        D = {
            "user_id": self.user_id,
            "name": self.name,
            "phone_number": self.phone_number,
            "password":self.password,
            "email": self.email,
            "telegram_id": self.telegram_id
        }
        res = dict()
        for param in D:
            if D[param]:
                res[param] = D[param]
        return res




class Board(object):
    classname = "Board"
    def __init__(self, board_id: int = None, name: str = None, deadline = None, color: str = None, description: str = None, **kwargs):
        self.board_id = board_id
        self.name = name
        self.deadline = deadline
        self.color = color
        self.description = description

        self._ref = board_id

    def __hash__(self):
        return hash(self._ref)


class Comment(object):
    classname = "Comment"
    def __init__(self, comment_id: int = None, task_id: int = None, content: str = None, date_time = None, author_id: int = None, board_id: str = None, **kwargs):
        self.comment_id = comment_id
        self.task_id = task_id
        self.content = content
        self.date_time = date_time
        self.author_id = author_id
        self.board_id = board_id

        self._ref = self.comment_id

    def __hash__(self):
        return hash(self._ref)


class File_(object):
    classname = "File_"
    def __init__(self, file_id: int = None, task_id: int = None, filename: str = None, author_id: int = None, **kwargs):
        self.file_id = file_id
        self.task_id = task_id
        self.filename = filename
        self.author_id = author_id

        self._ref = file_id

    def __hash__(self):
        return hash(self._ref)


class Task(object):
    classname = "Task"
    def __init__(self, task_id: int = None, name: str = None, board_id: int = None, description: str = None, deadline = None, stage: int = None, **kwargs):
        self.task_id = task_id
        self.name = name
        self.board_id = board_id
        self.description = description
        self.deadline = deadline
        self.stage = stage

        self._ref = task_id

    def __hash__(self):
        return hash(self._ref)


class UserBoard(object):
    classname = "UserBoard"
    def __init__(self, user_id: int = None, board_id: int = None, user_position: str = None, **kwargs):
        self.user_id = user_id
        self.board_id = board_id
        self.user_position = user_position

        self._ref = hash(user_id) + hash(board_id)

    def __hash__(self):
        return hash(self._ref)


class UserTask(object):
    classname = "UserTask"
    def __init__(self, user_id: int = None, task_id: int = None, user_position: str = None, **kwargs):
        self.user_id = user_id
        self.task_id = task_id
        self.user_position = user_position

        self._ref = hash(user_id) + hash(task_id)

    def __hash__(self):
        return hash(self._ref)

@dataclass(frozen=True)
class Matches:
    eq = '__eq__'
    lt = '__lt__'
    le = '__le__'
    ne = '__ne__'
    gt = '__gt__'
    ge = '__ge__'