from sqlalchemy import create_engine, Column, Integer, String, text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
import os


username = os.getenv("DB_USERNAME") 
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
database = os.getenv("DB_NAME")

# database_url = f"mysql+mysqldb://{username}:{password}@{host}/{database}" 

database_url = f"postgresql+psycopg2://{username}:{password}@{host}/{database}"



engine = create_engine(database_url)

# TEST THE CONNECTION

# with engine.connect() as connection:
#     result = connection.execute(text("SELECT version();"))
#     for row in result:
#         print(row)

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    userId = Column(String(60), primary_key=True, unique=True, nullable=False)
    firstname = Column(String(32), nullable=False)
    lastname = Column(String(32), nullable=False)
    email = Column(String(32), unique=True, nullable=False)
    password = Column(String(300), nullable=False)
    phone = Column(String(20), nullable=True)


class Organisation(Base):
    __tablename__ = "organisations"

    orgId = Column(String(60), primary_key=True,     nullable=False, unique=True)
    name = Column(String(32), nullable=False)
    description = Column(String(1024))
    

class UserOrganisation(Base):
    __tablename__ = "user_organisations"

    id = Column(Integer, primary_key=True, autoincrement=True)
    orgId = Column(String(60), ForeignKey('organisations.orgId'), nullable=False)
    userId = Column(String(60), ForeignKey("users.userId"), nullable=False)
