from flask_mysqldb import MySQL
import json
from flask import request
from functions import get_user_id
from cryptography.fernet import Fernet
import time
import pyotp
import qrcode
import io
import os
import base64

def generate_qr_code(mysql: MySQL) -> dict:
    response = {"hasError": False}

    responseJson = json.loads(request.data.decode())

    if "sessionToken" not in responseJson:
        response["hasError"] = True
        response["errorMessage"] = "Unexpected error"
        return response

    if 'key' not in responseJson or 'currPass' not in responseJson:
        response["hasError"] = True
        response["errorMessage"] = "No encryption key found"
        return response

    # entered password is hashed with 2 different salts on the frontend
    hashed_pw = responseJson["currPass"].strip() # normal login salt to verify accuracy
    encrypt_key = responseJson["key"].strip() # new salt to encrypt totp key

    # get the user id info
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
    
    # query the database to check if the password is valid
    user = None # make sure scope of user is outside the try block
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT username, password FROM users WHERE user_id=%s", (user_id,))
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
    
    # verify that the password matches
    if hashed_pw != user["password"]:
        response["hasError"] = True
        response["errorMessage"] = "Invalid password"
        del user['password']
        return response
    del user["password"]

    username = user["username"]

    # generate a totp key
    key = pyotp.random_base32()
    uri = pyotp.totp.TOTP(key).provisioning_uri(name=username, issuer_name='CodeCraft')

    if not uri:
        response['hasError'] = True
        response['errorMessage'] = 'Error generating key'
        response['logout'] = True
        return response

    # convert encrypt key from hex to bytes and encode in base 64 for fernet function
    encoded_encrypt_key = bytes.fromhex(encrypt_key)
    encoded_encrypt_key = base64.urlsafe_b64encode(encoded_encrypt_key).decode('utf-8')

    # encrypt the totp key
    f = Fernet(encoded_encrypt_key)
    token = f.encrypt(key.encode())

    # update temporary verification table
    try:
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM twofa_setup WHERE user_id = %s", (user_id,))
        cur.execute("INSERT INTO twofa_setup (user_id, fernet_key, totp_key) VALUES (%s, %s, %s)", (user_id, encrypt_key, token))
        mysql.connection.commit()
        cur.close()
    except Exception as e:
        response["hasError"] = True
        response["errorMessage"] = str(e)
        mysql.connection.rollback()
        cur.close()
        return response

    # generate and send the qr code to the frontend
    img = qrcode.make(uri)
    
    # encode the image
    buffer = io.BytesIO()
    img.save(buffer)
    img_bytes = buffer.getvalue()
    encoded_img = base64.b64encode(img_bytes).decode('utf-8')

    response["qr"] = encoded_img
    response["success"] = True
    return response

def validate_setup_totp(mysql: MySQL) -> dict:
    response = {"hasError": False}

    responseJson = json.loads(request.data.decode())

    if 'passcode' not in responseJson or 'sessionToken' not in responseJson:
        response["hasError"] = True
        response["errorMessage"] = "Unexpected error"
        return response

    passcode = responseJson['passcode'].strip()

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
    
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT totp_key, fernet_key FROM twofa_setup WHERE user_id = %s", (user_id,))
        user = cur.fetchone()
    except Exception as e:
        response["hasError"] = True
        response["errorMessage"] = str(e)
        cur.close()
        return response

    totp_key = user["totp_key"]
    fernet_key = user["fernet_key"]

    # convert decrypt key from hex to bytes and encode in base 64 for fernet function
    encoded_decrypt_key = bytes.fromhex(fernet_key)
    encoded_decrypt_key = base64.urlsafe_b64encode(encoded_decrypt_key).decode('utf-8')

    # decrypt the totp key with the fernet key
    f = Fernet(encoded_decrypt_key)
    decrypted_totp_key = f.decrypt(totp_key).decode('utf-8')

    # verify the code is correct
    totp = pyotp.TOTP(decrypted_totp_key)
    verified = totp.verify(passcode)

    if not verified:
        response["hasError"] = True
        response["errorMessage"] = "Failed TOTP verification"
        return response
    
    # move the code from the temporary database to the user database
    try:
        cur.execute("UPDATE users SET totp = %s WHERE user_id = %s", (totp_key,user_id))
        cur.execute("DELETE FROM twofa_setup WHERE user_id = %s", (user_id,))
        mysql.connection.commit()
        cur.close()
    except Exception as e:
        response["hasError"] = True
        response["errorMessage"] = str(e)
        mysql.connection.rollback()
        cur.close()
        return response

    response["success"] = True
    response["hasError"] = False
    return response

def validate_totp(mysql: MySQL) -> dict:
    response = {"hasError": False}

    responseJson = json.loads(request.data.decode())

    if 'passcode' not in responseJson or 'sessionToken' not in responseJson:
        response["hasError"] = True
        response["errorMessage"] = "Unexpected error"
        return response

    passcode = responseJson['passcode'].strip()

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

    # fetch the totp key from the database
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT totp FROM users WHERE user_id = %s", (user_id,))
        user = cur.fetchone()
    except Exception as e:
        cur.close()
        response["hasError"] = True
        response["errorMessage"] = str(e)
        return response

    if not user or not user["totp"]:
        response["hasError"] = True
        response["errorMessage"] = "Key not found"
        return response
    totp_key = user["totp"]

    # fetch the fernet key from the temporary table
    try:
        cur.execute("SELECT fernet_key FROM twofa_login WHERE user_id = %s", (user_id,))
        user = cur.fetchone()
    except Exception as e:
        response["hasError"] = True
        response["errorMessage"] = str(e)
        return response

    if not user["fernet_key"]:
        response["hasError"] = True
        response["errorMessage"] = "Key not found"
        return response

    fernet_key = user["fernet_key"]

    # convert decrypt key from hex to bytes and encode in base 64 for fernet function
    encoded_decrypt_key = bytes.fromhex(fernet_key)
    encoded_decrypt_key = base64.urlsafe_b64encode(encoded_decrypt_key).decode('utf-8')

    # decrypt the totp key using the fernet key
    f = Fernet(encoded_decrypt_key)
    decrypted_totp_key = f.decrypt(totp_key).decode('utf-8')

    # verify the code is correct
    totp = pyotp.TOTP(decrypted_totp_key)
    verified = totp.verify(passcode)

    if not verified:
        response["hasError"] = True
        response["errorMessage"] = "Failed TOTP verification"
        return response

    # delete the information on success
    try:
        cur.execute("DELETE FROM twofa_login WHERE user_id = %s", (user_id,))
        mysql.connection.commit()
        cur.close()
    except Exception as e:
        response["hasError"] = True
        response["errorMessage"] = str(e)
        mysql.connection.rollback()
        cur.close()
        return response
    
    response["success"] = True
    response["hasError"] = False
    return response