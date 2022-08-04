import abc
from sqlalchemy.sql.elements import and_, or_, not_
from src.solution.config import MinioConfig

class AbstractSpecification(abc.ABC):
    pass


class SqlAlchemySpecification(AbstractSpecification):
    @staticmethod
    def and_specification(conditions):
        return and_(*conditions)
    @staticmethod
    def or_specification(conditions):
        return or_(*conditions)

    @staticmethod
    def not_specification(conditions):
        return not_(*conditions)

    @staticmethod
    def values_specification(**kwargs):
        return kwargs

class MinioSpecification(AbstractSpecification):
    @staticmethod
    def fix_kwargs(**kwargs):
        kwargs["bucket_name"] = MinioConfig.main_bucket
        return kwargs