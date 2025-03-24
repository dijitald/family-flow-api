import os, uuid, logging
from datetime import datetime
from function_app_context import context
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship, mapped_column, Mapped
from sqlalchemy.dialects.mssql import (DATETIME2, FLOAT, INTEGER, NVARCHAR, UNIQUEIDENTIFIER, BIT)

class Base(DeclarativeBase):
    def to_dict(self, depth=2):
        result = {c.name: getattr(self, c.name) for c in self.__table__.columns}

        if depth > 0:
            for rel in self.__mapper__.relationships:
                related_obj = getattr(self, rel.key)
                if related_obj is not None:
                    if isinstance(related_obj, list):
                        result[rel.key] = [item.to_dict(depth - 1) for item in related_obj]
                    else:
                        result[rel.key] = related_obj.to_dict(depth - 1)
        return result
 
#     # def to_dict(self, visited=None):      #this one takes a while to complete but walks the entire stack. stops when it revisits a datatype and sets that value to null
#         # if visited is None:
#         #     visited = set()

#         # if self in visited:
#         #     return None

#         # visited.add(self)

#         # result = {}
#         # for c in self.__table__.columns:
#         #     value = getattr(self, c.name)
#         #     if isinstance(value, uuid.UUID):
#         #         result[c.name] = str(value)
#         #     else:
#         #         result[c.name] = value

#         # for rel in self.__mapper__.relationships:
#         #     related_obj = getattr(self, rel.key)
#         #     if related_obj is not None:
#         #         if isinstance(related_obj, list):
#         #             result[rel.key] = [item.to_dict(visited) for item in related_obj]
#         #         else:
#         #             result[rel.key] = related_obj.to_dict(visited)
#         # return result
    
#     # def to_dict(self):                #this one is the fastest, but only goes one level deep
#     # return {c.name: getattr(self, c.name) for c in self.__table__.columns}

#     # def to_dict(self):                #doesn't get child objects
#     #     if isinstance(self, list):
#     #         return [item.to_dict() for item in self]
#     #     elif isinstance(self, dict):
#     #         return {key: value.to_dict() for key, value in self.items()}
#     #     elif hasattr(self, '__dict__'):
#     #         data = {}
#     #         for key, value in self.__dict__.items():
#     #             if key.startswith('_'):
#     #                 continue
#     #             if isinstance(value, list):
#     #                 data[key] = [item.to_dict() for item in value]
#     #             else:
#     #                 data[key] = value.to_dict() if hasattr(value, 'to_dict') else value
#     #         return data
#     #     else:
#     #         return self
#     # def serialize(self):
#     #     return json.dumps(self.to_dict(), default=str)


class Household(Base):
    __tablename__ = 'households'
    id: Mapped[uuid.UUID] = mapped_column(UNIQUEIDENTIFIER, primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(NVARCHAR, nullable=False)
    createdOn: Mapped[datetime] = mapped_column(DATETIME2, default=datetime.now)
    users: Mapped[list["HouseholdMembership"]] = relationship("HouseholdMembership", back_populates="household")
    tasks: Mapped[list["Task"]] = relationship("Task", back_populates="household")
    activities: Mapped[list["Activity"]] = relationship("Activity", back_populates="household")

class User(Base):
    __tablename__ = 'users'
    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, autoincrement=True)
    guid: Mapped[str] = mapped_column(NVARCHAR, nullable=False)  # liveid uuid.tenantid
    email: Mapped[str] = mapped_column(NVARCHAR, nullable=False)
    sms: Mapped[str] = mapped_column(NVARCHAR, nullable=True)
    name: Mapped[str] = mapped_column(NVARCHAR, nullable=False, default='New User')
    createdOn: Mapped[datetime] = mapped_column(DATETIME2, default=datetime.now)
    lastLogon: Mapped[datetime] = mapped_column(DATETIME2, nullable=True)
    avatarPath: Mapped[str] = mapped_column(NVARCHAR, nullable=True)
    householdid: Mapped[uuid.UUID] = mapped_column(UNIQUEIDENTIFIER, ForeignKey('households.id'), nullable=True)
    households: Mapped[list["HouseholdMembership"]] = relationship("HouseholdMembership", back_populates="user")
    activities: Mapped[list["Activity"]] = relationship("Activity", back_populates="user")

