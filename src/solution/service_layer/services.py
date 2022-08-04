import datetime
import os

from sqlalchemy.orm import mapper
from src.solution.domain.model import *
from models import model as migration_model
from src.solution.service_layer.unit_of_work import SqlAlchemyUnitOfWork as UoW
from src.solution.service_layer.unit_of_work import MinioSession as FileClient
import _sha3
from flask.json import jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, unset_jwt_cookies
from src.solution.adapters.specification import *
from src.solution.adapters.repository import *
from src.solution.config import JWTConfig

fileclient = None


def make_conditions(obj, operator, **kwargs):
    condition_list = list()
    instance = obj()
    for attr in kwargs:
        if attr in instance.__dict__:
            condition_list.append(getattr(getattr(obj, attr), operator)(kwargs[attr]))
    return condition_list


def start_mappers():
    user_mapper = mapper(User, migration_model.users_table)
    board_mapper = mapper(Board, migration_model.board_table)
    comment_mapper = mapper(Comment, migration_model.comments)
    file_mapper = mapper(File_, migration_model.files)
    task_mapper = mapper(Task, migration_model.tasks_table)
    user_board_mapper = mapper(UserBoard, migration_model.users_boards)
    user_task_mapper = mapper(UserTask, migration_model.users_tasks)
    delete_mapper = mapper(Delete, migration_model.delete_table)


def runs():
    global fileclient
    start_mappers()
    fileclient = FileClient()


def hashing_password(password, phone):
    hash_ = _sha3.sha3_256((str(password) + str(phone)).encode("utf-8")).hexdigest()
    return hash_


def get_object(obj, **kwargs):
    req = obj(**kwargs).dict()

    conditions = make_conditions(obj=obj, operator=Matches.eq, **req)
    specification = SqlAlchemySpecification.and_specification(conditions)
    with UoW(obj=obj) as uow:
        row = SqlAlchemyRepository.get(obj=obj, session=uow.session, specification=specification)
        if row:
            answer: obj = row[obj.classname]
        else:
            answer = None

    return answer


def get_objects(obj, **kwargs):
    req = obj(**kwargs).dict()

    conditions = make_conditions(obj=obj, operator=Matches.eq, **req)
    specification = SqlAlchemySpecification.and_specification(conditions)
    with UoW(obj=obj) as uow:
        rows = SqlAlchemyRepository.list(obj=obj, session=uow.session, specification=specification)
        if rows:
            answer: obj = [row[obj.classname] for row in rows]
        else:
            answer = None

    return answer


def create_object(obj, **kwargs):
    instance = obj(**kwargs)
    with UoW(obj=obj) as uow:
        specification = SqlAlchemySpecification.values_specification(**instance.dict())
        answer = SqlAlchemyRepository.add(obj=obj, session=uow.session, specification=specification)
        uow.commit()
    return answer


def update_object(obj, previous_instance, **kwargs):
    instance = obj(**kwargs)
    with UoW(obj=obj) as uow:
        specification = {
            "where": SqlAlchemySpecification.and_specification(
                make_conditions(obj, operator=Matches.eq, **previous_instance.dict())),
            "values": SqlAlchemySpecification.values_specification(**instance.dict())
        }
        SqlAlchemyRepository.update(obj, session=uow.session, specification=specification)
        uow.commit()
    return True


def delete_object(obj, **kwargs):
    instance = obj(**kwargs)
    with UoW(obj=obj) as uow:
        conditions = make_conditions(obj=obj, operator=Matches.eq, **instance.dict())
        specification = SqlAlchemySpecification.and_specification(conditions)
        SqlAlchemyRepository.delete(obj, session=uow.session, specification=specification)
        uow.commit()
    return True


def create_file(**kwargs):
    specification = MinioSpecification.fix_kwargs(**kwargs)
    MinioRepository.add(fileclient.get_session(), specification)
    return True

def get_file(**kwargs):
    specification = MinioSpecification.fix_kwargs(**kwargs)
    file_data = MinioRepository.get(fileclient.get_session(), specification)
    return file_data

def delete_file(**kwargs):
    specification = MinioSpecification.fix_kwargs(**kwargs)
    MinioRepository.delete(fileclient.get_session(), specification)

def login_warden(**kwargs):
    if "phone_number" in kwargs and "password" in kwargs:
        kwargs["password"] = hashing_password(password=kwargs["password"], phone=kwargs["phone_number"])
        original_user = get_object(User, phone_number=kwargs["phone_number"])
        this_user = User(**kwargs)
        comparing = (original_user == this_user)
        if comparing:
            access_token = create_access_token(identity=kwargs[JWTConfig.jwt_identity])
            msg = {
                "status": "Ok",
                "access_token": access_token
            }
        else:
            msg = {
                "status": "Wrong password or phone_number"
            }
    else:
        msg = {
            "status": "Bad request"
        }
    return msg


