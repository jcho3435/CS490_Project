def insert_new_user(connection, username, email, password) -> dict:
    cur = connection.cursor(dictionary=True)

    user = None
    try:
        cur.execute("INSERT INTO users(username, email, password) VALUES (%s, %s, %s)", (username, email, password))
        connection.commit()
        cur.execute("SELECT * FROM users where username=%s and password=%s", (username, password))
        user = cur.fetchone()
        if not user:
            raise Exception("Insertion failed.")
    except Exception as e:
        cur.close()
        raise e
    
    cur.close()
    return user

def delete_user(connection, user_id):
    cur = connection.cursor(dictionary=True)

    try:
        cur.execute("DELETE FROM users WHERE user_id=%s", (user_id,))
        connection.commit()
        cur.execute("SELECT * FROM users WHERE user_id=%s", (user_id,))
        user = cur.fetchone()
        if user:
            raise Exception("Deletion failed")
    except Exception as e:
        cur.close()
        raise e