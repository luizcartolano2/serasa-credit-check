from flask import Flask, jsonify, Response
from services.serasa_service import SerasaService

app = Flask(__name__)
serasa_service = SerasaService()


@app.route("/api/v1/consulta/cpf/<cpf>")
def consult_cpf(cpf: str) -> tuple[Response, int]:
    """
    Consults the Serasa mock service for a person's credit report by CPF.
    :param cpf: a string representing the CPF number, which may contain non-digit characters
    :return: a JSON response with the result of the consultation
    """
    response, status = serasa_service.consult_cpf(cpf)
    if "cached" in response:
        response.headers["X-Cache-Hit"] = str(response["cached"]).lower()

    return jsonify(response), status


@app.route("/api/v1/consulta/cnpj/<cnpj>")
def consult_cnpj(cnpj: str) -> tuple[Response, int]:
    """
    Consults the Serasa mock service for a company's credit report by CNPJ.
    :param cnpj: a string representing the CNPJ number, which may contain non-digit characters
    :return: a JSON response with the result of the consultation
    """
    response, status = serasa_service.consult_cnpj(cnpj)
    if "cached" in response:
        response.headers["X-Cache-Hit"] = str(response["cached"]).lower()

    return jsonify(response), status


@app.route("/api/v1/health")
def health() -> tuple[Response, int]:
    """
    Health check endpoint to verify if the service is running.
    :return: a JSON response indicating the service status
    """
    return jsonify({"status": "ok"}), 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000, debug=True)