def registration_warden(**kwargs):
    if "phone_number" in kwargs and "password" in kwargs and "password_confirm" in kwargs:
        exists = get_object(User, phone_number=kwargs["phone_number"])
        if not exists:
            if kwargs["password"] == kwargs["password_confirm"]:
                kwargs["password"] = hashing_password(password=kwargs["password"], phone=kwargs["phone_number"])
                create_object(User, **kwargs)
                access_token = create_access_token(identity=kwargs[JWTConfig.jwt_identity])
                msg = {
                    "status": "Ok",
                    "access_token": access_token
                }
            else:
                msg = {
                    "status": "Password does not match"
                }
        else:
            msg = {
                "status": "User already exist"
            }
    else:
        msg = {
            "status": "Bad request"
        }
    return msg


def unset_session():
    response = jsonify({
        "status": "ok"
    })
    unset_jwt_cookies(response)
    return response


def profile_info_warden(**kwargs):
    msg = dict()
    if JWTConfig.jwt_identity in kwargs:
        user_full_info: dict = get_object(obj=User, **kwargs).dict()
        if user_full_info and "password" in user_full_info:
            user_full_info.pop("password")
            user_save_info = user_full_info
            data = dict()
            data["profile"] = user_save_info
            msg["data"] = data
            msg["status"] = "ok"
        else:
            msg["status"] = "Bad user"
    else:
        msg["status"] = "Bad request"

    return msg


def user_info_warden(**kwargs):
    msg = dict()
    if "user_id" in kwargs:
        user = get_object(obj=User, **kwargs)
        if user:
            user_full_info = user.dict()
            if user_full_info:
                user_save_info = {
                    "name": user_full_info["name"],
                    "user_id": user_full_info["user_id"]
                }
                data = dict()
                data["user"] = user_save_info
                msg["data"] = data
                msg["status"] = "ok"
            else:
                msg["status"] = "Bad user"
        else:
            msg["status"] = "User does not exist"
    else:
        msg["status"] = "Bad request"

    return msg


def board_info_warden(**kwargs):
    msg = dict()
    if JWTConfig.jwt_identity in kwargs and "board_id" in kwargs:
        board = get_object(obj=Board, **kwargs)
        if board:
            user = get_object(obj=User, **kwargs)
            if user:
                user_id = user["user_id"]
                user_board = get_object(obj=UserBoard, user_id=user_id, **kwargs)
                if user_board:
                    data = dict()
                    data["board"] = board.dict()
                    msg["status"] = "ok"
                    msg["data"] = data
                else:
                    msg["status"] = "Access denied"
            else:
                msg["status"] = "User does not exist"
        else:
            msg["status"] = "Bad board"
    else:
        msg["status"] = "Bad request"

    return msg


def profile_boards_warden(**kwargs):
    msg = dict()
    if JWTConfig.jwt_identity in kwargs:
        user = get_object(obj=User, **kwargs)
        if user:
            user_id = user["user_id"]
            user_boards = get_objects(obj=UserBoard, user_id=user_id, **kwargs)
            if user_boards:
                data = list()
                for user_board in user_boards:
                    full_info = dict()
                    if user_board:
                        user_board_info = user_board.dict()
                        board_info = get_object(obj=Board, board_id=user_board_info["board_id"]).dict()
                        full_info = user_board_info | board_info
                    if full_info:
                        data.append(full_info)
                msg["data"] = dict()
                msg["data"]["boards"] = data
                msg["status"] = "ok"
            else:
                msg["status"] = "User has no boards"
        else:
            msg["status"] = "User does not exist"
    else:
        msg["status"] = "Bad request"

    return msg


def board_tasks_warden(**kwargs):
    msg = dict()
    if JWTConfig.jwt_identity in kwargs and "board_id" in kwargs:
        user = get_object(obj=User, **kwargs)
        if user:
            user_id = user["user_id"]
            user_board = get_object(obj=UserBoard, user_id=user_id, **kwargs)
            if user_board:
                tasks = get_objects(obj=Task, **kwargs)

                data = {
                    "tasks": list()
                }
                if tasks:
                    for task in tasks:
                        if task:
                            data["tasks"].append(task.dict())
                msg["data"] = data
                msg["status"] = "Ok"
            else:
                msg["status"] = "Access denied"
        else:
            msg["status"] = "User does not exist"
    else:
        msg["status"] = "Bad request"

    return msg


