import pytest
from app import app


@pytest.fixture
def client():
    """
    Fixture to create a test client for the Flask application.
    :return: a test client instance
    """
    app.config["TESTING"] = True
    app.config["START_TIME"] = 0
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_serasa_service(monkeypatch):
    """
    Fixture to mock the Serasa service for testing purposes.
    :param monkeypatch:  a pytest fixture for monkeypatching
    :return: a mock Serasa service
    """
    class MockSerasaService:
        """
        Mock implementation of the Serasa service for testing.
        """
        @staticmethod
        def consult_cpf(cpf):
            """
            Mock implementation of the consult_cpf method.
            :param cpf: a string representing the CPF to be consulted
            :return: a tuple containing a mock response and status code
            """
            if cpf == "00000000000":
                return {"error": "Invalid CPF."}, 400
            if cpf == "40440440400":
                return {"error": "Document not found"}, 404
            return {"success": True, "data": {"cpf": cpf}, "cached": False}, 200

        @staticmethod
        def consult_cnpj(cnpj):
            """
            Mock implementation of the consult_cnpj method.
            :param cnpj: a string representing the CNPJ to be consulted
            :return: a tuple containing a mock response and status code
            """
            if cnpj == "00000000000000":
                return {"error": "Invalid CNPJ."}, 400
            if cnpj == "40440440400000":
                return {"error": "Document not found"}, 404
            return {"success": True, "data": {"cnpj": cnpj}, "cached": False}, 200

    monkeypatch.setattr("app.serasa_service", MockSerasaService())


def test_health_endpoint(client):
    """
    Test the health check endpoint.
    :param client: a test client instance
    :return: assertions to verify the health endpoint response
    """
    resp = client.get("/api/v1/health")
    assert resp.status_code == 200
    assert resp.json == {"status": "ok"}


def test_metrics_endpoint(client):
    """
    Test the metrics endpoint.
    :param client: a test client instance
    :return: assertions to verify the metrics endpoint response
    """
    resp = client.get("/metrics")
    assert resp.status_code == 200
    assert "uptime" in resp.json
    assert "last_request_duration" in resp.json


def test_consult_cpf_success(client, mock_serasa_service):
    """
    Test the CPF consultation endpoint for a successful case.
    :param client: a test client instance
    :param mock_serasa_service: a mock Serasa service
    :return: assertions to verify the CPF consultation response
    """
    resp = client.get("/api/v1/consulta/cpf/12345678909")
    assert resp.status_code == 200
    assert resp.json["success"] is True
    assert resp.json["data"]["cpf"] == "12345678909"
    assert resp.headers.get("X-Cache-Hit") == "false"


def test_consult_cpf_invalid(client, mock_serasa_service):
    """
    Test the CPF consultation endpoint for an invalid CPF case.
    :param client: a test client instance
    :param mock_serasa_service: a mock Serasa service
    :return: assertions to verify the CPF consultation response
    """
    resp = client.get("/api/v1/consulta/cpf/00000000000")
    assert resp.status_code == 400
    assert "Invalid CPF" in resp.json["error"]


def test_consult_cpf_not_found(client, mock_serasa_service):
    """
    Test the CPF consultation endpoint for a not found case.
    :param client: a test client instance
    :param mock_serasa_service: a mock Serasa service
    :return: assertions to verify the CPF consultation response
    """
    resp = client.get("/api/v1/consulta/cpf/40440440400")
    assert resp.status_code == 404


def test_consult_cnpj_success(client, mock_serasa_service):
    """
    Test the CNPJ consultation endpoint for a successful case.
    :param client: a test client instance
    :param mock_serasa_service: a mock Serasa service
    :return: assertions to verify the CNPJ consultation response
    """
    resp = client.get("/api/v1/consulta/cnpj/12345678000195")
    assert resp.status_code == 200
    assert resp.json["success"] is True
    assert resp.json["data"]["cnpj"] == "12345678000195"
    assert resp.headers.get("X-Cache-Hit") == "false"


def test_consult_cnpj_invalid(client, mock_serasa_service):
    """
    Test the CNPJ consultation endpoint for an invalid CNPJ case.
    :param client: a test client instance
    :param mock_serasa_service: a mock Serasa service
    :return: assertions to verify the CNPJ consultation response
    """
    resp = client.get("/api/v1/consulta/cnpj/00000000000000")
    assert resp.status_code == 400
    assert "Invalid CNPJ" in resp.json["error"]


def test_consult_cnpj_not_found(client, mock_serasa_service):
    """
    Test the CNPJ consultation endpoint for a not found case.
    :param client: a test client instance
    :param mock_serasa_service: a mock Serasa service
    :return: assertions to verify the CNPJ consultation response
    """
    resp = client.get("/api/v1/consulta/cnpj/40440440400000")
    assert resp.status_code == 404
