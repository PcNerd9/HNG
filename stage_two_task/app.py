from flask import Flask, jsonify, request
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
import uuid
from werkzeug.security import generate_password_hash, check_password_hash
from .model import Base, User, Organisation, UserOrganisation, engine
import os
from . import app, session



salt_lenght = int(os.getenv("SALT_LENGTH"))
hash_method = os.getenv("HASH_METHOD") 



@app.route("/auth/register", methods=["POST"])
def register():
    """
    create a new user and add it to the database
    """
    firstname = request.json.get("firstName", None)
    lastname = request.json.get("lastName", None)
    email = request.json.get("email", None)
    password = request.json.get("password", None)
    phone = request.json.get("phone", None)

    error_response = {
            "status": "Bad request",
            "message": "Registration unsuccessful",
            "statusCode": 400
        }

    if firstname is None or lastname is None or email is None or password is None:
        return jsonify(error_response), 400
    
    hashed_password = generate_password_hash(password, method=hash_method, salt_length=salt_lenght)
    userid = str(uuid.uuid4())
    try:
        new_user = User(userId=userid, firstname=firstname, lastname=lastname, email=email, password=hashed_password, phone=phone)
    except Exception as e:
        return jsonify(error_response), 400

    organisation_name = f"{firstname}'s Oganisation"
    orgId = str(uuid.uuid4())
    user_default_organisation = Organisation(orgId=orgId, name=organisation_name, description=None)
    user_organisation = UserOrganisation(orgId=orgId, userId=userid)

    try:
        session.add(new_user)
        session.add(user_default_organisation)
        session.add(user_organisation)
        session.commit()
    except IntegrityError as e:
        session.rollback()
        return jsonify(error_response), 422

    access_token = create_access_token(identity=userid)

    response = {"status" : "success",
                "message": "Registration successful",
                "data": {
                    "accessToken" : access_token,
                    "user": {
                        "userId": userid,
                        "firstName": firstname,
                        "lastName": lastname,
                        "email": email,
                        "phone": phone,
                    }
                }
            }
    return jsonify(response), 201

@app.route("/auth/login", methods=["POST"])
def login():
    """
    authenticate user
    """
    error_response = {
        "status": "Bad request",
        "message" : "Authentication failed",
        "statusCode" : 401
    }
    email = request.json.get('email', None)
    password = request.json.get('password', None)
    if email is None or password is None:
        return jsonify(error_response), 401
    
   
    user = session.query(User).filter_by(email=email).first()
    if user is None:
        return jsonify(error_response), 401
    if not check_password_hash(user.password, password):
        error_response["what"] = True
        return jsonify(error_response), 401
    
    access_token = create_access_token(identity=user.userId)
    response = {"status" : "success",
                "message": "Registration successful",
                "data": {
                    "accessToken" : access_token,
                    "user": {
                        "userId": user.userId,
                        "firstName": user.firstname,
                        "lastName": user.lastname,
                        "email": user.email,
                        "phone": user.phone,
                    }
                }
            }
    return jsonify(response), 200


@app.route("/api/users/<id>", methods=["GET"])
@jwt_required()
def get_user(id):
    """
    get a particular user with the provided
    user id
    """
    error_response =  {
        "status": "Bad request",
        "message" : "Authentication failed",
        "statusCode" : 401
    }
    current_user_id = get_jwt_identity()

    user = session.query(User).filter_by(userId = current_user_id).first()

    current_user_organisaton = session.query(UserOrganisation).filter_by(userId=current_user_id).all()
    listof_current_user_oganid = []

    for user_organ in current_user_organisaton:
        listof_current_user_oganid.append(user_organ.orgId)
    

    requested_user = session.query(User).filter_by(userId=id).first()
    if requested_user is None:
        return jsonify(error_response)
    
    requested_user_organisation = session.query(UserOrganisation).filter_by(userId=requested_user.userId).all()
    listof_requested_user_organid =[]

    for user_organ in requested_user_organisation:
        listof_requested_user_organid.append(user_organ.orgId)

    is_present = False
    for orgId in listof_requested_user_organid:
        if orgId in listof_current_user_oganid:
            is_present  = True
    
    if is_present is True:
        response = {
            "status" : "success", 
            "message": "Retrieval successful",
            "data" : {
                "userId": requested_user.userId,
                "firstName": requested_user.firstname,
                "lastName": requested_user.lastname,
                "email": requested_user.email,
                "phone": requested_user.phone
            }
        }
        return jsonify(response)
    else:
        return jsonify(error_response)
    