def board_users_warden(**kwargs):
    msg = dict()
    if "board_id" in kwargs and JWTConfig.jwt_identity in kwargs:
        user = get_object(obj=User, **kwargs)
        if user:
            user_id = user["user_id"]
            user_board = get_object(obj=UserBoard, user_id=user_id, **kwargs)
            if user_board:
                data = {
                    "users": list()
                }
                board = get_object(obj=Board, **kwargs)
                if board:
                    board_users = get_objects(obj=UserBoard, **kwargs)
                    if board_users:
                        for user in board_users:
                            if user:
                                data["users"].append(user.dict())
                    msg["data"] = data
                    msg["status"] = "ok"
                else:
                    msg["status"] = "Board does not exist"
            else:
                msg["status"] = "Access denied"
        else:
            msg["status"] = "User does not exist"
    else:
        msg["status"] = "Bad request"

    return msg


def task_info_warden(**kwargs):
    msg = dict()
    if "task_id" in kwargs and JWTConfig.jwt_identity in kwargs:
        user = get_object(obj=User, **kwargs)
        if user:
            user_id = user["user_id"]
            task = get_object(obj=Task, **kwargs)
            if task:
                board_id = task["board_id"]
                user_board = get_object(obj=UserBoard, user_id=user_id, board_id=board_id)
                if user_board:
                    data = {
                        "task": dict()
                    }
                    if task:
                        data["task"] = task.dict()

                    msg["data"] = data
                    msg["status"] = "ok"
                else:
                    msg["status"] = "Access denied"
            else:
                msg["status"] = "Task does not exist"
        else:
            msg["status"] = "User does not exist"
    else:
        msg["status"] = "Bad request"

    return msg


def task_users_warden(**kwargs):
    msg = dict()
    if "task_id" in kwargs and JWTConfig.jwt_identity in kwargs:
        user = get_object(obj=User, **kwargs)
        if user:
            task = get_object(obj=Task, **kwargs)
            if task:
                task_id = task["task_id"]
                board_id = task["board_id"]
                user_id = user["user_id"]
                user_board = get_object(obj=UserBoard, user_id=user_id, board_id=board_id)
                if user_board:
                    task_users = get_objects(obj=UserTask, user_id=user_id, task_id=task_id)
                    data = {
                        "users": list()
                    }
                    if task_users:
                        for user in task_users:
                            if user:
                                data["users"].append(user.dict())

                    msg["data"] = data
                    msg["status"] = "ok"
                else:
                    msg["status"] = "Access denied"
            else:
                msg["status"] = "Task does not exist"
        else:
            msg["status"] = "User does not exist"
    else:
        msg["status"] = "Bad request"

    return msg


def task_comments_warden(**kwargs):
    msg = dict()
    if "task_id" in kwargs and JWTConfig.jwt_identity in kwargs:
        user = get_object(obj=User, **kwargs)
        if user:
            task = get_object(obj=Task, **kwargs)
            if task:
                task_id = task["task_id"]
                board_id = task["board_id"]
                user_id = user["user_id"]
                user_board = get_object(obj=UserBoard, user_id=user_id, board_id=board_id)
                if user_board:
                    task_comments = get_objects(obj=Comment, task_id=task_id)
                    data = {
                        "comments": list()
                    }
                    if task_comments:
                        for comment in task_comments:
                            if comment:
                                data["comments"].append(comment.dict())

                    msg["data"] = data
                    msg["status"] = "ok"
                else:
                    msg["status"] = "Access denied"
            else:
                msg["status"] = "Task does not exist"
        else:
            msg["status"] = "User does not exist"
    else:
        msg["status"] = "Bad request"

    return msg


def task_files_warden(**kwargs):
    msg = dict()
    if "task_id" in kwargs and JWTConfig.jwt_identity in kwargs:
        user = get_object(obj=User, **kwargs)
        if user:
            task = get_object(obj=Task, **kwargs)
            if task:
                task_id = task["task_id"]
                board_id = task["board_id"]
                user_id = user["user_id"]
                user_board = get_object(obj=UserBoard, user_id=user_id, board_id=board_id)
                if user_board:
                    task_files = get_objects(obj=File_, task_id=task_id)
                    data = {
                        "files": list()
                    }
                    if task_files:
                        for file in task_files:
                            if file:
                                data["files"].append(file.dict())

                    msg["data"] = data
                    msg["status"] = "ok"
                else:
                    msg["status"] = "Access denied"
            else:
                msg["status"] = "Task does not exist"
        else:
            msg["status"] = "User does not exist"
    else:
        msg["status"] = "Bad request"

    return msg


