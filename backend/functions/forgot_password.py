from flask_mysqldb import MySQL
import json
from flask import request
from functions.validation import validate_username, validate_email
import uuid
import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv

load_dotenv()

def send_email(mysql: MySQL) -> dict:
    response = {"hasError": False}

    responseJson = json.loads(request.data.decode())

    if 'email' not in responseJson:
        response["hasError"] = True
        response["errorMessage"] = "Unexpected error"
        return response

    # accepts username or email for reset
    username_or_email = responseJson['email'].strip()
    # username/email validation
    is_username = False
    is_email = False
    validUser, _ = validate_username(username_or_email)
    if validUser:
        is_username = True
    else:
        validEmail, _ = validate_email(username_or_email)
        if validEmail:
            is_email = True
    
    if not is_username and not is_email:
        response["hasError"] = True
        response["errorMessage"] = "Invalid format for username or email"
        return response

    # check if the user exists
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT user_id, email, username FROM users WHERE username = %s OR email = %s", (username_or_email, username_or_email))
        user = cur.fetchone()
    except Exception as e:
        cur.close()
        response["hasError"] = True
        response["errorMessage"] = str(e)
        return response
    
    if not user:
        response["hasError"] = True
        response["errorMessage"] = "User not found"
        return response

    # generate uuid and store in db per user
    id = str(uuid.uuid4())
    try:
        cur.execute("DELETE FROM password_reset WHERE user_id=%s", (user["user_id"],))
        cur.execute("INSERT INTO password_reset(user_id, email_token) VALUES(%s, %s)", (user["user_id"], id))
        mysql.connection.commit()
    except Exception as e:
        mysql.connection.rollback()
        cur.close()
        response["hasError"] = True
        response["errorMessage"] = str(e)
        return response

    # send email with link using uuid
    username = user["username"]
    sender = 'codecraft.user.services@gmail.com'
    receiver = user["email"]
    # TODO: update link during deployment
    link = f"http://localhost:3000/resetpassword?token={id}"
    html_content = f"""\
    <html>
    <head></head>
    <body>
        <p>Hello {username},</p>
        <p>Click the following link to reset your password:<br>
        <a href="{link}">Reset Password</a>
        </p>
        <p>If you did not request to change your password, ignore this email.</p>
    </body>
    </html>
    """

    message = EmailMessage()
    message.set_content(html_content, subtype='html')
    message['Subject'] = "CodeCraft Password Reset"
    message['From'] = sender
    message['To'] = receiver

    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as smtpObj:
            smtpObj.starttls()
            smtpObj.login(sender, os.getenv('EMAIL_PASSWORD'))
            smtpObj.send_message(message)
    except:
        response["hasError"] = True
        response["errorMessage"] = "Failed to send email."
        return response

    response["success"] = True
    return response

def reset_password(mysql: MySQL) -> dict:
    response = {"hasError" : False}

    responseJson = json.loads(request.data.decode())

    if 'newPass' not in responseJson:
        response["hasError"] = True
        response["errorMessage"] = "No password submitted"
        return response

    if 'emailToken' not in responseJson:
        response["hasError"] = True
        response["errorMessage"] = "No email token found"
        return response
    
    new_pass = responseJson["newPass"]
    email_token = responseJson["emailToken"]

    # validate email token and grab user id
    user = None
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT user_id FROM password_reset WHERE email_token = %s", (email_token,))
        user = cur.fetchone()
    except Exception as e:
        cur.close()
        response["hasError"] = True
        response["errorMessage"] = str(e)
        return response
    
    if not user:
        response["hasError"] = True
        response["errorMessage"] = "Invalid email token"
        return response
    user_id = user["user_id"]

    # Update the password
    try:
        cur.execute("UPDATE users SET password = %s WHERE user_id = %s", (new_pass, user_id))
        cur.execute("DELETE FROM password_reset WHERE user_id = %s", (user_id,))
        mysql.connection.commit()
        cur.close()
    except Exception as e:
        response["hasError"] = True
        response["errorMessage"] = str(e)
        mysql.connection.rollback()
        if cur:
            cur.close()
        return response
    
    response["success"] = True
    return response