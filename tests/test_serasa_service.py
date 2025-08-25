import pytest
import time
from unittest.mock import patch, MagicMock

from services.serasa_service import SerasaService


@pytest.fixture
def service(monkeypatch):
    """
    Fixture to create a SerasaService instance with environment variables mocked.
    :param monkeypatch: a pytest fixture for modifying environment variables
    :return: a SerasaService instance
    """
    monkeypatch.setenv("MOCK_URL", "http://mock-serasa")
    monkeypatch.setenv("SERASA_AUTH_TOKEN", "fake-token")
    return SerasaService()


def make_response(status_code=200, json_data=None):
    """
    Helper function to create a mock response object.
    :param status_code: an integer representing the HTTP status code
    :param json_data: a dictionary representing the JSON response data
    :return: a MagicMock object simulating a response
    """
    resp = MagicMock()
    resp.status_code = status_code
    resp.json.return_value = json_data or {}
    return resp


# -------------------
# __get_token
# -------------------
@patch("services.serasa_service.requests.post")
def test_get_token_success(mock_post, service):
    """
    Test successful token retrieval.
    :param mock_post: a mock for requests.post
    :param service: a SerasaService instance
    :return: assertions on token retrieval
    """
    mock_post.return_value = make_response(200, {"accessToken": "abc123", "expiresIn": 60})
    token = service._SerasaService__get_token(force=True)
    assert token == "abc123"
    assert service.token_cache["token"] == "abc123"
    assert service.token_cache["expires_at"] > time.time()


@patch("services.serasa_service.requests.post")
def test_get_token_failure(mock_post, service):
    """
    Test token retrieval failure.
    :param mock_post: a mock for requests.post
    :param service: a SerasaService instance
    :return: assertion on exception raised
    """
    mock_post.return_value = make_response(500)
    with pytest.raises(Exception, match="Error authenticating"):
        service._SerasaService__get_token(force=True)


# -------------------
# consult_cpf
# -------------------
@patch("services.serasa_service.validate_cpf", return_value=False)
def test_consult_cpf_invalid(mock_validate, service):
    """
    Test CPF validation failure.
    :param mock_validate: a mock for validate_cpf
    :param service: a SerasaService instance
    :return: assertions on error response
    """
    data, status = service.consult_cpf("invalid")
    assert status == 400
    assert "error" in data


@patch("services.serasa_service.validate_cpf", return_value=True)
def test_consult_cpf_cache_hit(mock_validate, service):
    """
    Test CPF cache hit.
    :param mock_validate: a mock for validate_cpf
    :param service: a SerasaService instance
    :return: a assertions on cached response
    """
    service.cache["12345678909"] = {"foo": "bar"}
    data, status = service.consult_cpf("12345678909")
    assert status == 200
    assert data["cached"] is True


@patch("services.serasa_service.validate_cpf", return_value=True)
@patch("services.serasa_service.SerasaService._SerasaService__request_with_retry")
def test_consult_cpf_not_found(mock_request, mock_validate, service):
    """
    Test CPF not found in Serasa service.
    :param mock_request: a mock for the request_with_retry method
    :param mock_validate: a mock for validate_cpf
    :param service: a SerasaService instance
    :return: a assertions on 404 response
    """
    mock_request.return_value = make_response(404)
    data, status = service.consult_cpf("12345678909")
    assert status == 404
    assert "error" in data


@patch("services.serasa_service.validate_cpf", return_value=True)
@patch("services.serasa_service.SerasaService._SerasaService__request_with_retry")
def test_consult_cpf_service_error(mock_request, mock_validate, service):
    """
    Test CPF service error handling.
    :param mock_request: a mock for the request_with_retry method
    :param mock_validate: a mock for validate_cpf
    :param service: a SerasaService instance
    :return: a assertions on 503 response
    """
    mock_request.return_value = make_response(500)
    data, status = service.consult_cpf("12345678909")
    assert status == 503


@patch("services.serasa_service.validate_cpf", return_value=True)
@patch("services.serasa_service.SerasaService._SerasaService__request_with_retry")
def test_consult_cpf_success(mock_request, mock_validate, service):
    """
    Test successful CPF consultation.
    :param mock_request: a mock for the request_with_retry method
    :param mock_validate: a mock for validate_cpf
    :param service: a SerasaService instance
    :return: a assertions on successful response and caching
    """
    mock_request.return_value = make_response(200, {"report": "ok"})
    data, status = service.consult_cpf("12345678909")
    assert status == 200
    assert data["cached"] is False
    assert service.cache["12345678909"] == {"report": "ok"}