def add_board_warden(**kwargs):
    msg = dict()
    if JWTConfig.jwt_identity in kwargs and "boardname" in kwargs:
        board = Board(**kwargs)
        board_data = board.dict()
        if board_data:
            new_board = create_object(obj=Board, **board_data)

            user = get_object(obj=User, **kwargs)
            if user:
                user_id = user["user_id"]
                user_board = UserBoard(**kwargs)
                user_board_data = user_board.dict()
                user_board_data["user_id"] = user_id
                user_board_data["board_id"] = new_board["board_id"]
                user_board_data["user_position"] = "admin"
                create_object(obj=UserBoard, **user_board_data)
                msg["status"] = "ok"
            else:
                msg["status"] = "User does not exist"
        else:
            msg["status"] = "Bad request"
    else:
        msg["status"] = "Bade request"

    return msg


def add_task_warden(**kwargs):
    msg = dict()
    if JWTConfig.jwt_identity in kwargs and "board_id" in kwargs and "taskname" in kwargs:
        user = get_object(obj=User, **kwargs)
        if user:
            user_id = user["user_id"]
            user_board = get_object(obj=UserBoard, user_id=user_id, board_id=kwargs["board_id"])
            if user_board:
                new_task = create_object(obj=Task, author_id=user_id,**kwargs)
                create_object(obj=UserTask, task_id=new_task["task_id"], user_id=user_id, user_position="author")
                msg["status"] = "ok"
            else:
                msg["status"] = "Access denied"
        else:
            msg["status"] = "User does not exist"
    else:
        msg["status"] = "Bad request"

    return msg


def board_edit_warden(**kwargs):
    msg = dict()
    if JWTConfig.jwt_identity in kwargs and "board_id" in kwargs:
        user = get_object(obj=User, **kwargs)
        if user:
            user_id = user["user_id"]
            previous_board = get_object(obj=Board, board_id=kwargs["board_id"])
            user_board = get_object(obj=UserBoard, board_id=kwargs["board_id"], user_id=user_id, user_position="admin")
            update_object(obj=Board, previous_instance=previous_board, **kwargs)
            if user_board:
                update_object(obj=Board, previous_instance=previous_board, **kwargs)
                msg["status"] = "ok"
            else:
                msg["status"] = "Access denied"
        else:
            msg["status"] = "User does not exist"
    else:
        msg["status"] = "Bad request"

    return msg


def board_add_user_warden(**kwargs):
    msg = dict()
    if JWTConfig.jwt_identity in kwargs and "board_id" in kwargs and "user_id" in kwargs and "user_position" in kwargs:
        user = get_object(obj=User, **{JWTConfig.jwt_identity: kwargs[JWTConfig.jwt_identity]})
        if user:
            user_id = user["user_id"]
            insertion_user = get_object(obj=User, user_id=kwargs["user_id"])
            if insertion_user:
                user_board = get_object(obj=UserBoard, user_id=user_id, board_id=kwargs["board_id"],
                                        user_position="admin")
                if user_board:
                    create_object(obj=UserBoard, **kwargs)
                    msg["status"] = "ok"
                else:
                    msg["status"] = "Access denied"
            else:
                msg["status"] = "User does not exist"
        else:
            msg["status"] = "User does not exist"
    else:
        msg["status"] = "Bad request"

    return msg


def board_delete_user_warden(**kwargs):
    msg = dict()
    if JWTConfig.jwt_identity in kwargs and "board_id" in kwargs and "user_id" in kwargs:
        user = get_object(obj=User, **{JWTConfig.jwt_identity: kwargs[JWTConfig.jwt_identity]})
        if user:
            user_id = user["user_id"]
            insertion_user = get_object(obj=User, user_id=kwargs["user_id"])
            if insertion_user:
                user_board = get_object(obj=UserBoard, user_id=user_id, board_id=kwargs["board_id"],
                                        user_position="admin")
                if user_board:
                    delete_object(obj=UserBoard, user_id=kwargs["user_id"], board_id=kwargs["board_id"])
                    msg["status"] = "ok"
                else:
                    msg["status"] = "Access denied"
            else:
                msg["status"] = "User does not exist"
        else:
            msg["status"] = "User does not exist"
    else:
        msg["status"] = "Bad request"

    return msg


