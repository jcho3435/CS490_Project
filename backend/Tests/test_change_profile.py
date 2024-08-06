import pytest
from Tests.Mocks.MockFlaskMysql import MockFlaskMysqlConnection, MockFlaskMysqlCursor
from app import create_app
import json
from flask_mysqldb import MySQL
from mock import Mock
from functions import get_user_id

class TestChangeProfile:
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
    
    @pytest.mark.parametrize("oldUser,newUser,sessionToken", [("username", "username1", "cbcc70c5-a45c-48e0-83df-b9714c9122a2")])
    def test_username_change_success(self, client, oldUser, newUser, sessionToken, monkeypatch):
        # mocks connection
        monkeypatch.setattr(MySQL, "connection", MockFlaskMysqlConnection)
        mock = Mock(side_effect=[None, {"username": oldUser}])
        monkeypatch.setattr(MockFlaskMysqlCursor, "fetchone", mock)
        monkeypatch.setattr(get_user_id, "get_user_id", lambda mysql, token: (1, ""))

        response = client.post("/userChangeUsername", data=json.dumps({"current": oldUser, "new": newUser, "sessionToken": sessionToken}))
        response = response.json

        assert "success" in response
        assert response["success"]
        assert not response["hasError"]
    
    @pytest.mark.parametrize("oldUser,newUser,sessionToken", [("username", "username112312312322222222222222222222222toolong", "cbcc70c5-a45c-48e0-83df-b9714c9122a2"), ("username", "--------", "cbcc70c5-a45c-48e0-83df-b9714c9122a2"), ("username", "short", "cbcc70c5-a45c-48e0-83df-b9714c9122a2"), ("username", "__-----__$", "cbcc70c5-a45c-48e0-83df-b9714c9122a2")])
    def test_username_change_bad_username_format(self, client, oldUser, newUser, sessionToken, monkeypatch):
        # mocks connection
        monkeypatch.setattr(MySQL, "connection", MockFlaskMysqlConnection)
        mock = Mock(side_effect=[None, {"username": oldUser}])
        monkeypatch.setattr(MockFlaskMysqlCursor, "fetchone", mock)
        monkeypatch.setattr(get_user_id, "get_user_id", lambda mysql, token: (1, ""))

        response = client.post("/userChangeUsername", data=json.dumps({"current": oldUser, "new": newUser, "sessionToken": sessionToken}))
        response = response.json

        assert "success" not in response
        assert response["hasError"]

    @pytest.mark.parametrize("oldUser,newUser,sessionToken", [("username", "username1", "cbcc70c5-a45c-48e0-83df-b9714c9122a2")])
    def test_change_username_no_user_found(self, client, oldUser, newUser, sessionToken, monkeypatch):
        # mocks connection
        monkeypatch.setattr(MySQL, "connection", MockFlaskMysqlConnection)
        monkeypatch.setattr(get_user_id, "get_user_id", lambda mysql, token: (1, ""))

        response = client.post("/userChangeUsername", data=json.dumps({"current": oldUser, "new": newUser, "sessionToken": sessionToken}))
        response = response.json

        assert "success" not in response
        assert response["hasError"]
        assert response["errorMessage"].startswith("User not found")

    @pytest.mark.parametrize("oldUser,newUser,sessionToken", [("username", "username1", "cbcc70c5-a45c-48e0-83df-b9714c9122a2")])
    def test_change_username_incorrect_username(self, client, oldUser, newUser, sessionToken, monkeypatch):
        # mocks connection
        monkeypatch.setattr(MySQL, "connection", MockFlaskMysqlConnection)
        mock = Mock(side_effect=[None, {"username": oldUser + "random"}])
        monkeypatch.setattr(MockFlaskMysqlCursor, "fetchone", mock)
        monkeypatch.setattr(get_user_id, "get_user_id", lambda mysql, token: (1, ""))

        response = client.post("/userChangeUsername", data=json.dumps({"current": oldUser, "new": newUser, "sessionToken": sessionToken}))
        response = response.json

        assert "success" not in response
        assert response["hasError"]
        assert response["errorMessage"] == "Incorrect Username"

    @pytest.mark.parametrize("oldUser,newUser,sessionToken", [("username", "username1", "cbcc70c5-a45c-48e0-83df-b9714c9122a2")])
    def test_change_username_username_already_in_use(self, client, oldUser, newUser, sessionToken, monkeypatch):
        # mocks connection
        monkeypatch.setattr(MySQL, "connection", MockFlaskMysqlConnection)
        mock = Mock(side_effect=[{"username": newUser}, {"username": oldUser}])
        monkeypatch.setattr(MockFlaskMysqlCursor, "fetchone", mock)
        monkeypatch.setattr(get_user_id, "get_user_id", lambda mysql, token: (1, ""))

        response = client.post("/userChangeUsername", data=json.dumps({"current": oldUser, "new": newUser, "sessionToken": sessionToken}))
        response = response.json

        assert "success" not in response
        assert response["hasError"]
        assert response["errorMessage"].startswith("Username already in use.")

    @pytest.mark.parametrize("oldPass,newPass,sessionToken", [("password", "password2", "cbcc70c5-a45c-48e0-83df-b9714c9122a2")])
    def test_password_change_success(self, client, oldPass, newPass, sessionToken, monkeypatch):
        # mocks connection
        monkeypatch.setattr(MySQL, "connection", MockFlaskMysqlConnection)
        monkeypatch.setattr(MockFlaskMysqlCursor, "fetchone", lambda self: {"password": oldPass})
        monkeypatch.setattr(get_user_id, "get_user_id", lambda mysql, token: (1, ""))

        response = client.post("/userChangePassword", data=json.dumps({"currPass": oldPass, "newPass": newPass, "sessionToken": sessionToken}))
        response = response.json

        assert "success" in response
        assert response["success"]
        assert not response["hasError"]

    @pytest.mark.parametrize("oldPass,newPass,sessionToken", [("password", "password2", "cbcc70c5-a45c-48e0-83df-b9714c9122a2")])
    def test_change_password_no_user_found(self, client, oldPass, newPass, sessionToken, monkeypatch):
        # mocks connection
        monkeypatch.setattr(MySQL, "connection", MockFlaskMysqlConnection)
        monkeypatch.setattr(get_user_id, "get_user_id", lambda mysql, token: (1, ""))

        response = client.post("/userChangePassword", data=json.dumps({"currPass": oldPass, "newPass": newPass, "sessionToken": sessionToken}))
        response = response.json

        assert "success" not in response
        assert response["hasError"]
        assert response["errorMessage"].startswith("User not found")

    @pytest.mark.parametrize("oldPass,newPass,sessionToken", [("password", "password2", "cbcc70c5-a45c-48e0-83df-b9714c9122a2")])
    def test_change_password_incorrect_password(self, client, oldPass, newPass, sessionToken, monkeypatch):
        # mocks connection
        monkeypatch.setattr(MySQL, "connection", MockFlaskMysqlConnection)
        monkeypatch.setattr(MockFlaskMysqlCursor, "fetchone", lambda self: {"password": oldPass + "random"})
        monkeypatch.setattr(get_user_id, "get_user_id", lambda mysql, token: (1, ""))

        response = client.post("/userChangePassword", data=json.dumps({"currPass": oldPass, "newPass": newPass, "sessionToken": sessionToken}))
        response = response.json

        assert "success" not in response
        assert response["hasError"]
        assert response["errorMessage"] == "Invalid password"

    @pytest.mark.parametrize("sessionToken", [("cbcc70c5-a45c-48e0-83df-b9714c9122a2")])
    def test_delete_account_success(self, client, sessionToken, monkeypatch):
        # mocks connection
        monkeypatch.setattr(MySQL, "connection", MockFlaskMysqlConnection)
        monkeypatch.setattr(MockFlaskMysqlCursor, "fetchone", lambda self: {"sessionToken", sessionToken})
        monkeypatch.setattr(get_user_id, "get_user_id", lambda mysql, token: (1, ""))

        response = client.post("/deleteAccount", data=json.dumps({"sessionToken": sessionToken}))
        response = response.json

        assert "success" in response
        assert response["success"]
        assert not response["hasError"]

    @pytest.mark.parametrize("sessionToken", [("cbcc70c5-a45c-48e0-83df-b9714c9122a2")])
    def test_delete_account_no_user_found(self, client, sessionToken, monkeypatch):
        # mocks connection
        monkeypatch.setattr(MySQL, "connection", MockFlaskMysqlConnection)
        monkeypatch.setattr(get_user_id, "get_user_id", lambda mysql, token: (1, ""))

        response = client.post("/deleteAccount", data=json.dumps({"sessionToken": sessionToken}))
        response = response.json

        assert "success" not in response
        assert response["hasError"]
        assert response["errorMessage"].startswith("User not found")