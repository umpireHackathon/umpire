#!/usr/bin/python3
""" new class for sqlAlchemy """

import os
from backend.models.base_model import BaseModel, Base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy import (create_engine)
from backend.models import (
    Suburb,
    BusStop,
    Agency,
    User,
    Route,
    MLModel,
    Terminal,
    Vehicle,
    VehicleTrip
)
from dotenv import load_dotenv

load_dotenv()

classes = [
    Suburb, BusStop, Agency, User, Route,
    MLModel, Terminal, Vehicle, VehicleTrip
]

class DBStorage:
    """ create tables in environmental"""
    __engine = None
    __session = None

    def __init__(self):
        user = os.getenv("UMPIRE_DB_USER")
        passwd = os.getenv("UMPIRE_DB_PWD")
        db = os.getenv("UMPIRE_DB")
        host = os.getenv("UMPIRE_DB_HOST")
        env = os.getenv("UMPIRE_ENV")
        print("============DBStorage initialized ================")
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
            tables = classes
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

    def new_all(self, *args):
        """ This method adds all instances to the session """
        for obj in args:
            self.__session.add(obj)

    def save(self):
        """save changes
        """
        self.__session.commit()

    def delete(self, obj=None):
        """delete an element in the table
        """
        if obj:
            self.__session.delete(obj)

    def delete_all(self):
        """ This method deletes all instances from the session """
        for c in classes:
            self.__session.query(c).delete()
        self.save()
        
    def reload(self):
        """configuration
        """
        Base.metadata.create_all(self.__engine)
        sec = sessionmaker(bind=self.__engine, expire_on_commit=False)
        Session = scoped_session(sec)
        self.__session = Session()

    def get(self, cls, id):
        """ This method retrieves an instance from the session
        Args:
            cls (str): The class name
            id (str): The instance id
        Returns: The instance or None
        """
        if id is None or cls is None:
            return None
        objs = self.all(cls)
        return objs.get('{}.{}'.format(cls, id))
    
    def get_by(self, cls, **kwargs):
        """ This method returns a list of instances of a class that match the keyword arguments """
        if cls:
            return self.__session.query(cls).filter_by(**kwargs).all()
        return None
    
    def get_many_by(self, cls, **kwargs):
        """ This method returns a list of instances of a class that match the keyword arguments """
        if cls:
            return self.__session.query(cls).filter_by(**kwargs).all()
        return []

    def get_one_by(self, cls, **kwargs):
        """ This method returns the first instance of a class that matches the keyword arguments """
        if cls:
            return self.__session.query(cls).filter_by(**kwargs).first()
        return None

    def get_or_create(self, cls, **kwargs):
        """ This method returns the first instance of a class that matches the keyword arguments
        or creates a new instance if one does not exist """
        instance = self.get_one_by(cls, **kwargs)
        if instance is None:
            instance = cls(**kwargs)
            self.new(instance)
            self.save()
        return instance
    
    def close(self):
        """ calls remove()
        """
        self.__session.close()