def task_edit_warden(**kwargs):
    msg = dict()
    if JWTConfig.jwt_identity in kwargs and "task_id" in kwargs:
        user = get_object(obj=User, **{JWTConfig.jwt_identity: kwargs[JWTConfig.jwt_identity]})
        if user:
            user_id = user["user_id"]
            previous_task = get_object(obj=Task, task_id=kwargs["task_id"])
            if previous_task:
                board_id = previous_task["board_id"]
                user_board = get_object(obj=UserBoard, user_id=user_id, board_id=board_id, user_position="admin")
                user_task = get_object(obj=UserTask, user_id=user_id, task_id=previous_task["task_id"],
                                       user_position="author")
                if user_board or user_task:
                    update_object(obj=Task, previous_instance=previous_task, **kwargs)
                    msg["status"] = "ok"
                else:
                    msg["status"] = "Access denied"
            else:
                msg["status"] = "Task does not exist"
        else:
            msg["status"] = "User does not exist"
    else:
        msg["status"] = "Bad request"

    return msg


def task_add_comment_warden(**kwargs):
    msg = dict()
    if JWTConfig.jwt_identity in kwargs and "task_id" in kwargs and "content" in kwargs:
        user = get_object(obj=User, **{JWTConfig.jwt_identity: kwargs[JWTConfig.jwt_identity]})
        if user:
            user_id = user["user_id"]
            task = get_object(obj=Task, task_id=kwargs["task_id"])
            if task:
                board_id = task["board_id"]
                user_board = get_object(obj=UserBoard, board_id=board_id, user_id=user_id)
                if user_board:
                    create_object(Comment,
                                  author_id=user_id,
                                  board_id=board_id,
                                  date_time=datetime.datetime.now(),
                                  **kwargs)
                    msg["status"] = "ok"

                else:
                    msg["status"] = "Access denied"
        else:
            msg["status"] = "User does not exist"
    else:
        msg["status"] = "Bad request"

    return msg


def task_add_user_warden(**kwargs):
    msg = dict()
    if JWTConfig.jwt_identity in kwargs and "task_id" in kwargs and "user_id" in kwargs and "user_position" in kwargs:
        if kwargs["user_position"] == "performer" or kwargs["user_position"] == "supervisor":
            user = get_object(obj=User, **{JWTConfig.jwt_identity: kwargs[JWTConfig.jwt_identity]})
            if user:
                user_id = user["user_id"]
                task = get_object(obj=Task, task_id=kwargs["task_id"])
                if task:
                    user_task = get_object(obj=UserTask, user_id=user_id, task_id=task["task_id"],
                                           user_position="author")
                    user_board = get_object(obj=UserBoard, user_id=user_id, board_id=task["board_id"],
                                            user_position="admin")
                    if user_task or user_board:
                        check_user = get_object(obj=UserTask,
                                                user_id=kwargs["user_id"],
                                                task_id=kwargs["task_id"],
                                                user_position=kwargs["user_position"])
                        if not check_user:
                            create_object(obj=UserTask,
                                          user_id=kwargs["user_id"],
                                          task_id=kwargs["task_id"],
                                          user_position=kwargs["user_position"])

                            msg["status"] = "ok"
                        else:
                            msg["status"] = "Already exists"
                    else:
                        msg["status"] = "Access denied"
                else:
                    msg["status"] = "Task does not exist"
            else:
                msg["status"] = "User does not exist"
        else:
            msg["status"] = f"Wrong user position:{kwargs['user_position']}"
    else:
        msg["status"] = "Bad request"

    return msg


def task_delete_user_warden(**kwargs):
    msg = dict()
    if JWTConfig.jwt_identity in kwargs and "task_id" in kwargs and "user_id" in kwargs and "user_position" in kwargs:
        if kwargs["user_position"] == "performer" or kwargs["user_position"] == "supervisor":
            user = get_object(obj=User, **{JWTConfig.jwt_identity: kwargs[JWTConfig.jwt_identity]})
            if user:
                user_id = user["user_id"]
                task = get_object(obj=Task, task_id=kwargs["task_id"])
                if task:
                    user_task = get_object(obj=UserTask, user_id=user_id, task_id=task["task_id"],
                                           user_position="author")
                    user_board = get_object(obj=UserBoard, user_id=user_id, board_id=task["board_id"],
                                            user_position="admin")
                    if user_task or user_board:
                        check_user = get_object(obj=UserTask,
                                                user_id=kwargs["user_id"],
                                                task_id=kwargs["task_id"],
                                                user_position=kwargs["user_position"])
                        if check_user:
                            delete_object(obj=UserTask,
                                          user_id=kwargs["user_id"],
                                          task_id=kwargs["task_id"],
                                          user_position=kwargs["user_position"])

                            msg["status"] = "ok"
                        else:
                            msg["status"] = "Does not exist"
                    else:
                        msg["status"] = "Access denied"
                else:
                    msg["status"] = "Task does not exist"
            else:
                msg["status"] = "User does not exist"
        else:
            msg["status"] = f"Wrong user position:{kwargs['user_position']}"
    else:
        msg["status"] = "Bad request"

    return msg


