import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv()

# mysql connection parameters
mysql_config = {
    'host': os.getenv('DB_URL'),
    'user': os.getenv('MYSQL_USER'),
    'password': os.getenv('MYSQL_PASSWORD'),
}

# connect to server
connection = mysql.connector.connect(**mysql_config)

# create and switch to the database
create_database_query = "CREATE DATABASE IF NOT EXISTS codecraft"
cursor = connection.cursor()
cursor.execute(create_database_query)

mysql_config['database'] = 'codecraft'
connection.close()
connection = mysql.connector.connect(**mysql_config)

# create users table
cursor = connection.cursor()
create_user_table_query = """
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(24) NOT NULL UNIQUE,
    email VARCHAR(64) NOT NULL UNIQUE,
    password VARCHAR(64) NOT NULL,
    totp VARCHAR(144)
)
"""
cursor.execute(create_user_table_query)

create_twofa_setup_table_query = """
CREATE TABLE IF NOT EXISTS twofa_setup (
    twofa_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    fernet_key VARCHAR(64),
    totp_key VARCHAR(144),
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
)
"""
cursor.execute(create_twofa_setup_table_query)

create_twofa_login_table_query = """
CREATE TABLE IF NOT EXISTS twofa_login (
    twofa_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    fernet_key VARCHAR(64),
    login_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
)
"""
cursor.execute(create_twofa_login_table_query)

# create translation table
create_translation_table_query = """
CREATE TABLE IF NOT EXISTS translation_history (
    translation_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    source_language VARCHAR(10),
    original_code TEXT(16383),
    target_language VARCHAR(10),
    translated_code TEXT(16383),
    status VARCHAR(16),
    submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    total_tokens INT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
)
"""
cursor.execute(create_translation_table_query)

# create translation error table
create_translation_error_table_query = """
CREATE TABLE IF NOT EXISTS translation_errors (
    error_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    translation_id INT NOT NULL,
    error_message VARCHAR(2048) NOT NULL,
    error_code INT,
    error_type VARCHAR(8) NOT NULL,
    FOREIGN KEY (translation_id) REFERENCES translation_history(translation_id) ON DELETE CASCADE
)
"""
cursor.execute(create_translation_error_table_query)

# create feedback form table
create_feedback_table_query = """
CREATE TABLE IF NOT EXISTS user_feedback (
    feedback_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    precision_rating INT CHECK (precision_rating BETWEEN 1 AND 5),
    ease_rating INT CHECK (ease_rating BETWEEN 1 AND 5),
    speed_rating INT CHECK (speed_rating BETWEEN 1 AND 5),
    future_use_rating INT CHECK (future_use_rating BETWEEN 1 AND 5),
    note VARCHAR(300),
    submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
)
"""
cursor.execute(create_feedback_table_query)

# create translation feedback table
create_translation_feedback_table_query = """
CREATE TABLE IF NOT EXISTS translation_feedback (
    feedback_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    translation_id INT NOT NULL,
    user_id INT NOT NULL,
    star_rating INT CHECK (star_rating BETWEEN 1 AND 5),
    note VARCHAR(150),
    submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (translation_id) REFERENCES translation_history(translation_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
)
"""
cursor.execute(create_translation_feedback_table_query)

# create logged in user table
create_logged_in_user_query = """
CREATE TABLE IF NOT EXISTS logged_in (
    login_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    session_token CHAR(36) NOT NULL,
    login_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
)
"""
cursor.execute(create_logged_in_user_query)

create_password_reset_table_query = """
CREATE TABLE IF NOT EXISTS password_reset (
    reset_id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    email_token CHAR(36) NOT NULL,
    email_request_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
)
"""
cursor.execute(create_password_reset_table_query)

create_remove_old_email_tokens_procedure_query = """
CREATE PROCEDURE IF NOT EXISTS RemoveOldEmailTokens()
BEGIN
    DECLARE cutoff_time TIMESTAMP;
    SET cutoff_time = NOW() - INTERVAL 15 MINUTE;

    DELETE FROM password_reset WHERE email_request_time < cutoff_time;
END
"""
cursor.execute(create_remove_old_email_tokens_procedure_query)

create_remove_old_email_tokens_event_query = """
CREATE EVENT IF NOT EXISTS RemoveOldEmailTokensEvent
ON SCHEDULE EVERY 1 MINUTE
DO
BEGIN
    CALL RemoveOldEmailTokens();
END;
"""
cursor.execute(create_remove_old_email_tokens_event_query)

create_remove_old_fernet_keys_procedure_query = """
CREATE PROCEDURE IF NOT EXISTS RemoveOldFernetKeys()
BEGIN
    DECLARE cutoff_time TIMESTAMP;
    SET cutoff_time = NOW() - INTERVAL 5 MINUTE;

    DELETE FROM twofa_login WHERE login_date < cutoff_date;
END
"""
cursor.execute(create_remove_old_fernet_keys_procedure_query)

create_remove_old_fernet_keys_event_query = """
CREATE EVENT IF NOT EXISTS RemoveOldFernetKeysEvent
ON SCHEDULE EVERY 1 MINUTE
DO
BEGIN
    CALL RemoveOldFernetKeys();
END;
"""
cursor.execute(create_remove_old_fernet_keys_event_query)

create_remove_old_logins_procedure_query = """
CREATE PROCEDURE IF NOT EXISTS RemoveOldLogins()
BEGIN
    DECLARE cutoff_date TIMESTAMP;
    SET cutoff_date = NOW() - INTERVAL 1 DAY;

    DELETE FROM logged_in WHERE login_date < cutoff_date;
END
"""
cursor.execute(create_remove_old_logins_procedure_query)

create_remove_old_logins_event_query = """
CREATE EVENT IF NOT EXISTS RemoveOldLoginsEvent
ON SCHEDULE EVERY 1 MINUTE
DO
BEGIN
    CALL RemoveOldLogins();
END;
"""
cursor.execute(create_remove_old_logins_event_query)

cursor.execute("SHOW VARIABLES LIKE 'event_scheduler'")
result = cursor.fetchone()
event_scheduler_status = result[1]
if event_scheduler_status != 'ON':
    cursor.execute("SET GLOBAL event_scheduler = ON")

# save changes and close
connection.commit()
cursor.close()
connection.close()
