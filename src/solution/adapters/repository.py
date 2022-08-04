import abc

from sqlalchemy import insert, select, update, delete

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
        query = insert(obj).values(**specification).returning(obj)
        insertion = session.execute(query)
        result = insertion.first()
        return result

    @staticmethod
    def list(obj, session, specification):
        query = select(obj).where(specification)
        selection = session.execute(query)
        result = selection.fetchall()
        return result

    @staticmethod
    def update(obj, session, specification):
        where_ = specification["where"]
        values_ = specification["values"]
        query = update(obj).where(where_).values(**values_)
        session.execute(query)

    @staticmethod
    def delete(obj, session, specification):
        query = delete(obj).where(specification)
        deletion = session.execute(query)


class MinioRepository(AbstractRepository):
    @staticmethod
    def add(session, specification):
        try:
            response = session.put_object(**specification)
        except Exception as e:
            print(e)
    @staticmethod
    def get(session, specification):
        try:
            response = session.get_object(**specification)
           # response.data  # I need to do it i dont know why (else file data will be empty)
            return response.data
        finally:
            response.close()
            response.release_conn()

    @staticmethod
    def delete(session, specification):
        try:
            response = session.remove_object(**specification)
        except Exception as e:
            print(e)