def profile_edit_warden(**kwargs):
    msg = dict()
    if JWTConfig.jwt_identity in kwargs and "changes" in kwargs and "old_password" in kwargs and isinstance(
            kwargs["changes"], dict):
        user = get_object(obj=User, **{JWTConfig.jwt_identity: kwargs[JWTConfig.jwt_identity]})
        if user:
            old_password_hash = user["password"]
            hash_check = hashing_password(password=kwargs["old_password"], phone=user["phone_number"])
            if hash_check == old_password_hash:
                if "password" in kwargs["changes"]:
                    if "phone_number" not in kwargs["changes"]:
                        kwargs["changes"]["phone_number"] = user["phone_number"]
                    if "password" in kwargs["changes"]:
                        kwargs["changes"]["password"] = hashing_password(password=kwargs["changes"]["password"],
                                                                         phone=kwargs["changes"]["phone_number"])
                    else:
                        kwargs["changes"]["password"] = hashing_password(password=kwargs["old_password"],
                                                                         phone=kwargs["changes"]["phone_number"])

                update_object(obj=User, previous_instance=user, **kwargs["changes"])
                msg["status"] = "ok"
            else:
                msg["status"] = "Access denied"
        else:
            msg["status"] = "User does not exist"
    else:
        msg["status"] = "Bad request"

    return msg


def task_delete_comment_warden(**kwargs):
    msg = dict()
    if JWTConfig.jwt_identity in kwargs and "comment_id" in kwargs:
        user = get_object(obj=User, **{JWTConfig.jwt_identity: kwargs[JWTConfig.jwt_identity]})
        if user:
            user_id = user["user_id"]
            comment = get_object(obj=Comment, comment_id=kwargs["comment_id"])
            if comment:
                author_id = comment["author_id"]
                if user_id == author_id:
                    delete_object(obj=Comment, comment_id=kwargs["comment_id"])
                    msg["status"] = "ok"
                else:
                    msg["status"] = "Access denied"
            else:
                msg["status"] = "Comment does not exist"
        else:
            msg["status"] = "User does not exist"
    else:
        msg["status"] = "Bad request"

    return msg


def delete_board_warden(**kwargs):
    msg = dict()
    if JWTConfig.jwt_identity in kwargs and "board_id" in kwargs:
        user = get_object(obj=User, **kwargs)
        if user:
            user_id = user["user_id"]
            user_board = get_object(obj=UserBoard, board_id=kwargs["board_id"], user_id=user_id, user_position="admin")
            if user_board:
                board = get_object(obj=Board, board_id=kwargs["board_id"])
                if board:
                    delete_object(obj=UserBoard, board_id=kwargs["board_id"])
                    board_tasks = get_objects(obj=Task, board_id=kwargs["board_id"])
                    if board_tasks:
                        for task in board_tasks:
                            if task:
                                files = get_objects(obj=File_, task_id=task["task_id"])
                                if files:
                                    for file in files:
                                        file_type = file["filename"].split(".")[-1]
                                        filename = str(file["file_id"]) + "." + file_type
                                        delete_file(object_name=filename)
                                    delete_object(obj=File_, task_id=task["task_id"])
                                    delete_object(obj=UserTask, task_id=task["task_id"])

                    delete_object(obj=Task, board_id=kwargs["board_id"])
                    delete_object(obj=Comment, board_id=kwargs["board_id"])
                    delete_object(obj=Board, board_id=kwargs["board_id"])
                    msg["status"] = "ok"
                else:
                    msg["status"] = "Board does not exist"
            else:
                msg["status"] = "Access denied"
        else:
            msg["status"] = "User does not exist"
    else:
        msg["status"] = "Bad request"

    return msg


