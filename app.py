import time

from flasgger import Swagger
from flask import Flask, jsonify, Response, g, request
from services.serasa_service import SerasaService
from utils.logger import get_correlation_id, logger
from utils.metrics import track_metrics
from utils.rate_limiter import RateLimiter

app = Flask(__name__)
Swagger(app)
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

    ---
    parameters:
      - name: cpf
        in: path
        type: string
        required: true
        description: CPF to query
    responses:
      200:
        description: Successful response
        headers:
          X-Cache-Hit:
            type: string
            description: Indicates if the response was served from cache
      400:
        description: Invalid CPF
      404:
        description: Document not found
      503:
        description: Error in Serasa service
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

    ---
    parameters:
      - name: cnpj
        in: path
        type: string
        required: true
        description: CNPJ to query
    responses:
      200:
        description: Successful response
        headers:
          X-Cache-Hit:
            type: string
            description: Indicates if the response was served from cache
      400:
        description: Invalid CNPJ
      404:
        description: Document not found
      503:
        description: Error in Serasa service
    """

    response_data, status = serasa_service.consult_cnpj(cnpj)

    response = jsonify(response_data)
    response.status_code = status

    if "cached" in response_data:
        response.headers["X-Cache-Hit"] = str(response_data["cached"]).lower()

    return response


@app.route("/metrics")
def metrics() -> Response:
    """
    Metrics endpoint to provide service metrics such as uptime and last request duration.
    :return: a JSON response with the service metrics

    ---
    responses:
      200:
        description: Metrics retrieved successfully
        schema:
          type: object
          properties:
            uptime:
              type: number
              description: Service uptime in seconds
            last_request_duration:
              type: number
              description: Duration of the last request in seconds
    """
    uptime = time.time() - app.config.get("START_TIME", time.time())
    return jsonify({"uptime": uptime, "last_request_duration": metrics_data["last_request_duration"]})


@app.route("/api/v1/health")
def health() -> tuple[Response, int]:
    """
    Health check endpoint to verify if the service is running.
    :return: JSON response with service status

    ---
    responses:
      200:
        description: Service is healthy
        schema:
          type: object
          properties:
            status:
              type: string
              example: ok
    """
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
