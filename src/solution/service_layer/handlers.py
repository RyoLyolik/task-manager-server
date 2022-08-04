from src.solution.adapters.specification import *
from src.solution.service_layer.unit_of_work import SqlAlchemyUnitOfWork as UoW
from src.solution.domain.model import *
from src.solution.adapters.repository import *
from sqlalchemy.orm import mapper
from models import model as migration_model
import _sha3

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


def make_conditions(obj, operator, **kwargs):
    condition_list = list()
    instance = obj()
    for attr in kwargs:
        if attr in instance.__dict__:
            condition_list.append(getattr(getattr(obj, attr), operator)(kwargs[attr]))
    return condition_list


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