def delete_task_warden(**kwargs):
    msg = dict()
    if JWTConfig.jwt_identity in kwargs and "task_id" in kwargs:
        user = get_object(obj=User, **kwargs)
        if user:
            user_id = user["user_id"]
            task = get_object(obj=Task, task_id=kwargs["task_id"])
            if task:
                user_board = get_object(obj=UserBoard, board_id=task["board_id"], user_id=user_id,
                                        user_position="admin")
                user_task = get_object(obj=UserTask, task_id=kwargs["task_id"], user_id=user_id, user_position="author")
                if user_board or user_task:
                    delete_object(obj=Comment, task_id=kwargs["task_id"])
                    delete_object(obj=UserTask, task_id=kwargs["task_id"])
                    files = get_objects(obj=File_, task_id=kwargs["task_id"])
                    if files:
                        for file in files:
                            file_type = file["filename"].split(".")[-1]
                            filename = str(file["file_id"]) + "." + file_type
                            delete_file(object_name=filename)
                    delete_object(obj=File_, task_id=kwargs["task_id"])
                    delete_object(obj=Task, task_id=kwargs["task_id"])
                    msg["status"] = "ok"
                else:
                    msg["status"] = "Access denied"
            else:
                msg["status"] = "Task does not exist"
        else:
            msg["status"] = "User does not exist"
    else:
        msg["status"] = "Bad request"

    return msg


def task_add_file_warden(**kwargs):
    msg = dict()
    if JWTConfig.jwt_identity in kwargs and "values" in kwargs and "files" in kwargs and "task_id" in kwargs[
        "values"] and kwargs["files"]:
        user = get_object(obj=User, **{JWTConfig.jwt_identity: kwargs[JWTConfig.jwt_identity]})
        if user:
            task = get_object(obj=Task, task_id=kwargs["values"]["task_id"])
            if task:
                user_board = get_object(obj=UserBoard, user_id=user["user_id"], board_id=task["board_id"])
                if user_board:
                    file = kwargs["files"]["file"]
                    filename = file.filename
                    name_type = filename.split('.')
                    if len(name_type) >= 2:
                        filetype = name_type[-1]
                        created_file = create_object(obj=File_, filename=filename, task_id=task["task_id"],
                                                     author_id=user["user_id"])
                        file_id = created_file["file_id"]
                        new_name = str(file_id) + '.' + filetype

                        file.save('MINIO_TEMP_FILE')
                        file.close()

                        file = open("MINIO_TEMP_FILE", "rb")
                        file_stat = os.stat("MINIO_TEMP_FILE")
                        filesize = file_stat.st_size

                        file_info = {
                            "data": file,
                            "object_name": new_name,
                            "length": filesize
                        }
                        create_file(**file_info)
                        file.close()
                        msg["status"] = "ok"
                    else:
                        msg["status"] = "Wrong filename"
                else:
                    msg["status"] = "Access denied"
            else:
                msg["status"] = "Task does not exist"
        else:
            msg["status"] = "User does not exist"
    else:
        msg["status"] = "Bad request"

    return msg


def task_get_file_warden(**kwargs):
    msg = dict()
    if "file_id" in kwargs and JWTConfig.jwt_identity in kwargs:
        user = get_object(obj=User, **{JWTConfig.jwt_identity: kwargs[JWTConfig.jwt_identity]})
        if user:
            file = get_object(obj=File_, file_id=kwargs["file_id"])
            if file:
                task = get_object(obj=Task, task_id=file["task_id"])
                if task:
                    user_board = get_object(obj=UserBoard, user_id=user["user_id"], board_id=task["board_id"])
                    if user_board:
                        file_info = get_object(obj=File_, file_id=kwargs["file_id"])
                        if file_info:
                            file_type = file["filename"].split(".")[-1]
                            filename = str(kwargs["file_id"]) + "." + file_type
                            file_data = get_file(object_name=filename)
                            msg["status"] = "ok"
                            data = {
                                "filedata": file_data,
                                "filename": file_info["filename"]
                            }
                            msg["data"] = data
                        else:
                            msg["status"] = "File does not exist"
                    else:
                        msg["status"] = "Access denied"
                else:
                    msg["status"] = "Task does not exist"
            else:
                msg["status"] = "File does not exist"
        else:
            msg["status"] = "User does not exist"
    else:
        msg["status"] = "Bad request"
    return msg


def task_delete_file_warden(**kwargs):
    msg = dict()
    if "file_id" in kwargs and JWTConfig.jwt_identity in kwargs:
        user = get_object(obj=User, **{JWTConfig.jwt_identity: kwargs[JWTConfig.jwt_identity]})
        if user:
            file = get_object(obj=File_, file_id=kwargs["file_id"])
            if file:
                task = get_object(obj=Task, task_id=file["task_id"])
                if task:
                    user_board = get_object(obj=UserBoard, user_id=user["user_id"], board_id=task["board_id"], user_position="admin")
                    file_info = get_object(obj=File_, file_id=kwargs["file_id"])
                    if file_info:
                        if user_board or file_info["author_id"] == user["user_id"]:
                            file_type = file["filename"].split(".")[-1]
                            filename = str(kwargs["file_id"]) + "." + file_type
                            delete_file(object_name=filename)
                            delete_object(obj=File_, file_id=kwargs["file_id"])
                            msg["status"] = "ok"
                        else:
                            msg["status"] = "Access denied"
                    else:
                        msg["status"] = "File does not exist"
                else:
                    msg["status"] = "Task does not exist"
            else:
                msg["status"] = "File does not exist"
        else:
            msg["status"] = "User does not exist"
    else:
        msg["status"] = "Bad request"
    return msg


