import pytest
from Tests.Mocks.MockFlaskMysql import MockFlaskMysqlConnection, MockFlaskMysqlCursor
from app import create_app
import json
from flask_mysqldb import MySQL
from mock import Mock
from functions import get_user_id
import smtplib

class TestForgotPassword:
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
    

    @pytest.mark.parametrize("email", [("notarealuser@njit.edu"), ("aaaaaaa@abc123.com"), ("username123"), ("mdefran131"), ("real-username")])
    def test_successful_email(self, client, email, monkeypatch):
        # mocks connection
        monkeypatch.setattr(MySQL, "connection", MockFlaskMysqlConnection)
        monkeypatch.setattr(MockFlaskMysqlCursor, "fetchone", lambda self: {"user_id": 1, "email": "email@email.com", "username": "username"})

        response = client.post("/userSendEmail", data=json.dumps({"email": email}))
        response = response.json

        assert "success" in response
        assert response["success"]
        assert not response["hasError"]

    @pytest.mark.parametrize("email", [("notarealuser@njit.edu"), ("mdefran131")])
    def test_user_not_found(self, client, email, monkeypatch):
        # mocks connection
        monkeypatch.setattr(MySQL, "connection", MockFlaskMysqlConnection)

        response = client.post("/userSendEmail", data=json.dumps({"email": email}))
        response = response.json

        assert "success" not in response
        assert response["hasError"]
        assert response["errorMessage"].startswith("User not found")

    @pytest.mark.parametrize("email", [("short"), ("--------"), ("email@email..com"), ("emailatemail.com"), ("email@emaildotcom"), ("email@email@email.com"), ("email@.com")])
    def test_invalid_email_or_username(self, client, email, monkeypatch):
        # mocks connection
        monkeypatch.setattr(MySQL, "connection", MockFlaskMysqlConnection)

        response = client.post("/userSendEmail", data=json.dumps({"email": email}))
        response = response.json

        assert "success" not in response
        assert response["hasError"]
        assert response["errorMessage"].startswith("Invalid format for username or email")

    @pytest.mark.parametrize("email", [("email@email.com")])
    def test_failed_email(self, client, email, monkeypatch):
        def SeededError():
            raise Exception("Error sending email.")

        # mocks connection
        monkeypatch.setattr(MySQL, "connection", MockFlaskMysqlConnection)
        monkeypatch.setattr(MockFlaskMysqlCursor, "fetchone", lambda self: {"user_id": 1, "email": "email@email.com", "username": "username"})
        monkeypatch.setattr(smtplib, "SMTP", SeededError)

        response = client.post("/userSendEmail", data=json.dumps({"email": email}))
        response = response.json

        assert "success" not in response
        assert response["hasError"]
        assert response["errorMessage"].startswith("Failed to send email")

    @pytest.mark.parametrize("newPass,emailToken", [("Password1!", "0c5a0708-09ca-4869-a22b-fde2a89f4ad9")])
    def test_successful_password_reset(self, client, newPass, emailToken, monkeypatch):
        monkeypatch.setattr(MySQL, "connection", MockFlaskMysqlConnection)
        monkeypatch.setattr(MockFlaskMysqlCursor, "fetchone", lambda self: {"user_id": 1})

        response = client.post("/userResetPassword", data=json.dumps({"newPass": newPass, "emailToken": emailToken}))
        response = response.json

        assert "success" in response
        assert response["success"]
        assert not response["hasError"]

    @pytest.mark.parametrize("newPass", [("Password1!")])
    def test_missing_token(self, client, newPass, monkeypatch):
        monkeypatch.setattr(MySQL, "connection", MockFlaskMysqlConnection)
        monkeypatch.setattr(MockFlaskMysqlCursor, "fetchone", lambda self: {"user_id": 1})

        response = client.post("/userResetPassword", data=json.dumps({"newPass": newPass}))
        response = response.json

        assert "success" not in response
        assert response["hasError"]
        assert response["errorMessage"].startswith("No email token found")

    @pytest.mark.parametrize("emailToken", [("0c5a0708-09ca-4869-a22b-fde2a89f4ad9")])
    def test_missing_password(self, client, emailToken, monkeypatch):
        monkeypatch.setattr(MySQL, "connection", MockFlaskMysqlConnection)
        monkeypatch.setattr(MockFlaskMysqlCursor, "fetchone", lambda self: {"user_id": 1})

        response = client.post("/userResetPassword", data=json.dumps({"emailToken": emailToken}))
        response = response.json

        assert "success" not in response
        assert response["hasError"]
        assert response["errorMessage"].startswith("No password submitted")

    @pytest.mark.parametrize("newPass,emailToken", [("Password1!", "0c5a0708-09ca-4869-a22b-fde2a89f4ad9")])
    def test_invalid_token(self, client, newPass, emailToken, monkeypatch):
        monkeypatch.setattr(MySQL, "connection", MockFlaskMysqlConnection)

        response = client.post("/userResetPassword", data=json.dumps({"newPass": newPass, "emailToken": emailToken}))
        response = response.json

        assert "success" not in response
        assert response["hasError"]
        assert response["errorMessage"].startswith("Invalid email token")