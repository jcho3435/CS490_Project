from flask_mysqldb import MySQL
import json
from flask import request
from functions.validation import validate_username, validate_email
import uuid

def register(mysql: MySQL) -> dict:
    response = {"hasError" : False}
    response["sqlErrors"] = []

    responseJson = json.loads(request.data.decode())

    if 'username' not in responseJson or 'email' not in responseJson or 'password' not in responseJson:
        response["hasError"] = True
        response["errorMessage"] = "Unexpected error"
        return response

    username = responseJson['username'].strip()
    email = responseJson['email'].strip()
    # all password checks should be on frontend
    encrypted_pw = responseJson["password"]

    # username validation
    validUser, errors = validate_username(username)
    if not validUser:
        response["hasError"] = True
        response["usernameErrors"] = errors

    # email validation
    validEmail, errors = validate_email(email)
    if not validEmail:
        response["hasError"] = True
        response["emailErrors"] = errors

    if response["hasError"]:
        return response
    
    try:
        # query db to make sure email and username are unique
        cur = mysql.connection.cursor()
        cur.execute("SELECT username, email FROM users WHERE username = %s OR email = %s", (username, email))
        existing_user = cur.fetchone()

        if existing_user:
            response["hasError"] = True
            response["sqlErrors"] = []
            if existing_user["username"] == username:
                response["sqlErrors"].append("Chosen username already in use")
            if existing_user["email"] == email:
                response["sqlErrors"].append("Chosen email already in use")
            return response
    except Exception as e:
        response["hasError"] = True
        response["sqlErrors"].append(str(e))
        cur.close()
        return response

    try:
        # insert new user into db
        cur.execute("INSERT INTO users (username, email, password) VALUES (%s, %s, %s)", (username, email, encrypted_pw))
        mysql.connection.commit()
    except Exception as e:
        mysql.connection.rollback()
        response["hasError"] = True
        response["sqlErrors"].append(str(e))
        cur.close()
        return response

    # get user id
    user_id = ""
    try:
        cur.execute("SELECT user_id FROM users WHERE username=%s", (username,))
        user = cur.fetchone()
        if not user:
            raise Exception("Username was not properly inserted into the database.") #Better hope we never hit this
        user_id = user["user_id"]
    except Exception as e:
        cur.close()
        response["hasError"] = True
        response["sqlErrors"].append(str(e))
        return response

    # insert user id into new table, also generate a uuid
    id = str(uuid.uuid4())

    try:
        cur.execute("INSERT INTO logged_in(user_id, session_token) VALUES(%s, %s)", (user_id, id))
        mysql.connection.commit()
    except:
        mysql.connection.rollback()
        cur.close()
        response["hasError"] = True
        response["sqlErrors"].append(str(e))
        return response

    cur.close()
    
    response["success"] = True
    response["sessionToken"] = id
    return response