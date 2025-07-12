#!/usr/bin/python3
""" new class for sqlAlchemy """
from os import getenv
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import (create_engine)
from backend.models.base_model import Base
from backend.models.suburb import Suburb
from backend.models.bus_stop import BusStop


class DBStorage:
    """ create tables in environmental"""
    __engine = None
    __session = None

    def __init__(self):
        user = getenv("UMPIRE_DB_USER")
        passwd = getenv("UMPIRE_DB_PWD")
        db = getenv("UMPIRE_DB")
        host = getenv("UMPIRE_DB_HOST")
        env = getenv("UMPIRE_ENV")
        # initializes the db storage
        self.__engine = create_engine('postgresql+psycopg2://{}:{}@{}/{}'
                                       .format(user, passwd, host, db),
                                       pool_pre_ping=True)
        if env == "test":
            Base.metadata.drop_all(self.__engine)

    def all(self, cls=None):
        """returns a dictionary
        Return:
            returns a dictionary of __object
        """
        session = self.__session
        dic = {}
        if not cls:
            tables = [Suburb, BusStop]
        else:
            if type(cls) == str:
                cls = eval(cls)
            tables = [cls]

        for tab in tables:
            query = session.query(tab).all()

            for rows in query:
                key = "{}.{}".format(type(rows).__name__, rows.id)
                dic[key] = rows

        return (dic)

    def new(self, obj):
        """add a new element in the table
        """
        if obj:
            self.__session.add(obj)

    def save(self):
        """save changes
        """
        self.__session.commit()

    def delete(self, obj=None):
        """delete an element in the table
        """
        if obj:
            self.session.delete(obj)

    def reload(self):
        """configuration
        """
        Base.metadata.create_all(self.__engine)
        sec = sessionmaker(bind=self.__engine, expire_on_commit=False)
        Session = scoped_session(sec)
        self.__session = Session()

    def close(self):
        """ calls remove()
        """
        self.__session.close()