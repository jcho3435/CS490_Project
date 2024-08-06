from flask_mysqldb import MySQL
import json
from flask import request 
from functions import get_user_id
from functions.cache import translation_cache, translation_cache_lock

def delete_translations(mysql: MySQL):
    response = {"hasError": False}

    responseJson = json.loads(request.data.decode())

    if 'ids' not in responseJson:
        response['hasError'] = True
        response['errorMessage'] = "Unexpected Error"
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
    
    ids = responseJson["ids"]

    if type(ids) != str and type(ids) != list:
        response["hasError"] = True
        response["errorMessage"] = "Frontend error: Passed data should be a list of ints."
        return response
    
    if type(ids) == list:
        for e in ids:
            if type(e) != int:
                response["hasError"] = True
                response["errorMessage"] = "Frontend error: Passed data should be a list of ints."
                return response
                
    try:
        cur = mysql.connection.cursor()
        if ids == "all":
            cur.execute("DELETE FROM translation_history WHERE user_id=%s", (user_id,))
            with translation_cache_lock:
                if user_id in translation_cache:
                    translation_cache[user_id].history = None
        elif type(ids) == list:
            deletion = "DELETE FROM translation_history WHERE user_id=%s AND ("
            for i in range(len(ids)):
                deletion += "translation_id=%s OR "
            deletion = deletion.strip(" OR ")
            deletion += ")"
            cur.execute(deletion, (user_id, *ids))
            with translation_cache_lock:
                if user_id in translation_cache:
                    del translation_cache[user_id]
        else:
            response["hasError"] = True
            response["errorMessage"] = "Frontend error: Passed data is invalid."
            return response

        mysql.connection.commit()
        cur.close()

    except Exception as e:
        mysql.connection.rollback()
        response["hasError"] = True
        response["errorMessage"] = str(e)
        if cur:
            cur.close()
        return response

    response["success"] = True
    return response
