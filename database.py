import os

from sqlobject.col import StringCol, ForeignKey, BoolCol
from sqlobject.dbconnection import connectionForURI
from sqlobject.main import sqlhub, SQLObject

db_filename = os.path.abspath('data.db')
connection_string = 'sqlite:' + db_filename
connection = connectionForURI(connection_string)
sqlhub.processConnection = connection


class User(SQLObject):
    username = StringCol(unique=True, notNone=True)
    country_code = StringCol(notNone=True)

    @staticmethod
    def get_user(username):
        return User.selectBy(username=username.lower()).getOne(default=None)


class Stream(SQLObject):
    user = ForeignKey('User')
    title = StringCol(notNone=True)
    url = StringCol(notNone=True)
    ended = BoolCol(default=False)

User.createTable(ifNotExists=True)
Stream.createTable(ifNotExists=True)
