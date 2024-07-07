from flask import Flask
import os
from .model import Base, engine
from flask_jwt_extended import JWTManager
from sqlalchemy.orm import sessionmaker

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")
jwt = JWTManager(app)

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)
session = Session()