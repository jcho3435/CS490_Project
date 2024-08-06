from flask_mysqldb import MySQL
import json
from flask import request
from functions.validation import validate_username
from functions import get_user_id

def change_username(mysql: MySQL) -> dict:
    response = {"hasError": False}

    responseJson = json.loads(request.data.decode())
    
    if "sessionToken" not in responseJson or 'current' not in responseJson or 'new' not in responseJson:
        response["hasError"] = True
        response["errorMessage"] = "Unexpected error"
        return response
    
    current_user = responseJson["current"]
    new_user = responseJson["new"]

    user_id, error = get_user_id.get_user_id(mysql, responseJson['sessionToken'])
    if error:
        response['hasError'] = True
        response['errorMessage'] = error
        response['logout'] = True
        return response

    if user_id == -1:
        response['hasError'] = True
        response['errorMessage'] = "[LOGIN ERROR] User is not logged in!"
        response['logout'] = True
        return response

    valid, errors = validate_username(new_user)
    if not valid:
        response["hasError"] = True
        response["errorMessage"] = errors
        return response
    
    user = None #make sure scope of user is outside the try block
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT username FROM users WHERE username=%s", (new_user,))
        user = cur.fetchone()
    except Exception as e:
        cur.close()
        response["hasError"] = True
        response["errorMessage"] = str(e)
        return response

    if user:
        response["hasError"] = True
        response["errorMessage"] = "Username already in use. Choose a different username."
        return response
    
    try:
        cur.execute("SELECT username FROM users WHERE user_id=%s", (user_id,))
        user = cur.fetchone()
    except Exception as e:
        cur.close()
        response["hasError"] = True
        response["errorMessage"] = str(e)
        return response

    if not user:
        response["hasError"] = True
        response["errorMessage"] = "User not found (Make sure you're signed in)"
        return response

    if current_user == user['username']:
        try:
            cur.execute("UPDATE users SET username=%s WHERE user_id=%s", (new_user, user_id))
            mysql.connection.commit()
            cur.close()
            response["success"] = True
            return response
        except Exception as e:
            response["hasError"] = True
            response["errorMessage"] = str(e)
            mysql.connection.rollback()
            if cur:
                cur.close()
            return response
    
    else:
        response["hasError"] = True
        response["errorMessage"] = "Incorrect Username"

    return response

def change_password(mysql: MySQL) -> dict:
    response = {"hasError" : False}

    responseJson = json.loads(request.data.decode())

    if "sessionToken" not in responseJson or 'currPass' not in responseJson or 'newPass' not in responseJson:
        response["hasError"] = True
        response["errorMessage"] = "Unexpected error"
        return response
    
    currPass = responseJson["currPass"]
    newPass = responseJson["newPass"]
    user_id, error = get_user_id.get_user_id(mysql, responseJson['sessionToken'])
    if error:
        response['hasError'] = True
        response['errorMessage'] = error
        response['logout'] = True
        return response

    if user_id == -1:
        response['hasError'] = True
        response['errorMessage'] = "[LOGIN ERROR] User is not logged in!"
        response['logout'] = True
        return response
    
    # query the database to check if the user credentials are valid
    user = None #make sure scope of user is outside the try block
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT password FROM users WHERE user_id=%s", (user_id,))
        user = cur.fetchone()
    except Exception as e:
        cur.close()
        response["hasError"] = True
        response["errorMessage"] = str(e)
        return response

    if not user:
        response["hasError"] = True
        response["errorMessage"] = "User not found (Make sure you're signed in)"
        return response

    # make sure password matches
    if currPass == user['password']:
        try:
            cur.execute("UPDATE users SET password=%s WHERE user_id=%s", (newPass, user_id))
            mysql.connection.commit()
            cur.close()
            response["success"] = True
            return response
        except Exception as e:
            response["hasError"] = True
            response["errorMessage"] = str(e)
            mysql.connection.rollback()
            if cur:
                cur.close()
            return response
    
    else:
        response["hasError"] = True
        response["errorMessage"] = "Invalid password"
        del user['password']

    return response

def delete_user(mysql: MySQL) -> dict:
    response = {"hasError" : False}

    responseJson = json.loads(request.data.decode())

    if "sessionToken" not in responseJson:
        response["hasError"] = True
        response["errorMessage"] = "Unexpected error"
        return response
    
    user_id, error = get_user_id.get_user_id(mysql, responseJson['sessionToken'])
    if error:
        response['hasError'] = True
        response['errorMessage'] = error
        response['logout'] = True
        return response

    if user_id == -1:
        response['hasError'] = True
        response['errorMessage'] = "[LOGIN ERROR] User is not logged in!"
        response['logout'] = True
        return response
    
    # query the database to check if the user credentials are valid
    user = None #make sure scope of user is outside the try block
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT user_id FROM users WHERE user_id=%s", (user_id,))
        user = cur.fetchone()
    except Exception as e:
        cur.close()
        response["hasError"] = True
        response["errorMessage"] = str(e)
        return response

    if not user:
        response["hasError"] = True
        response["errorMessage"] = "User not found (Make sure you're signed in)"
        return response

    try:
        cur.execute("DELETE FROM users WHERE user_id=%s", (user_id,))
        mysql.connection.commit()
        cur.close()
        response["success"] = True
        return response
    except Exception as e:
        response["hasError"] = True
        response["errorMessage"] = str(e)
        mysql.connection.rollback()
        if cur:
            cur.close()
        return response