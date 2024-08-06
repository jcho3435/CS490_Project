import pytest
from app import create_app
import os
from dotenv import load_dotenv
import mysql.connector
from Tests.setup_and_teardown import setup_module, teardown_module
import uuid
import time
import json
import datetime
from Tests import helpers

# *************************** TEST INFORMATION *************************** #
# THESE TESTS TEST ONLY THE SQL CALLS USED IN OTHER FUNCTIONS. THE TABLE   #
# IS PRE-FILLED WITH SOME TESTING VALUES. LOOK IN TESTS/SETUP_AND_TEARDOWN #
# IF YOU WISH TO SEE THE EXACT VALUES THAT ARE BEING PLACED IN THE TABLE   #
# ------------------------------------------------------------------------ #
# IF ANY SQL QUERIES ARE CHANGED IN ANY EXISTING FUNCTIONS, IT IS CRUCIAL  #
# THAT THEIR CORRESPONDING TESTING QUERIES ARE CHANGED IN THIS TESTING     #
# FILE IN ORDER TO ENSURE THAT THE QUERIES BEING TESTED ARE ACCURATE       #
# *************************** TEST INFORMATION *************************** #

class TestSql:
    @classmethod
    def setup_class(TestSql):
        load_dotenv()

        mysql_config = {
            'host': os.getenv('DB_URL'),
            'user': os.getenv('MYSQL_USER'),
            'password': os.getenv('MYSQL_PASSWORD'),
            'database': 'codecraft_testing'
        }

        global connection
        connection = mysql.connector.connect(**mysql_config)

    @classmethod
    def teardown_class(TestSql):
        global connection
        connection.close()
        
    @pytest.fixture()
    def app(self):
        app = create_app(True)
        app.config.update({
            "TESTING": True,
        })

        yield app

    @pytest.fixture()
    def client(self, app):
        return app.test_client()


    @pytest.fixture()
    def runner(self, app):
        return app.test_cli_runner()
    
    @pytest.mark.parametrize("username,email,password,expectExisting", [("username1", "email@email.com", "password", True), ("unique", "email@email.com", "password", False)])
    def test_registration_sql_and_delete_user(self, username, email, password, expectExisting):
        cur = connection.cursor(dictionary=True)

        try:
            cur.execute("SELECT username, email FROM users WHERE username = %s OR email = %s", (username, email)) # Exact query used in register_user.py
            existing_user = cur.fetchone()
            if expectExisting:
                assert existing_user
            else:
                assert not existing_user
        except Exception as e:
            cur.close()
            assert str(e) and False
        
        if not expectExisting:
            try:
                cur.execute("INSERT INTO users(username, email, password) VALUES (%s, %s, %s)", (username, email, password))
                connection.commit()
            except Exception as e:
                cur.close()
                assert str(e) and False

            try:
                cur.execute("SELECT * FROM users WHERE user_id = %s AND username = %s AND email = %s AND password = %s", (4, username, email, password))
                user = cur.fetchone()
                assert user
            except Exception as e:
                cur.close()
                assert str(e) and False

            # Test teardown- delete inserted value to prevent unexpected behavior in future tests - also delete user
            try:
                cur.execute("INSERT INTO logged_in(user_id, session_token) VALUES(%s, %s)", (4, str(uuid.uuid4())))
                cur.execute("DELETE FROM users WHERE user_id = %s", (4,))
                connection.commit()
                cur.execute("SELECT * FROM logged_in")
                user = cur.fetchone()
                assert not user

                cur.execute("SELECT * FROM users")
                user = cur.fetchall()
                assert user and len(user) == 3
            except Exception as e:
                cur.close()
                assert str(e) and False

        cur.close()

    @pytest.mark.parametrize("username,password,expectExisting", [("username", "password", False), ("username1", "password", True), ("email1@email.com", "password", True)])
    def test_login_sql_and_get_user_id(self, username, password, expectExisting): # This test should cover the login portion of user registration as well
        cur = connection.cursor(dictionary=True)

        user = None
        try:
            cur.execute("SELECT user_id, password FROM users WHERE username = %s OR email = %s", (username, username))
            user = cur.fetchone()
            if not expectExisting:
                assert not user
            else:
                assert user
        except Exception as e:
            cur.close()
            assert str(e) and False

        if expectExisting:
            assert user["user_id"] > 0
            assert user["password"] == password
            id = str(uuid.uuid4())
            try:
                cur.execute("DELETE FROM logged_in WHERE user_id=%s", (user["user_id"],))
                cur.execute("INSERT INTO logged_in(user_id, session_token) VALUES(%s, %s)", (user["user_id"], id))
                connection.commit()
                cur.execute("SELECT * FROM logged_in WHERE user_id = %s", (user["user_id"],))
                user = cur.fetchone()
                assert user
                assert user["session_token"] == id # This should be sufficient for ensuring get_user_id works

                connection.commit()
                cur.execute("SELECT * FROM logged_in WHERE user_id = %s", (user["user_id"],))
                user1 = cur.fetchone()
                its = 0
                while user1: # THIS IS A CHECK FOR AUTOMATIC LOGIN EXPIRY
                    its += 1
                    time.sleep(.2)
                    connection.commit()
                    cur.execute("SELECT * FROM logged_in WHERE user_id = %s", (user["user_id"],))
                    user1 = cur.fetchone()
                    if its >= 27:
                        raise Exception("Timed out while waiting for data to be removed from logged_in table")
                assert not user1
            except Exception as e:
                cur.close()
                assert str(e) and False

        cur.close()
    
    @pytest.mark.parametrize("user_id", [(1)])
    def test_fetch_translation_history_sql(self, user_id):
        cur = connection.cursor(dictionary=True)

        rows = None
        try:
            cur.execute("SELECT source_language, original_code, target_language, translated_code, submission_date FROM translation_history WHERE user_id=%s ORDER BY submission_date DESC", (user_id,))
            rows = cur.fetchall()
            assert rows
        except Exception as e:
            cur.close()
            assert str(e) and False
        
        assert len(rows) == 3
        assert rows[0]["source_language"] == "python"
        assert rows[1]["original_code"] == "print('Hello world 1!')"
        assert rows[2]["target_language"] == "javascript"
        assert rows[0]["translated_code"] == "console.log('Hello world 0!');"
        cur.close()
    
    #                                                                                                                                                                                      Testing empty string insertion
    @pytest.mark.parametrize("user_id,precision_rating,ease_rating,speed_rating,future_use_rating,note,expectInsertion", [(1, 5, 5, 5, 5, "This is a note, but it is unique. This should be inserted.", True), (1, 5, 5, 5, 5, "", True), (1, 5, 5, 5, 6, "Rating is not valid, should not be inserted", False), (-1, 5, 5, 5, 5, "User id is invalid, should not be inserted", False), (1, 5, 5, 5, 5, "This note will be very long, and this is the last test case, so don't worry about anything on this line after this string. ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------", False),])
    def test_feedback_form_sql(self, user_id, precision_rating, ease_rating, speed_rating, future_use_rating, note, expectInsertion):
        cur = connection.cursor(dictionary=True)

        #Test setup should already insert 1 value into the table
        try:
            insertion = """
            INSERT INTO user_feedback (user_id, precision_rating, ease_rating, speed_rating, future_use_rating, note) 
            VALUES (%s, %s, %s, %s, %s, %s)
            """
            cur.execute(insertion, (user_id, precision_rating, ease_rating, speed_rating, future_use_rating, note))
            connection.commit()

            if expectInsertion:
                cur.execute("SELECT * FROM user_feedback WHERE user_id=%s AND precision_rating=%s AND note=%s", (user_id, precision_rating, note))
                feedback = cur.fetchone()
                cur.close()
                assert feedback
            elif not expectInsertion:
                #SQL query should have failed, so this should never hit since we should be in the except block 
                assert False
        except Exception as e:
            if expectInsertion:
                cur.close()
                assert str(e) and False
            elif not expectInsertion:
                cur.execute("SELECT * FROM user_feedback WHERE note=%s", (note,))
                feedback = cur.fetchone()
                cur.close()
                assert not feedback

        if cur:
            cur.close()
    
    @pytest.mark.parametrize("translation_id,user_id,star_rating,note, expectInsert", [(1, 1, 1, "Unique note", True), (2, 1, 6, "Bad star rating value", False), (3, 1, 5, "I Will make this note far too long so that it does not insert. There are no more test cases after this one, so you do not need to look further than this. _-----------------------------------------------------------------------------------------------------------------------------------------------------------", False)])
    def test_translation_feedback_sql(self, translation_id, user_id, star_rating, note, expectInsert):
        cur = connection.cursor(dictionary=True)
        
        try:
            cur.execute("INSERT INTO translation_feedback (translation_id, user_id, star_rating, note) VALUES (%s, %s, %s, %s)", (translation_id, user_id, star_rating, note))
            connection.commit()

            if expectInsert:
                cur.execute("SELECT * FROM translation_feedback WHERE translation_id=%s AND user_id=%s AND star_rating=%s AND note=%s", (translation_id, user_id, star_rating, note))
                feedback = cur.fetchone()
                cur.close()
                assert feedback
            elif not expectInsert:
                #SQL query should have failed, so this should never hit since we should be in the except block 
                assert False
        except Exception as e:
            if expectInsert:
                cur.close()
                assert str(e) and False
            elif not expectInsert:
                cur.execute("SELECT * FROM translation_feedback WHERE note=%s", (note,))
                feedback = cur.fetchone()
                cur.close()
                assert not feedback

        if cur:
            cur.close()

    @pytest.mark.parametrize("user_id,srcLang,message,toLang,translation", [(1, "python", "print('Hi')", "javascript", "console.log('Hi')")])
    def test_translate_log_translate_errors_and_delete_translation_sql(self, user_id, srcLang, message, toLang, translation):
        cur = connection.cursor(dictionary=True)

        #Testing initial check for rate limit
        #Translation_history should be pre-populated w/ data
        try:
            cur.execute("SELECT submission_date FROM translation_history WHERE user_id=%s ORDER BY submission_date DESC LIMIT 1", (user_id,))
            lastSubmit = cur.fetchone()

            lastSubmit = lastSubmit['submission_date']
            difference = datetime.datetime.now() - lastSubmit
            rate_limit = datetime.timedelta(seconds=100) #We aren't really trying to test if datetime is working, so just set a high time delta

            assert difference < rate_limit
        except Exception as e:
            cur.close()
            assert str(e) and False #Exception in check for rate limit

        translation_id = -1
        try:
            cur.execute(
                "INSERT INTO translation_history(user_id, source_language, original_code, target_language, translated_code, status, total_tokens) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (user_id, srcLang, message, toLang, user_id, "in progress", 0)
            )
            connection.commit()
            cur.execute("SELECT translation_id FROM translation_history WHERE user_id=%s and status=%s", (user_id, "in progress"))
            val = cur.fetchone()
            assert val #If this fails, then there was a failure to insert the temporary entry into db
            translation_id = val["translation_id"]
            assert translation_id
        except Exception as e:
            cur.close()
            assert str(e) and False

        try:
            cur.execute(
                "UPDATE translation_history SET translated_code = %s, status = %s, total_tokens = %s WHERE translated_code = %s AND status = %s", 
                (translation, "stop", 85, user_id, "in progress")
            )
            connection.commit()
            cur.execute("SELECT * FROM translation_history WHERE user_id=%s AND original_code=%s", (user_id, message))
            entry = cur.fetchone()
            assert entry
            assert entry["translated_code"] == translation and entry["total_tokens"] == 85
            translation_id = entry["translation_id"]
        except Exception as e:
            cur.close()
            assert str(e) and False

        #Test translation error logging
        #Modified function    takes connection rather than mysql
        def db_log_translation_errors(connection, translation_id, errorMessage, errorCode = None, etype = "other"):
            if translation_id < 1:
                print("Issue with SQL code on inserting in progress translation into translation_history")
                return
            cur = connection.cursor()
            try:
                cur.execute("INSERT INTO translation_errors(translation_id, error_message, error_code, error_type) VALUES(%s, %s, %s, %s)", (translation_id, errorMessage, errorCode, etype))
                connection.commit()
            except Exception as e:
                print("Error while attempting to insert a translation error into the database!")
                print("Error message:", str(e))
                cur.close()
                return
            cur.close()

        try:
            db_log_translation_errors(connection, translation_id, "This is an API error", 400, "api")
            connection.commit()
            cur.execute("SELECT * FROM translation_errors WHERE translation_id=%s AND error_type=%s", (translation_id, "api"))
            entry = cur.fetchone()
            assert entry

            db_log_translation_errors(connection, translation_id, "This is some other error")
            connection.commit()
            cur.execute("SELECT * FROM translation_errors WHERE translation_id=%s AND error_type=%s", (translation_id, "other"))
            entry2 = cur.fetchone()
            assert entry2
        except Exception as e:
            cur.close()
            assert str(e) and False 
        
        ids = [translation_id, 12123] #random id
        deletion = "DELETE FROM translation_history WHERE user_id=%s AND ("
        for i in range(len(ids)):
            deletion += "translation_id=%s OR "
        deletion = deletion.strip(" OR ")
        deletion += ")"

        try:
            cur.execute(deletion, (user_id, *ids))
            connection.commit()
            cur.execute("SELECT * FROM translation_history WHERE user_id=%s AND original_code=%s", (user_id, message)) # This entry should have been removed
            entry = cur.fetchone()
            assert not entry
        except Exception as e:
            cur.close()
            assert str(e) and False

        cur.close()
    
    def test_send_email_sql_and_automatic_expiry(self):
        cur = connection.cursor(dictionary=True)

        id = str(uuid.uuid4())
        user = {"user_id": 1}
        try:
            cur.execute("DELETE FROM password_reset WHERE user_id=%s", (user["user_id"],))
            cur.execute("INSERT INTO password_reset(user_id, email_token) VALUES(%s, %s)", (user["user_id"], id))
            connection.commit()

            cur.execute("SELECT * FROM password_reset WHERE user_id=%s AND email_token=%s", (user["user_id"], id))
            entry = cur.fetchone()
            assert entry

            its = 0
            while entry: # THIS IS A CHECK FOR AUTOMATIC FORGET PASSWORD EXPIRY
                its += 1
                time.sleep(.2)
                connection.commit()
                cur.execute("SELECT * FROM password_reset WHERE user_id = %s", (user["user_id"],))
                entry = cur.fetchone()
                if its >= 27:
                    raise Exception("Timed out while waiting for data to be removed from password_reset table")
            assert not entry
        except Exception as e:
            cur.close()
            assert str(e) and False
            
        cur.close()

    def test_password_recovery_sql(self):
        cur = connection.cursor(dictionary=True)

        #setup- make a new user for this test
        user = None
        try:
            user = helpers.insert_new_user(connection, "newUser1", "newEmail@email.com", "password")
        except Exception as e:
            cur.close()
            assert str(e) and False

        id = str(uuid.uuid4())
        try:
            cur.execute("DELETE FROM password_reset WHERE user_id=%s", (user["user_id"],))
            cur.execute("INSERT INTO password_reset(user_id, email_token) VALUES(%s, %s)", (user["user_id"], id))
            connection.commit()
        except Exception as e:
            cur.close()
            assert str(e) and False
            
        user = None
        try:
            cur.execute("SELECT user_id FROM password_reset WHERE email_token = %s", (id,))
            user = cur.fetchone()
            assert user
        except Exception as e: 
            cur.close()
            assert str(e) and False

        user_id = user["user_id"]
        # Update the password
        try:
            cur.execute("UPDATE users SET password = %s WHERE user_id = %s", ("newPassword", user_id))
            cur.execute("DELETE FROM password_reset WHERE user_id = %s", (user_id,))
            connection.commit()
            cur.execute("SELECT * FROM password_reset WHERE user_id = %s", (user_id,))
            user = cur.fetchone()
            assert not user

            cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
            user = cur.fetchone()
            assert user and user["password"] == "newPassword"
        except Exception as e:
            cur.close()
            assert str(e) and False
        
        #TEST TEARDOWN
        try:
            helpers.delete_user(connection, user_id)
        except Exception as e:
            cur.close()
            assert str(e) and False

        cur.close()
     
    @pytest.mark.parametrize("new_user,expectUnique", [("newusername", True), ("username1", False)])
    def test_change_username_sql(self, new_user, expectUnique):
        cur = connection.cursor(dictionary=True)

        #setup- make a new user for this test
        user = None
        try:
            user = helpers.insert_new_user(connection, "newUser1", "newEmail@email.com", "password")
            assert user
        except Exception as e:
            cur.close()
            assert str(e) and False
        
        user_id = user["user_id"]

        try:
            cur.execute("SELECT username FROM users WHERE username=%s", (new_user,))
            user = cur.fetchone()
            if expectUnique:
                assert not user
            else:
                assert user
        except Exception as e:
            cur.close()
            assert str(e) and False

        if expectUnique: #this is the only case in which there will be an update
            try:
                cur.execute("SELECT username FROM users WHERE user_id=%s", (user_id,))
                user = cur.fetchone()
                assert user
            except Exception as e:
                cur.close()
                return str(e) and False
            
            try:
                cur.execute("UPDATE users SET username=%s WHERE user_id=%s", (new_user, user_id))
                connection.commit()
                cur.execute("SELECT * FROM users WHERE user_id = %s", (user_id,))
                user = cur.fetchone()
                assert user["username"] == new_user
            except Exception as e:
                cur.close()
                assert str(e) and False

        #teardown
        try:
            helpers.delete_user(connection, user_id)
        except Exception as e:
            cur.close()
            assert str(e) and False

        cur.close()

    def test_change_password_sql(self):
        cur = connection.cursor(dictionary=True)

        #setup- make a new user for this test
        user = None
        try:
            user = helpers.insert_new_user(connection, "newUser1", "newEmail@email.com", "password")
            assert user
        except Exception as e:
            cur.close()
            assert str(e) and False
        
        user_id = user["user_id"]

        #change password query
        try:
            cur.execute("UPDATE users SET password=%s WHERE user_id=%s", ("newPassword", user_id))
            connection.commit()
            cur.execute("SELECT * FROM users WHERE user_id=%s", (user_id,))
            user = cur.fetchone()
            assert user and user["password"] == "newPassword"
        except Exception as e:
            cur.close()
            assert str(e) and False
        
        #teardown
        try:
            helpers.delete_user(connection, user_id)
        except Exception as e:
            cur.close()
            assert str(e) and False
            
        cur.close()
    
    # ****************** TEST INFO ****************** #
    # This test is unneeded because the exact queries #
    # used in account deletion are already being used #
    # in the function helpers.delete_user             #
    # ****************** TEST INFO ****************** #
    '''
    def test_delete_account_sql(self):
        pass
    '''
    
    def test_logout_sql(self, client):
        cur = connection.cursor(dictionary=True)
        
        sessionToken = str(uuid.uuid4())
        try: 
            cur.execute("INSERT INTO logged_in(user_id, session_token) VALUES(%s, %s)", (1, sessionToken))
            connection.commit()
            cur.execute("SELECT * FROM logged_in WHERE session_token=%s", (sessionToken,))
            entry = cur.fetchone()
            assert entry and entry["session_token"] == sessionToken
        except Exception as e:
            cur.close()
            assert str(e) and False

        response = client.post("/userLogout", data=json.dumps({"sessionToken": sessionToken}))
        response = response.json

        assert "success" in response and response["success"]

        connection.commit()
        try:
            cur.execute("SELECT * FROM logged_in WHERE session_token=%s", (sessionToken,))
            newEntry = cur.fetchone()
            assert not newEntry
        except Exception as e:
            cur.close()
            assert str(e) and False

        cur.close()

    def test_aggregated_feedback(self, client):
        cur = connection.cursor(dictionary=True)

        try:
            cur.execute("DELETE FROM translation_feedback")
            cur.execute("INSERT INTO translation_feedback(translation_id, user_id, star_rating, note) VALUES (%s, %s, %s, %s)", (1, 3, 3, "Okay translation."))
            cur.execute("INSERT INTO translation_feedback(translation_id, user_id, star_rating, note) VALUES (%s, %s, %s, %s)", (2, 1, 5, "AMAZING!"))
            cur.execute("INSERT INTO translation_feedback(translation_id, user_id, star_rating, note) VALUES (%s, %s, %s, %s)", (3, 2, 1, "Horrible and broken."))
            connection.commit()
        except Exception as e:
            cur.close()
            connection.rollback()
            assert str(e) and False
        
        try:
            selection = "SELECT AVG(star_rating) AS average_rating, COUNT(star_rating) AS total_ratings FROM translation_feedback"
            cur.execute(selection)
            data = cur.fetchone()
        except Exception as e:
            if cur:
                cur.close()
            assert str(e) and False
        
        assert data["average_rating"] == 3
        assert data["total_ratings"] == 3