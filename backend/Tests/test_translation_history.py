import pytest
from Tests.Mocks.MockFlaskMysql import MockFlaskMysqlConnection, MockFlaskMysqlCursor
from flask_mysqldb import MySQL
from app import create_app
import json
from functions import get_user_id
import datetime
from functions.cache import translation_cache

class TestTranslationHistory:
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

    @pytest.mark.parametrize("sessionToken", [("cbcc70c5-a45c-48e0-83df-b9714c9122a2")])
    def test_get_translation_history_success(self, sessionToken, client, monkeypatch):
        monkeypatch.setattr(MySQL, "connection", MockFlaskMysqlConnection)
        monkeypatch.setattr(get_user_id, "get_user_id", lambda mysql, token: (1, ""))
        retVal = ({'source_language': 'JavaScript', 'original_code': 'console.log("Hello world") //This should be placed inside a function', 'target_language': 'Python', 'translated_code': 'print("Hello world") #This should be placed inside a function', 'submission_date': datetime.datetime(2024, 4, 9, 0, 19, 26)}, {'source_language': 'Python', 'original_code': 'print("I\'m testing the translation!") #This should replace the div on the page with <p> and the content of this emssage</p>', 'target_language': 'JavaScript', 'translated_code': 'document.getElementById("divId").innerHTML = "<p>I\'m testing the translation!</p>";', 'submission_date': datetime.datetime(2024, 4, 5, 14, 31, 27)})
        monkeypatch.setattr(MockFlaskMysqlCursor, "fetchall", lambda self: retVal)

        length = len(retVal)

        response = client.post("/translationHistory", data=json.dumps({"sessionToken": sessionToken}))
        response = response.json

        assert "success" in response
        assert not response["hasError"]
        assert "rows" in response
        rows = response["rows"]
        assert length == len(rows)
        assert rows[0]['source_language'] == "JavaScript"
        assert 1 in translation_cache and translation_cache[1].history == retVal #ensures that translation_cache is functioning
        translation_cache.clear()

    @pytest.mark.parametrize("sessionToken,userId,error", [("cbcc70c5-a45c-48e0-83df-b9714c9122a2", -1, ""), ("cbcc70c5-a45c-48e0-83df-b9714c9122a2", 1, "Error")])
    def test_get_translation_history_invalid_session_token(self, sessionToken, userId, error, client, monkeypatch):
        monkeypatch.setattr(MySQL, "connection", MockFlaskMysqlConnection)
        monkeypatch.setattr(get_user_id, "get_user_id", lambda mysql, token: (userId, error))

        response = client.post("/translationHistory", data=json.dumps({"sessionToken": sessionToken}))
        response = response.json

        assert "success" not in response
        assert response["hasError"]
        assert response["logout"]
        assert response["errorMessage"] == "[LOGIN ERROR] User is not logged in!" or response["errorMessage"] == error

    @pytest.mark.parametrize("sessionToken", [("cbcc70c5-a45c-48e0-83df-b9714c9122a2")])
    def test_get_translation_history_catches_sql_error(self, sessionToken, client, monkeypatch):
        monkeypatch.setattr(MySQL, "connection", MockFlaskMysqlConnection)
        monkeypatch.setattr(get_user_id, "get_user_id", lambda mysql, token: (1, ""))
        def seeded_error(self, query, format=None):
            raise Exception("Exception")
        monkeypatch.setattr(MockFlaskMysqlCursor, "execute", seeded_error)

        response = client.post("/translationHistory", data=json.dumps({"sessionToken": sessionToken}))
        response = response.json

        assert "success" not in response
        assert response["hasError"]
        assert response["errorMessage"] == "Exception"