import pytest
from Tests.Mocks.MockFlaskMysql import MockFlaskMysqlConnection, MockFlaskMysqlCursor
from app import create_app
import json
from flask_mysqldb import MySQL
from functions import get_user_id

class TestTranslationFeedback:
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
    
    @pytest.mark.parametrize("sessionToken,translation_id,star_rating,note", [("cbcc70c5-a45c-48e0-83df-b9714c9122a2", 1, 3, 'This is a correct note!'), ("cbcc70c5-a45c-48e0-83df-b9714c9122a2", 1, 1, 'This is another correct note that is slightly longer.')])
    def test_translation_feedback_success(self, client, sessionToken, translation_id, star_rating, note, monkeypatch):
        # mock connection
        monkeypatch.setattr(MySQL, "connection", MockFlaskMysqlConnection)
        monkeypatch.setattr(get_user_id, "get_user_id", lambda mysql, token: (1, ""))

        response = client.post("/submitTranslationFeedback", data=json.dumps({"sessionToken":sessionToken, "translation_id":translation_id, "star_rating":star_rating, "note":note}))
        response = response.json

        assert response["success"]
        assert not response["hasError"]

    @pytest.mark.parametrize("sessionToken,translation_id,star_rating,note", [("cbcc70c5-a45c-48e0-83df-b9714c9122a2", 1, 0, 'This is a correct note!'), ("cbcc70c5-a45c-48e0-83df-b9714c9122a2", 3, 7, 'This is another correct note that is slightly longer.'), ("cbcc70c5-a45c-48e0-83df-b9714c9122a2", 3, 3.5, 'Correct.')])
    def test_invalid_translation_rating_value(self, client, sessionToken, translation_id, star_rating, note, monkeypatch):
        monkeypatch.setattr(MySQL, "connection", MockFlaskMysqlConnection)
        monkeypatch.setattr(get_user_id, "get_user_id", lambda mysql, token: (1, ""))

        response = client.post("/submitTranslationFeedback", data=json.dumps({"sessionToken":sessionToken, "translation_id":translation_id, "star_rating":star_rating, "note":note}))
        response = response.json

        assert response["hasError"]
        assert "success" not in response
        assert "errorMessage" in response and response["errorMessage"] == "Invalid rating value(s)"



    long_string = """
    I'd just like to interject for a moment. What you're referring to as Linux,
    is in fact, GNU/Linux, or as I've recently taken to calling it, GNU plus Linux.
    Linux is not an operating system unto itself, but rather another free component
    of a fully functioning GNU system made useful by the GNU corelibs, shell utilities
    and vital system components comprising a full OS as defined by POSIX.
    """
    @pytest.mark.parametrize("sessionToken,translation_id,star_rating,note", [("cbcc70c5-a45c-48e0-83df-b9714c9122a2", 5, 4, long_string)])
    def test_invalid_translation_note_length(self, client, sessionToken, translation_id, star_rating, note, monkeypatch):
        monkeypatch.setattr(MySQL, "connection", MockFlaskMysqlConnection)
        monkeypatch.setattr(get_user_id, "get_user_id", lambda mysql, token: (1, ""))

        response = client.post("/submitTranslationFeedback", data=json.dumps({"sessionToken":sessionToken, "translation_id":translation_id, "star_rating":star_rating, "note":note}))
        response = response.json

        assert response["hasError"]
        assert "success" not in response
        assert "errorMessage" in response and response["errorMessage"] == "Invalid note string length"

    @pytest.mark.parametrize("sessionToken,translation_id,star_rating,note", [("cbcc70c5-a45c-48e0-83df-b9714c9122a2", 3, 5, 'This is a correct note!')])
    def test_translation_feedback_database_error(self, client, sessionToken, translation_id, star_rating, note, monkeypatch):
        monkeypatch.setattr(MySQL, "connection", MockFlaskMysqlConnection)
        def seeded_error(self, insertion, format):
            raise Exception("Database connection error.")
        monkeypatch.setattr(MockFlaskMysqlCursor, "execute", seeded_error)
        monkeypatch.setattr(get_user_id, "get_user_id", lambda mysql, token: (1, ""))

        response = client.post("/submitTranslationFeedback", data=json.dumps({"sessionToken":sessionToken, "translation_id":translation_id, "star_rating":star_rating, "note":note}))
        response = response.json

        assert response["hasError"]
        assert "success" not in response
        assert "errorMessage" in response and response["errorMessage"] == "Exception: Database connection error."