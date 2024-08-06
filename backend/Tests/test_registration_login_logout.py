import pytest
from Tests.Mocks.MockFlaskMysql import MockFlaskMysqlConnection, MockFlaskMysqlCursor
from app import create_app
import json
from flask_mysqldb import MySQL
from mock import Mock

class TestRegistrationLoginLogout:
    @pytest.fixture()
    def app(self):
        app = create_app(True)
        app.config.update({
            "TESTING": True,
        })

        # other setup can go here

        yield app

        # clean up / reset resources here


    @pytest.fixture()
    def client(self, app):
        return app.test_client()


    @pytest.fixture()
    def runner(self, app):
        return app.test_cli_runner()
    
    @pytest.mark.parametrize("username,email,password", [("sampleUser", "sample.example@example.com", "somepassword"), ("    sampleUser    ", "\nsample.example@example.com\t", "anotherpassword")])
    def test_user_registration_success(self, client, username, email, password, monkeypatch):
        # mocks connection
        monkeypatch.setattr(MySQL, "connection", MockFlaskMysqlConnection)
        test_mock = Mock(side_effect=[None, {"user_id": 1}])
        monkeypatch.setattr(MockFlaskMysqlCursor, "fetchone", test_mock)

        response = client.post("/registerNewUser", data=json.dumps({"username": username, "email": email, "password": password}))
        response = response.json

        assert response["success"]
        assert not response["hasError"]

    @pytest.mark.parametrize("username", [("short"), ("sampleUsernameIsFarTooLongAndThrowsError"), ("__------__"), ("this$is$bad$format")])
    def test_user_registration_invalid_username_returns_error_response(self, client, username):
        valid_email = "sample.example@example.com"
        valid_password = "somepassword"

        response = client.post("/registerNewUser", data=json.dumps({"username": username, "email": valid_email, "password": valid_password}))
        response = response.json

        assert "success" not in response
        assert "emailErrors" not in response
        assert response["hasError"]
        assert "usernameErrors" in response
        assert len(response["usernameErrors"]) == 1

    @pytest.mark.parametrize("email", [("this.email@is.wayyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy.toooooooooo.long"),
                                        ("thisemail@usesinvalidformat"), ("thisemail.also@usesinvalid-format"), ("thisemail@usesinvalidformat..also")])
    def test_user_registration_invalid_email_returns_error_response(self, client, email):
        valid_username = "sampleUser"
        valid_password = "somepassword"

        response = client.post("/registerNewUser", data=json.dumps({"username": valid_username, "email": email, "password": valid_password}))
        response = response.json

        assert "success" not in response
        assert "usernameErrors" not in response
        assert response["hasError"]
        assert "emailErrors" in response
        assert len(response["emailErrors"]) == 1

    @pytest.mark.parametrize("username", [("duplicateUser")])
    def test_user_registration_duplicate_username_fails(self, client, username, monkeypatch):
        # mocks
        monkeypatch.setattr(MySQL, "connection", MockFlaskMysqlConnection)
        monkeypatch.setattr(MockFlaskMysqlCursor, "fetchone", lambda self: {"username": "duplicateUser", "email" : "valid@email.com"})

        response = client.post("/registerNewUser", data=json.dumps({"username": username, "email": "sample.example@example.com", "password": "somepassword"}))
        response = response.json
        
        assert "success" not in response
        assert response["hasError"]
        assert "sqlErrors" in response
        assert len(response["sqlErrors"]) == 1 and response["sqlErrors"][0] == "Chosen username already in use"

    @pytest.mark.parametrize("email", [("duplicate@email.com")])
    def test_user_registration_duplicate_email_fails(self, client, email, monkeypatch):
        # mocks
        monkeypatch.setattr(MySQL, "connection", MockFlaskMysqlConnection)
        monkeypatch.setattr(MockFlaskMysqlCursor, "fetchone", lambda self: {"username": "validUser", "email" : "duplicate@email.com"})

        response = client.post("/registerNewUser", data=json.dumps({"username": "sampleUser", "email": email, "password": "somepassword"}))
        response = response.json
        
        assert "success" not in response
        assert response["hasError"]
        assert "sqlErrors" in response
        assert len(response["sqlErrors"]) == 1 and response["sqlErrors"][0] == "Chosen email already in use"

    @pytest.mark.parametrize("username,password,key", [("validUser", "validPassword", "9d832321b2d6e7c8c7d89671825b26fff21be4f4bbaf664f2df7e46d2336963a"), ("valid@email.com", "validPassword", "9d832321b2d6e7c8c7d89671825b26fff21be4f4bbaf664f2df7e46d2336963a")])
    def test_user_login_success_two_factor_disabled(self, client, username, password, key, monkeypatch):
        # mocks
        monkeypatch.setattr(MySQL, "connection", MockFlaskMysqlConnection)
        mock = Mock(side_effect=[{"user_id": "1", "password" : "validPassword"}, None, {"totp": None}])
        monkeypatch.setattr(MockFlaskMysqlCursor, "fetchone", mock)

        response = client.post("/userLoginCredentials", data=json.dumps({"username": username, "password": password, "key": key}))
        response = response.json

        assert "success" in response and response["success"]
        assert not response["hasError"]      #sessionToken is uuid, so should be len 36
        assert response["totp"] == "disabled"
        assert "sessionToken" in response and len(response["sessionToken"]) == 36

    @pytest.mark.parametrize("username,password,key", [("validUser", "validPassword", "9d832321b2d6e7c8c7d89671825b26fff21be4f4bbaf664f2df7e46d2336963a"), ("valid@email.com", "validPassword", "9d832321b2d6e7c8c7d89671825b26fff21be4f4bbaf664f2df7e46d2336963a")])
    def test_user_login_success_two_factor_enabled(self, client, username, password, key, monkeypatch):
        # mocks
        monkeypatch.setattr(MySQL, "connection", MockFlaskMysqlConnection)
        mock = Mock(side_effect=[{"user_id": "1", "password" : "validPassword"}, None, {"totp": "gAAAAABmIzSHEOp2tWCwNXilYPDIAzO4Ugp-274gAS50Dr9XsHfIDzMFPkjsrrpw5p5EkpFkj8_TgTXy8i47k3Dhq7VS6V2zyvqrOZo4sg1jmIhdKgXZs4naldLw3MKZVHn-EmcpdPcn"}])
        monkeypatch.setattr(MockFlaskMysqlCursor, "fetchone", mock)

        response = client.post("/userLoginCredentials", data=json.dumps({"username": username, "password": password, "key": key}))
        response = response.json

        assert "success" in response and response["success"]
        assert not response["hasError"]      #sessionToken is uuid, so should be len 36
        assert response["totp"] == "enabled"
        assert "sessionToken" in response and len(response["sessionToken"]) == 36

    @pytest.mark.parametrize("username,password,key", [("unrecognizedUser", "validPassword", "9d832321b2d6e7c8c7d89671825b26fff21be4f4bbaf664f2df7e46d2336963a")])
    def test_user_login_unrecognized_username_or_email_returns_error_response(self, client, username, password, key, monkeypatch):
        # mocks
        monkeypatch.setattr(MySQL, "connection", MockFlaskMysqlConnection)
        
        response = client.post("/userLoginCredentials", data=json.dumps({"username": username, "password": password, "key": key}))
        response = response.json

        assert "success" not in response
        assert response["hasError"]
        assert "errorMessage" in response and response["errorMessage"] == "User not found"
    @pytest.mark.parametrize("username,password,key", [("validUser", "incorrectPassword", "9d832321b2d6e7c8c7d89671825b26fff21be4f4bbaf664f2df7e46d2336963a")])
    def test_user_login_incorrect_password_returns_error_response(self, client, username, password, key, monkeypatch):
        # mocks
        monkeypatch.setattr(MySQL, "connection", MockFlaskMysqlConnection)
        monkeypatch.setattr(MockFlaskMysqlCursor, "fetchone", lambda self: {"user_id": 1, "password": "correctPassword"})

        response = client.post("/userLoginCredentials", data=json.dumps({"username": username, "password": password, "key": key}))
        response = response.json
        
        assert "success" not in response
        assert response["hasError"]
        assert "errorMessage" in response and response["errorMessage"] == "Invalid password"
    
    @pytest.mark.parametrize("username", [("bad@userOrEmail")])
    def test_user_login_invalid_username_or_email_returns_error_response(self, client, username):
        response = client.post("/userLoginCredentials", data=json.dumps({"username": username, "password": "mockpassword"}))
        response = response.json
        
        assert "success" not in response
        assert response["hasError"]
        assert "errorMessage" in response
        assert response["errorMessage"] == "Invalid format for username or email"

    @pytest.mark.parametrize("sessionToken", [("cbcc70c5-a45c-48e0-83df-b9714c9122a2")])
    def test_logout_success(self, client, sessionToken, monkeypatch):
        monkeypatch.setattr(MySQL, "connection", MockFlaskMysqlConnection)
        response = client.post("/userLogout", data=json.dumps({"sessionToken": sessionToken}))
        response = response.json
        
        assert "success" in response
        assert not response["hasError"]

    @pytest.mark.parametrize("sessionToken", [(None), ("")])
    def test_logout_no_token_set_returns_error_response(self, client, sessionToken, monkeypatch):
        monkeypatch.setattr(MySQL, "connection", MockFlaskMysqlConnection)
        response = client.post("/userLogout", data=json.dumps({"sessionToken": sessionToken}))
        response = response.json
        
        assert "success" not in response
        assert response["hasError"]
        assert "errorMessage" in response and response["errorMessage"] == "User has no session token set."

    @pytest.mark.parametrize("sessionToken", [("cbcc70c5-a45c-48e0-83df-b9714c9122a2")])
    def test_logout_sql_error_is_caught(self, client, sessionToken, monkeypatch):
        monkeypatch.setattr(MySQL, "connection", MockFlaskMysqlConnection)
        def seeded_error(self, query, format=None):
            raise Exception("SQL Error")
        monkeypatch.setattr(MockFlaskMysqlCursor, "execute", seeded_error)
        response = client.post("/userLogout", data=json.dumps({"sessionToken": sessionToken}))
        response = response.json
        
        assert "success" not in response
        assert response["hasError"]
        assert "errorMessage" in response and response["errorMessage"] == "SQL Error"