@app.route("/api/organisations", methods=["GET"])
@jwt_required()
def get_all_organisations():
    """
    return all organisations that a user belong
    """
    userId = get_jwt_identity()

    user_organisation = session.query(UserOrganisation).filter_by(userId=userId).all()
    data = []
    for user_organ in user_organisation:
        organ = session.query(Organisation).filter_by(orgId=user_organ.orgId).first()
        organ_dict = {
            "orgId": organ.orgId,
            "name": organ.name,
            "description": organ.description
        }
        data.append(organ_dict)

    response = {
        "status": "success",
        "message" : "Retrieval successful",
        "data": {
            "organisations": data
        }
    }
    return jsonify(response)

@app.route("/api/organisations/<orgId>", methods=["GET"])
@jwt_required()
def get_organisation(orgId):
    """
    return a json of an organisation details
    """

    userId = get_jwt_identity()
    user = session.query(User).filter_by(userId=userId).first()

    user_organisations = session.query(UserOrganisation).filter_by(userId=userId).all()

    orgIds = []
    for organ in user_organisations:
        orgIds.append(organ.orgId)
    if orgId in orgIds:
        organisation = session.query(Organisation).filter_by(orgId=orgId).first()
        return jsonify({
            "status": "success",
            "message": "Retrieval successful",
            "data": {
                "orgId": orgId,
                "name": organisation.name,
                "description": organisation.description
            }
        })
    else:
        return jsonify({
        "status": "Bad request",
        "message" : "Authentication failed",
        "statusCode" : 401
        })
    

@app.route("/api/organisations", methods=["POST"])
@jwt_required()
def add_organisation():
    """
    add a new organisation to the database
    """
    userId = get_jwt_identity()
    
    name = request.json.get("name", None)
    description = request.json.get("organisation", None)
    error_response = {
        "status": "Bad Request",
        "message": "Client error",
        "statusCode": 400
    }
    if name is None:
        return jsonify(error_response)
    orgId = str(uuid.uuid4())
    organisation = Organisation(orgId=orgId, name=name, description=description)
    user_org = UserOrganisation(userId=userId, orgId=orgId)

    try:
        session.add(organisation)
        session.add(user_org)
        session.commit()
    except IntegrityError as e:
        error_response["message"] = e.statement
        return jsonify(error_response)
    
    response = {
        "status": "success",
        "message": "Organisation created successfully",
        "data": {
            "orgId": organisation.orgId,
            "name": organisation.name,
            "description": organisation.description
        }
    }
    return jsonify(response)

    
@app.route("/api/organisations/<orgId>/users", methods=["POST"])
@jwt_required()
def add_user_to_organisation(orgId):
    """
    add a user to an organisation
    """
    userId = get_jwt_identity()

    error_response = {
        "status": "Bad Request",
        "message": "Client error",
        "statusCode": 400
    }

    new_userId = request.json.get("userId",None)
    if userId is None:
        return jsonify(error_response)
    
    new_user = session.query(User).filter_by(userId=new_userId).first()
    if new_user is None:
        error_response["message"] = "Invalid User Id"
        return jsonify(error_response), 400
    
    organisation = session.query(Organisation).filter_by(orgId=orgId).first()
    if organisation is None:
        error_response["message"] = "Invalid Organisation Id"
        return jsonify(error_response),400
    
    user_organs = session.query(UserOrganisation).filter_by(userId=userId).all()
    listof_organ = []

    for user_organ in user_organs:
        listof_organ.append(user_organ.orgId)

    if organisation.orgId not in listof_organ:
        return jsonify(error_response)
    
    user_organisation = UserOrganisation(userId=new_userId, orgId=organisation.orgId)

    try:
        session.add(user_organisation)
        session.commit()
    except IntegrityError as e:
        session.rollback()
        error_response["message"] = e.statement
        return jsonify(error_response), 422
    
    response = {
        "status": "success",
        "message": "User added to organisation successfully"
    }
    return jsonify(response)




if __name__ == "__main__":
    app.run(debug=True)
