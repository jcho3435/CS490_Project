from functions import get_user_id
import pytest
from flask_mysqldb import MySQL
from Tests.Mocks.MockFlaskMysql import MockFlaskMysqlConnection, MockFlaskMysqlCursor
from app import create_app
import datetime
import requests
from requests import Response

# Helper functions
def create_response(code: int, reason: str) -> Response:
    response = Response()
    response.status_code = code
    response.reason = reason
    return response

class TestFunctions:
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

    def test_get_user_id(self, monkeypatch):
        monkeypatch.setattr(MySQL, "connection", MockFlaskMysqlConnection)

        #Test some unexpected error with sql query
        def seeded_error(self, query, format=None):
            raise Exception("Error in SQL query.")
        monkeypatch.setattr(MockFlaskMysqlCursor, "execute", seeded_error)
        mysql = MySQL()
        user_id, error = get_user_id.get_user_id(mysql, "some token")

        assert user_id == -1
        assert error == "Error in SQL query."

        #Test success
        monkeypatch.setattr(MockFlaskMysqlCursor, "execute", lambda self, query, format=None: None)
        monkeypatch.setattr(MockFlaskMysqlCursor, "fetchone", lambda self: {"user_id": 1, "login_date": datetime.datetime.now()})

        user_id, error = get_user_id.get_user_id(mysql, "some token")

        assert user_id == 1
        assert error == ""

    def test_api_status_baseline(self, client):
        # Test that we can hit the API without mocking
        response = client.get("/getApiStatus")
        response = response.json

        assert "code" in response and "reason" in response

    @pytest.mark.parametrize("errorType", [(requests.HTTPError), (requests.ConnectionError), (requests.Timeout), (requests.TooManyRedirects), (requests.RequestException)])
    def test_api_status_returns_response_on_error(self, errorType, client, monkeypatch):
        def seeded_error(self, url: str = None, params = None, data = None, headers = None, cookies = None, files = None, auth = None, timeout = None, allow_redirects: bool = ..., proxies = None, hooks = None):
            raise errorType(response=create_response(506, "Reason"))
        monkeypatch.setattr(requests, "get", seeded_error)

        response = client.get("/getApiStatus")
        response = response.json

        assert "code" in response and "reason" in response
        assert response["code"] == 506 and response["reason"] == "Reason"