from flask import Flask
from flask_cors import CORS
from flask_mysqldb import MySQL
from openai import OpenAI
import os
import time
from dotenv import load_dotenv


from functions import register_user as register, user_login as login, submit_feedback as feedback, translate_code as translate, translation_feedback as translationFeedback
from functions import api_status as status, change_profile as profile, logout, forgot_password, delete_translations
from functions import translation_history
from functions import two_factor

load_dotenv()

# All functions require a return statement
def create_app(testing: bool):
    api = Flask(__name__)
    CORS(api)

    # mysql configurations
    api.config['MYSQL_CURSORCLASS'] = 'DictCursor'
    if testing:
        api.config['MYSQL_HOST'] = 'localhost'
        api.config['MYSQL_USER'] = 'root'
        api.config['MYSQL_DB'] = 'codecraft_testing'
        api.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
    else:
        api.config['MYSQL_HOST'] = os.getenv('DB_URL')
        api.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
        api.config['MYSQL_DB'] = os.getenv('MYSQL_DB')
        api.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')

    mysql = MySQL(api)
    
    gpt_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    # registration page
    @api.route('/registerNewUser', methods = ["POST"])
    def register_user():
        return register.register(mysql)


    # login page
    @api.route('/userLoginCredentials', methods=['POST'])
    def user_login():
        return login.login(mysql)
        

    #feedback page
    @api.route('/submitFeedback', methods=['POST'])
    def submit_feedback():
        return feedback.submit_feedback(mysql)

    # code translation backend
    @api.route('/translate', methods=['POST'])
    def translate_code():
        return translate.translate(mysql, gpt_client)


    # translation feedback
    @api.route('/submitTranslationFeedback', methods=['POST'])
    def translation_feedback():
        return translationFeedback.submit_translation_feedback(mysql)
    

    # Fetch aggregated feedback
    @api.route('/getAggregatedFeedback')
    def aggregated_feedback():
        return translationFeedback.aggregated_feedback(mysql)


    # API status
    @api.route('/getApiStatus')
    def get_status():
        return status.get_status(gpt_client.api_key)
    

    # Change username
    @api.route('/userChangeUsername', methods=['POST'])
    def change_username():
        return profile.change_username(mysql)


    # Change password
    @api.route('/userChangePassword', methods=['POST'])
    def change_password():
        return profile.change_password(mysql)


    # Email for password reset
    @api.route('/userSendEmail', methods=['POST'])
    def send_email():
        return forgot_password.send_email(mysql)


    # Reset user password
    @api.route('/userResetPassword', methods=['POST'])
    def reset_password():
        return forgot_password.reset_password(mysql)


    # Delete account
    @api.route('/deleteAccount', methods=['POST'])
    def delete_account():
        return profile.delete_user(mysql)
    

    # Pull translation history
    @api.route('/translationHistory', methods=['POST'])
    def translation_history_route():
        return translation_history.get_translation_history(mysql)


    # Generate the initial QR code for 2FA
    @api.route('/getQRCode', methods=['POST'])
    def generate_qr_code():
        return two_factor.generate_qr_code(mysql)
    

    # Verify the setup TOTP for 2Fa
    @api.route('/validateSetupTOTP', methods=['POST'])
    def validate_setup_totp():
        return two_factor.validate_setup_totp(mysql)

    
    # Verify the TOTP for 2Fa
    @api.route('/validateTOTP', methods=['POST'])
    def validate_totp():
        return two_factor.validate_totp(mysql)


    # Logout
    @api.route('/userLogout', methods=['POST'])
    def user_logout():
        return logout.logout(mysql)
    

    # Manage translation history
    @api.route('/deleteTranslations', methods=['POST'])
    def manage_translation_history():
        return delete_translations.delete_translations(mysql)

    return api