import abc
from src.solution.adapters.repository import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from src.solution.config import *
from src.solution.adapters.repository import *

DEFAULT_SESSION_FACTORY = sessionmaker(
    bind=create_engine(
        DataBaseConfig.get_database_uri(),
    )
)

class AbstractUnitOfWork(abc.ABC):
    products: AbstractRepository
    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self):
        self._commit()

    @abc.abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError

class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(self, session_factory=DEFAULT_SESSION_FACTORY, obj=None):
        self.session_factory = session_factory
        self.obj = obj

    def __enter__(self):
        self.session = self.session_factory()  # type: Session
        return super().__enter__()

    def __exit__(self, *args):
        self.session.close()

    def _commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()