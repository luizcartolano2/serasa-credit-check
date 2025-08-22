import time

from flask import Flask, jsonify, Response, g, request
from services.serasa_service import SerasaService
from utils.logger import get_correlation_id, logger
from utils.metrics import track_metrics
from utils.rate_limiter import RateLimiter

app = Flask(__name__)
serasa_service = SerasaService()

rate_limiter = RateLimiter(limit=10, period=60)
metrics_data = {"last_request_duration": 0}


@app.before_request
def start_request():
    g.correlation_id = get_correlation_id()
    g.start_time = time.time()
    logger.info(f"Incoming request: {request.method} {request.path}")


@app.after_request
def end_request(response):
    duration = time.time() - g.start_time
    metrics_data["last_request_duration"] = duration
    return response


@app.route("/api/v1/consulta/cpf/<cpf>")
@rate_limiter.decorator
@track_metrics
def consult_cpf(cpf: str) -> Response:
    """
    Consults the Serasa mock service for a person's credit report by CPF.
    :param cpf: a string representing the CPF number, which may contain non-digit characters
    :return: a JSON response with the result of the consultation
    """
    response_data, status = serasa_service.consult_cpf(cpf)

    response = jsonify(response_data)
    response.status_code = status

    if "cached" in response_data:
        response.headers["X-Cache-Hit"] = str(response_data["cached"]).lower()

    return response


@app.route("/api/v1/consulta/cnpj/<cnpj>")
@rate_limiter.decorator
@track_metrics
def consult_cnpj(cnpj: str) -> Response:
    """
    Consults the Serasa mock service for a company's credit report by CNPJ.
    :param cnpj: a string representing the CNPJ number, which may contain non-digit characters
    :return: a JSON response with the result of the consultation
    """
    response_data, status = serasa_service.consult_cnpj(cnpj)

    response = jsonify(response_data)
    response.status_code = status

    if "cached" in response_data:
        response.headers["X-Cache-Hit"] = str(response_data["cached"]).lower()

    return response


@app.route("/metrics")
def metrics() -> Response:
    uptime = time.time() - app.config.get("START_TIME", time.time())
    return jsonify({
        "uptime": uptime,
        "last_request_duration": metrics_data["last_request_duration"]
    })


@app.route("/api/v1/health")
def health() -> tuple[Response, int]:
    """
    Health check endpoint to verify if the service is running.
    :return: a JSON response indicating the service status
    """
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
