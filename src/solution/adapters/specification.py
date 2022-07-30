import abc
from src.solution.domain.model import *
from models.model import *
from src.solution.service_layer.services import *
from sqlalchemy.sql.elements import and_, or_, not_


class AbstractSpecification(abc.ABC):
    pass


class SqlAlchemySpecification(AbstractSpecification):
    @staticmethod
    def getting_specification(conditions):
        return and_(*conditions)

    @staticmethod
    def insertion_specification(**kwargs):
        return kwargs