# -------------------
# consult_cnpj
# -------------------
@patch("services.serasa_service.validate_cnpj", return_value=False)
def test_consult_cnpj_invalid(mock_validate, service):
    """
    Test CNPJ validation failure.
    :param mock_validate: a mock for validate_cnpj
    :param service: a SerasaService instance
    :return: an assertions on error response
    """
    data, status = service.consult_cnpj("invalid")
    assert status == 400


@patch("services.serasa_service.validate_cnpj", return_value=True)
def test_consult_cnpj_cache_hit(mock_validate, service):
    """
    Test CNPJ cache hit.
    :param mock_validate: a mock for validate_cnpj
    :param service: a SerasaService instance
    :return: an assertions on cached response
    """
    service.cache["12345678000195"] = {"foo": "bar"}
    data, status = service.consult_cnpj("12345678000195")
    assert status == 200
    assert data["cached"] is True


@patch("services.serasa_service.validate_cnpj", return_value=True)
@patch("services.serasa_service.SerasaService._SerasaService__request_with_retry")
def test_consult_cnpj_not_found(mock_request, mock_validate, service):
    """
    Test CNPJ not found in Serasa service.
    :param mock_request: a mock for the request_with_retry method
    :param mock_validate: a mock for validate_cnpj
    :param service: a SerasaService instance
    :return: an assertions on 404 response
    """
    mock_request.return_value = make_response(404)
    data, status = service.consult_cnpj("12345678000195")
    assert status == 404


@patch("services.serasa_service.validate_cnpj", return_value=True)
@patch("services.serasa_service.SerasaService._SerasaService__request_with_retry")
def test_consult_cnpj_service_error(mock_request, mock_validate, service):
    """
    Test CNPJ service error handling.
    :param mock_request: a mock for the request_with_retry method
    :param mock_validate: a mock for validate_cnpj
    :param service: a SerasaService instance
    :return: an assertions on 503 response
    """
    mock_request.return_value = make_response(500)
    data, status = service.consult_cnpj("12345678000195")
    assert status == 503


@patch("services.serasa_service.validate_cnpj", return_value=True)
@patch("services.serasa_service.SerasaService._SerasaService__request_with_retry")
def test_consult_cnpj_success(mock_request, mock_validate, service):
    """
    Test successful CNPJ consultation.
    :param mock_request: a mock for the request_with_retry method
    :param mock_validate: a mock for validate_cnpj
    :param service: a SerasaService instance
    :return: an assertions on successful response and caching
    """
    mock_request.return_value = make_response(200, {"company": "ok"})
    data, status = service.consult_cnpj("12345678000195")
    assert status == 200
    assert data["cached"] is False
    assert service.cache["12345678000195"] == {"company": "ok"}


# -------------------
# __request_with_retry
# -------------------
@patch("services.serasa_service.requests.get")
@patch("services.serasa_service.SerasaService._SerasaService__get_token", return_value="t1")
def test_request_with_retry_success(mock_get_token, mock_get, service):
    """
    Test successful request without token expiration.
    :param mock_get_token: a mock for the __get_token method
    :param mock_get: a mock for requests.get
    :param service: a SerasaService instance
    :return: an assertions on successful response
    """
    mock_get.return_value = make_response(200, {"ok": True})
    resp = service._SerasaService__request_with_retry("http://mock-serasa/x", "123")
    assert resp.status_code == 200
    mock_get_token.assert_called_once()


@patch("services.serasa_service.requests.get")
@patch("services.serasa_service.SerasaService._SerasaService__get_token", side_effect=["t1", "t2"])
def test_request_with_retry_token_expired(mock_get_token, mock_get, service):
    """
    Test request with token expiration and retry.
    :param mock_get_token: a mock for the __get_token method
    :param mock_get: a mock for requests.get
    :param service: a SerasaService instance
    :return: an assertions on successful response after retry
    """
    # First call -> 401, second call -> 200
    mock_get.side_effect = [make_response(401), make_response(200, {"ok": True})]
    resp = service._SerasaService__request_with_retry("http://mock-serasa/x", "123")
    assert resp.status_code == 200
    assert mock_get_token.call_count == 2
