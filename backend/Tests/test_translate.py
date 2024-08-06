import pytest
from Tests.Mocks.MockFlaskMysql import MockFlaskMysqlConnection, MockFlaskMysqlCursor
import Tests.Mocks.MockGptApi as MockGpt
from app import create_app
import json
from flask_mysqldb import MySQL
from openai import resources
import datetime
from functions import get_user_id
from mock import Mock
import openai
import functions.translate_code

class TestTranslate:
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
    
    # The translated_before variable is a boolean just intended to change the behavior of the test's monkeypatch for cur.execute()
    @pytest.mark.parametrize("text,srcLang,toLang,sessionToken,translated_before", [("print('hello world!')", "Python", "Java", "cbcc70c5-a45c-48e0-83df-b9714c9122a2", False), ("print('hello world!')", "Python", "Java", "cbcc70c5-a45c-48e0-83df-b9714c9122a2", True)])
    def test_translation_success(self, client, text, srcLang, toLang, sessionToken, translated_before, monkeypatch):
        choices = [MockGpt.completion_choice_builder(
            finish_reason="stop",
            index=0,
            logprobs=None,
            content="System.out.println(\"hello world!\");",
            role="assistant",
            function_call=None,
            tool_calls=None
            )]
        
        gpt_response = MockGpt.completion_response_builder(
            choices=choices,
            id="chatcmpl-925pb878hKeuj7abfDnQmKEezr05I",
            created=1710286099,
            model="gpt-3.5-turbo-0125",
            object="chat.completion",
            system_fingerprint="fp_abcd123456",
            completion_tokens=7,
            prompt_tokens=60,
            total_tokens=67
            )
        if translated_before:
            lastSubmit = datetime.datetime(1970, 1, 1, 12, 10, 10)
            mock = Mock(side_effect=[{"submission_date": lastSubmit}, None, None, {"translation_id": 3}])
            monkeypatch.setattr(MockFlaskMysqlCursor, "fetchone", mock)
        monkeypatch.setattr(resources.chat.Completions, "create", lambda self, model, messages, max_tokens, temperature: gpt_response)
        monkeypatch.setattr(MySQL, "connection", MockFlaskMysqlConnection)
        monkeypatch.setattr(get_user_id, "get_user_id", lambda mysql, token: (1, ""))

        response = client.post("/translate", data=json.dumps({"text": text, "srcLang": srcLang, "toLang": toLang, "sessionToken": sessionToken}))
        response = response.json

        assert response["success"]
        assert not response["hasError"]
        assert "output" in response
        assert "finish_reason" in response and response["finish_reason"] == "stop"
        assert response["output"] == "System.out.println(\"hello world!\");"


    @pytest.mark.parametrize("text,srcLang,toLang,sessionToken", [("print('hello world!')", "Python", "Java", "cbcc70c5-a45c-48e0-83df-b9714c9122a2")])
    def test_database_connection_error(self, client, text, srcLang, toLang, sessionToken, monkeypatch):
        choices = [MockGpt.completion_choice_builder(
            finish_reason="stop",
            index=0,
            logprobs=None,
            content="System.out.println(\"hello world!\");",
            role="assistant",
            function_call=None,
            tool_calls=None
            )]
        
        gpt_response = MockGpt.completion_response_builder(
            choices=choices,
            id="chatcmpl-925pb878hKeuj7abfDnQmKEezr05I",
            created=1710286099,
            model="gpt-3.5-turbo-0125",
            object="chat.completion",
            system_fingerprint="fp_abcd123456",
            completion_tokens=7,
            prompt_tokens=60,
            total_tokens=67
            )
        
        monkeypatch.setattr(resources.chat.Completions, "create", lambda self, model, messages, max_tokens, temperature: gpt_response)
        monkeypatch.setattr(MySQL, "connection", MockFlaskMysqlConnection)
        monkeypatch.setattr(get_user_id, "get_user_id", lambda mysql, token: (1, ""))

        def seeded_error(self, insertion, format):
            raise Exception("Database connection error.")
        
        monkeypatch.setattr(MockFlaskMysqlCursor, "execute", seeded_error)

        response = client.post("/translate", data=json.dumps({"text": text, "srcLang": srcLang, "toLang": toLang, "sessionToken": sessionToken}))
        response = response.json

        assert response["hasError"]
        assert "success" not in response
        assert "errorMessage" in response and response["errorMessage"] == "Database connection error."


    @pytest.mark.parametrize("text,srcLang,toLang,sessionToken", [("print('hello world!')", "Python", "Java", "cbcc70c5-a45c-48e0-83df-b9714c9122a2")])
    def test_api_connection_error(self, client, text, srcLang, toLang, sessionToken, monkeypatch):
        def seeded_error(self, model, messages, max_tokens, temperature):
            raise openai.APIConnectionError(message="GPT API connection error.", request=None)
        
        monkeypatch.setattr(resources.chat.Completions, "create", seeded_error)
        monkeypatch.setattr(functions.translate_code, "db_log_translation_errors", lambda self, translation_id, eMessage, eCode = None, etype = None: None)
        monkeypatch.setattr(MySQL, "connection", MockFlaskMysqlConnection)
        monkeypatch.setattr(get_user_id, "get_user_id", lambda mysql, token: (1, ""))
        

        response = client.post("/translate", data=json.dumps({"text": text, "srcLang": srcLang, "toLang": toLang, "sessionToken": sessionToken}))
        response = response.json

        assert response["hasError"]
        assert "success" not in response
        assert "apiErrorMessage" in response and response["apiErrorMessage"] == "GPT API connection error."

    @pytest.mark.parametrize("text,srcLang,toLang,sessionToken", [("print('hello world!')", "Python", "Java", "cbcc70c5-a45c-48e0-83df-b9714c9122a2")])
    def test_translation_rate_limit(self, client, text, srcLang, toLang, sessionToken, monkeypatch):
        choices = [MockGpt.completion_choice_builder(
            finish_reason="stop",
            index=0,
            logprobs=None,
            content="System.out.println(\"hello world!\");",
            role="assistant",
            function_call=None,
            tool_calls=None
            )]
        
        gpt_response = MockGpt.completion_response_builder(
            choices=choices,
            id="chatcmpl-925pb878hKeuj7abfDnQmKEezr05I",
            created=1710286099,
            model="gpt-3.5-turbo-0125",
            object="chat.completion",
            system_fingerprint="fp_abcd123456",
            completion_tokens=7,
            prompt_tokens=60,
            total_tokens=67
            )
    
        lastSubmit = datetime.datetime.now() - datetime.timedelta(seconds=1)
        monkeypatch.setattr(MockFlaskMysqlCursor, "fetchone", lambda self: {"submission_date": lastSubmit})
        monkeypatch.setattr(get_user_id, "get_user_id", lambda mysql, token: (1, ""))

        monkeypatch.setattr(resources.chat.Completions, "create", lambda self, model, messages, max_tokens, temperature: gpt_response)
        monkeypatch.setattr(MySQL, "connection", MockFlaskMysqlConnection)

        response = client.post("/translate", data=json.dumps({"text": text, "srcLang": srcLang, "toLang": toLang, "sessionToken": sessionToken}))
        response = response.json

        assert "success" not in response
        assert response["hasError"]
        assert "output" not in response
        assert response["errorMessage"].startswith("Rate limited:")