class HouseholdMembership(Base):
    __tablename__ = 'memberships'
    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, autoincrement=True)
    household: Mapped[Household] = relationship("Household", back_populates="users")
    householdid: Mapped[uuid.UUID] = mapped_column(UNIQUEIDENTIFIER, ForeignKey('households.id'))
    user: Mapped[User] = relationship("User", back_populates="households")
    userid: Mapped[int] = mapped_column(INTEGER, ForeignKey('users.id'))
    role: Mapped[str] = mapped_column(NVARCHAR, default='member')
    balance: Mapped[float] = mapped_column(FLOAT, default=0)
    createdOn: Mapped[datetime] = mapped_column(DATETIME2, default=datetime.now)

class Task(Base):
    __tablename__ = 'tasks'
    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, autoincrement=True)
    household: Mapped[Household] = relationship("Household", back_populates="tasks")
    householdid: Mapped[uuid.UUID] = mapped_column(UNIQUEIDENTIFIER, ForeignKey('households.id'))
    name: Mapped[str] = mapped_column(NVARCHAR, nullable=False)
    description: Mapped[str] = mapped_column(NVARCHAR, nullable=True)
    active: Mapped[bool] = mapped_column(BIT, default=True)
    rewardAmount: Mapped[float] = mapped_column(FLOAT, default=0)
    lastCompleted: Mapped[datetime] = mapped_column(DATETIME2, nullable=True)
    nextDueDate: Mapped[datetime] = mapped_column(DATETIME2, nullable=True)
    createdOn: Mapped[datetime] = mapped_column(DATETIME2, default=datetime.now)
    createdBy: Mapped[str] = mapped_column(NVARCHAR, nullable=False)
    frequency: Mapped[str] = mapped_column(NVARCHAR, nullable=True)
    everyWeekday: Mapped[bool] = mapped_column(BIT, default=False)
    interval: Mapped[int] = mapped_column(INTEGER, default=0)
    dayOfWeek: Mapped[int] = mapped_column(INTEGER, default=0)
    dayOfMonth: Mapped[int] = mapped_column(INTEGER, default=0)
    instance: Mapped[int] = mapped_column(INTEGER, default=0)
    isInstanceBasedMonthly: Mapped[bool] = mapped_column(BIT, default=False)
    monthOfYear: Mapped[int] = mapped_column(INTEGER, default=0)
    isInstanceBasedYearly: Mapped[bool] = mapped_column(BIT, default=False)

class Activity(Base):
    __tablename__ = 'activities'
    id: Mapped[int] = mapped_column(INTEGER, primary_key=True, autoincrement=True)
    household: Mapped[Household] = relationship("Household", back_populates="activities")
    householdid: Mapped[uuid.UUID] = mapped_column(UNIQUEIDENTIFIER, ForeignKey('households.id'))
    date: Mapped[datetime] = mapped_column(DATETIME2, default=datetime.now)
    user: Mapped[User] = relationship("User", back_populates="activities")
    userId: Mapped[int] = mapped_column(INTEGER, ForeignKey('users.id'))
    userName: Mapped[str] = mapped_column(NVARCHAR)
    amount: Mapped[float] = mapped_column(FLOAT, default=0)
    isCredit: Mapped[bool] = mapped_column(BIT)  # true = credit, false = debit
    description: Mapped[str] = mapped_column(NVARCHAR)
    tags: Mapped[str] = mapped_column(NVARCHAR, nullable=True)
    
try :
    # Set up SQLAlchemy
    #DATABASE_URL = "mssql+pyodbc://username:password@server:1433/database?driver=ODBC+Driver+18+for+SQL+Server"
    DATABASE_URL = os.getenv("DATABASE_CONNECTIONSTRING")
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)

except Exception as e:
    logging.critical(f"Error creating database tables: {e}")
    raise
finally:
    engine.dispose()
    