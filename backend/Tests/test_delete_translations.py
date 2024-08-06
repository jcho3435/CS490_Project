import pytest
from Tests.Mocks.MockFlaskMysql import MockFlaskMysqlConnection, MockFlaskMysqlCursor
from flask_mysqldb import MySQL
from app import create_app
import json
from functions import get_user_id
import datetime

class TestDeleteTranslations:
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

    @pytest.mark.parametrize("sessionToken,ids", [("cbcc70c5-a45c-48e0-83df-b9714c9122a2", "all"), ("cbcc70c5-a45c-48e0-83df-b9714c9122a2", [1, 2, 3])])
    def test_delete_translation_success(self, sessionToken, ids, client, monkeypatch):
        monkeypatch.setattr(MySQL, "connection", MockFlaskMysqlConnection)
        monkeypatch.setattr(get_user_id, "get_user_id", lambda mysql, token: (1, ""))

        response = client.post("/deleteTranslations", data=json.dumps({"sessionToken": sessionToken, "ids": ids}))
        response = response.json

        assert "success" in response
        assert not response["hasError"]

    @pytest.mark.parametrize("sessionToken,ids", [("cbcc70c5-a45c-48e0-83df-b9714c9122a2", "clear"), ("cbcc70c5-a45c-48e0-83df-b9714c9122a2", 1), ("cbcc70c5-a45c-48e0-83df-b9714c9122a2", [1, 2, "3"])])
    def test_delete_translation_bad_ids_value_returns_error(self, sessionToken, ids, client, monkeypatch):
        monkeypatch.setattr(MySQL, "connection", MockFlaskMysqlConnection)
        monkeypatch.setattr(get_user_id, "get_user_id", lambda mysql, token: (1, ""))

        response = client.post("/deleteTranslations", data=json.dumps({"sessionToken": sessionToken, "ids": ids}))
        response = response.json

        assert "success" not in response
        assert response["hasError"]
        assert response["errorMessage"].startswith("Frontend error") 

    @pytest.mark.parametrize("sessionToken,ids,expectedQuery", [("cbcc70c5-a45c-48e0-83df-b9714c9122a2", "all", "DELETE FROM translation_history WHERE user_id=%s"), ("cbcc70c5-a45c-48e0-83df-b9714c9122a2", [1, 3, 5], "DELETE FROM translation_history WHERE user_id=%s AND (translation_id=%s OR translation_id=%s OR translation_id=%s)")])
    def test_delete_translation_uses_correct_query_and_errors_get_caught(self, sessionToken, ids, expectedQuery, client, monkeypatch):
        monkeypatch.setattr(MySQL, "connection", MockFlaskMysqlConnection)
        monkeypatch.setattr(get_user_id, "get_user_id", lambda mysql, token: (1, ""))
        def seeded_error(self, query, format=None):
            raise Exception(query)
        monkeypatch.setattr(MockFlaskMysqlCursor, "execute", seeded_error)

        response = client.post("/deleteTranslations", data=json.dumps({"sessionToken": sessionToken, "ids": ids}))
        response = response.json

        assert "success" not in response
        assert response["hasError"]
        assert response["errorMessage"] == expectedQuery
    
    @pytest.mark.parametrize("sessionToken,userId,error", [("cbcc70c5-a45c-48e0-83df-b9714c9122a2", -1, ""), ("cbcc70c5-a45c-48e0-83df-b9714c9122a2", 1, "Error")])
    def test_delete_translation_invalid_session_token(self, sessionToken, userId, error, client, monkeypatch):
        monkeypatch.setattr(MySQL, "connection", MockFlaskMysqlConnection)
        monkeypatch.setattr(get_user_id, "get_user_id", lambda mysql, token: (userId, error))

        response = client.post("/deleteTranslations", data=json.dumps({"sessionToken": sessionToken, "ids": [1, 2, 3]}))
        response = response.json

        assert "success" not in response
        assert response["hasError"]
        assert response["logout"]
        assert response["errorMessage"] == "[LOGIN ERROR] User is not logged in!" or response["errorMessage"] == error