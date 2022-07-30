import abc

import sqlalchemy
from sqlalchemy import insert, select, update, delete
from sqlalchemy.sql.elements import *
from models import model as migration_model
from src.solution.adapters.specification import *
from src.solution.domain.model import *
from src.solution.service_layer.services import *



class AbstractRepository(abc.ABC):
    @staticmethod
    @abc.abstractmethod
    def get(**kwargs):
        raise NotImplementedError

    @staticmethod
    @abc.abstractmethod
    def add(**kwargs):
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    @staticmethod
    def get(obj, session, specification):
        query = select(obj).where(specification)
        selection = session.execute(query)
        result = selection.first()
        return result

    @staticmethod
    def add(obj, session, specification):
        query = insert(obj).values(**specification)
        insertion = session.execute(query)

