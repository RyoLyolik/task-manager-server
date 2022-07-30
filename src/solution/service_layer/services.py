from sqlalchemy.orm import mapper
from src.solution.domain.model import *
from models import model as migration_model
from src.solution.service_layer.unit_of_work import SqlAlchemyUnitOfWork as UoW
import _sha3
from flask.json import jsonify
from flask_jwt_extended import create_access_token, get_jwt_identity, unset_jwt_cookies
from src.solution.adapters.specification import *
from src.solution.adapters.repository import *

def make_conditions(obj, operator, **kwargs):
    condition_list = list()
    instance = obj()
    for attr in kwargs:
        if attr in instance.__dict__:
            condition_list.append(getattr(getattr(User, attr), operator)(kwargs[attr]))
    return condition_list


def start_mappers():
    user_mapper = mapper(User, migration_model.users_table)
    board_mapper = mapper(Board, migration_model.board_table)
    comment_mapper = mapper(Comment, migration_model.comments)
    file_mapper = mapper(File_, migration_model.files)
    task_mapper = mapper(Task, migration_model.tasks_table)
    user_board_mapper = mapper(UserBoard, migration_model.users_boards)
    user_task_mapper = mapper(UserTask, migration_model.users_tasks)


def hashing_password(password, phone):
    hash_ = _sha3.sha3_256((str(password) + str(phone)).encode("utf-8")).hexdigest()
    return hash_


def get_object(obj, **kwargs):
    conditions = make_conditions(obj=obj, operator=Matches.eq, **kwargs)
    specification = SqlAlchemySpecification.getting_specification(conditions)
    with UoW(obj=obj) as uow:
        row = SqlAlchemyRepository.get(obj=obj, session=uow.session, specification=specification)
        if row:
            answer = row[obj.classname]
        else:
            answer = None

    return answer


# def compare_objects(obj1, obj2):
#     user =
#     if user.user_id:
#         find, code = get_object_info(user_id=user.user_id)
#     elif user.phone_number:
#         find, code = get_object_info(phone_number=user.phone_number)
#     else:
#         return False
#     found_user = User(**find)
#     if user == found_user:
#         return True
#     return False


def login_warden(**kwargs):
    if "phone_number" in kwargs and "password" in kwargs:
        kwargs["password"] = hashing_password(password=kwargs["password"], phone=kwargs["phone_number"])
        original_user = get_object(User, phone_number=kwargs["phone_number"])
        this_user = User(**kwargs)
        comparing = (original_user==this_user)
        if comparing:
            access_token = create_access_token(identity=kwargs["phone_number"])
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
                access_token = create_access_token(identity=kwargs["password"])
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

def create_object(obj, **kwargs):
    instance = obj(**kwargs)
    with UoW(obj=obj) as uow:
        specification = SqlAlchemySpecification.insertion_specification(**instance.dict())
        SqlAlchemyRepository.add(obj=obj, session=uow.session, specification=specification)
        uow.commit()




def unset_session():
    response = jsonify({
        "status": "ok"
    })
    unset_jwt_cookies(response)
    return response