def trashcan_add_task_warden(**kwargs):
    msg = dict()
    if JWTConfig.jwt_identity in kwargs and "task_id" in kwargs:
        user = get_object(obj=User, **kwargs)
        if user:
            user_id = user["user_id"]
            task = get_object(obj=Task, task_id=kwargs["task_id"])
            if task:
                user_board = get_object(obj=UserBoard, board_id=task["board_id"], user_id=user_id,
                                        user_position="admin")
                user_task = get_object(obj=UserTask, task_id=kwargs["task_id"], user_id=user_id, user_position="author")
                if user_board or user_task:
                    create_object(obj=Delete, **task.dict())
                    delete_object(obj=Comment, task_id=kwargs["task_id"])
                    delete_object(obj=UserTask, task_id=kwargs["task_id"])
                    files = get_objects(obj=File_, task_id=kwargs["task_id"])
                    if files:
                        for file in files:
                            file_type = file["filename"].split(".")[-1]
                            filename = str(file["file_id"]) + "." + file_type
                            delete_file(object_name=filename)
                    delete_object(obj=File_, task_id=kwargs["task_id"])
                    delete_object(obj=Task, task_id=kwargs["task_id"])
                    msg["status"] = "ok"
                else:
                    msg["status"] = "Access denied"
            else:
                msg["status"] = "Task does not exist"
        else:
            msg["status"] = "User does not exist"
    else:
        msg["status"] = "Bad request"

    return msg

def trashcan_get_tasks_warden(**kwargs):
    msg = dict()
    if JWTConfig.jwt_identity in kwargs and "board_id" in kwargs:
        user = get_object(obj=User, **kwargs)
        if user:
            user_id = user["user_id"]
            user_board = get_object(obj=UserBoard, board_id=kwargs["board_id"], user_id=user_id)
            if user_board:
                data = {
                    "tasks": list()
                }
                tasks = get_objects(obj=Delete, board_id=kwargs["board_id"])
                if tasks:
                    for task in tasks:
                        if task:
                            data["tasks"].append(task.dict())
                msg["data"] = data
                msg["status"] = "ok"
            else:
                msg["status"] = "Access denied"
        else:
            msg["status"] = "User does not exist"
    else:
        msg["status"] = "Bad request"

    return msg


def trashcan_restore_task_warden(**kwargs):
    msg = dict()
    if JWTConfig.jwt_identity in kwargs and "task_id" in kwargs:
        user = get_object(obj=User, **kwargs)
        if user:
            user_id = user["user_id"]
            task = get_object(obj=Delete, task_id=kwargs["task_id"])
            if task:
                user_board = get_object(obj=UserBoard, board_id=task["board_id"], user_id=user_id,
                                        user_position="admin")
                if user_board or task["author_id"] == user["user_id"]:
                    delete_object(obj=Delete, **task.dict())
                    create_object(obj=Task, **task.dict())
                    create_object(obj=UserTask, task_id=kwargs["task_id"], user_id=task["author_id"], user_position="author")
                    msg["status"] = "ok"
                else:
                    msg["status"] = "Access denied"
            else:
                msg["status"] = "Task does not exist"
        else:
            msg["status"] = "User does not exist"
    else:
        msg["status"] = "Bad request"

    return msg

def trashcan_delete_task_warden(**kwargs):
    msg = dict()
    if JWTConfig.jwt_identity in kwargs and "task_id" in kwargs:
        user = get_object(obj=User, **kwargs)
        if user:
            user_id = user["user_id"]
            task = get_object(obj=Delete, task_id=kwargs["task_id"])
            if task:
                user_board = get_object(obj=UserBoard, board_id=task["board_id"], user_id=user_id,
                                        user_position="admin")
                if user_board or task["author_id"] == user["user_id"]:
                    delete_object(obj=Delete, **task.dict())
                    msg["status"] = "ok"
                else:
                    msg["status"] = "Access denied"
            else:
                msg["status"] = "Task does not exist"
        else:
            msg["status"] = "User does not exist"
    else:
        msg["status"] = "Bad request"

    return msg