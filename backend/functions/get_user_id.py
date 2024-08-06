from flask_mysqldb import MySQL
import datetime
from functions.cache import id_cache, User, id_cache_lock

def get_user_id(mysql: MySQL, token: str) -> int:
    error = ""

    with id_cache_lock:
        if token in id_cache:
            user = id_cache[token]
            if datetime.datetime.now() < user.expiry:
                return user.id, error
            else:
                id_cache.pop(token)

    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT user_id, login_date from logged_in WHERE session_token = %s", (token,))
    except Exception as e:
        cur.close
        error = str(e)

    user = cur.fetchone()
    
    cur.close()
    if user:
        with id_cache_lock:
            id_cache[token] = User(token, user["user_id"], user["login_date"])
        return user['user_id'], error
    else:
        return -1, error