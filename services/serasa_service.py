import os
import time
from typing import Optional

import requests
from cachetools import TTLCache

from services.validation import validate_cpf, validate_cnpj
from utils.logger import logger


class SerasaService:
    """
    Service class for interacting with the Serasa mock service.
    This class provides methods to authenticate, consult CPF and CNPJ, and cache results.

    Attributes:
        mock_url (str): The base URL of the Serasa mock service.
        auth_header (dict): The authorization header for API requests.
        token_cache (dict): Cache for the access token and its expiration time.
        cache (TTLCache): Cache for storing consultation results with a time-to-live.
    Methods:
        __get_token() -> Optional[str]:
            Authenticates with the mock Serasa service to retrieve an access token.
        consult_cpf(cpf: str) -> [dict, int]:
            Consults the Serasa mock service for a person's credit report by CPF.
        consult_cnpj(cnpj: str) -> [dict, int]:
            Consults the Serasa mock service for a company's credit report by CNPJ.
    """

    def __init__(self):
        self.mock_url = os.getenv("MOCK_URL")
        self.auth_header = {"Authorization": f"Basic {os.getenv('SERASA_AUTH_TOKEN')}"}
        self.token_cache = {"token": None, "expires_at": 0}
        self.cache = TTLCache(maxsize=100, ttl=int(os.getenv("SERASA_CACHE_TTL", 300)))

    def __get_token(self, force=False) -> Optional[str]:
        """
        Authenticates with the mock Serasa service to retrieve an access token.
        :param force: a boolean indicating whether to force re-authentication
        :return: a string representing the access token
        """
        if not force and self.token_cache["token"] and self.token_cache["expires_at"] > time.time():
            return self.token_cache["token"]

        resp = requests.post(
            f"{self.mock_url}/security/iam/v1/client-identities/login",
            headers=self.auth_header,
        )
        if resp.status_code != 200:
            raise Exception("Error authenticating with Serasa mock service")

        data = resp.json()
        token = data.get("accessToken")
        expires_in = data.get("expiresIn", 60)
        if isinstance(expires_in, str):
            expires_in = int(expires_in)

        self.token_cache["token"] = token
        self.token_cache["expires_at"] = time.time() + expires_in - 5

        logger.info({
            "event": "auth_success",
            "token_set": True,
            "expires_at": self.token_cache["expires_at"]
        })

        return token

    def __request_with_retry(self, url: str, document_id: str) -> requests.Response:
        """
        Makes a GET request to the specified URL with retries on failure.
        :param url: a string representing the URL to request
        :param document_id: a string representing the document ID (CPF or CNPJ)
        :return: a requests.Response object
        """
        logger.info({"event": "request_start", "document_id": document_id, "url": url})

        token = self.__get_token()
        headers = {"Authorization": f"Bearer {token}", "X-Document-Id": document_id}
        resp = requests.get(url, headers=headers)

        if resp.status_code == 401:
            logger.warning({"event": "token_expired", "message": "Retrying request with new token"})

            token = self.__get_token(force=True)
            headers["Authorization"] = f"Bearer {token}"
            resp = requests.get(url, headers=headers)

        logger.info({
            "event": "request_end",
            "document_id": document_id,
            "status_code": resp.status_code
        })

        return resp

    def consult_cpf(self, cpf: str) -> [dict, int]:
        """
        Consults the Serasa mock service for a person's credit report by CPF.
        :param cpf: a string representing the CPF number, which may contain non-digit characters
        :return: a dictionary with the result of the consultation
        """
        logger.info({"event": "validate_cpf", "cpf": cpf})

        if not validate_cpf(cpf):
            logger.error({"event": "invalid_cpf", "cpf": cpf})
            return {"error": "Invalid CPF."}, 400

        if cpf in self.cache:
            logger.info({"event": "cache_hit", "document_id": cpf})
            return {"success": True, "data": self.cache[cpf], "cached": True}, 200

        logger.info({"event": "auth_request", "message": "Requesting new token"})
        resp = self.__request_with_retry(
            f"{self.mock_url}/credit-services/person-information-report/v1/creditreport?reportName=RELATORIO_BASICO_PF_PME",
            cpf,
        )

        if resp.status_code == 404:
            logger.error({"event": "document_not_found", "document_id": cpf})
            return {"error": "Document not found"}, 404
        if resp.status_code != 200:
            logger.error({"event": "service_error", "status_code": resp.status_code})
            return {"error": "Error in Serasa service. Please try again later."}, 503

        data = resp.json()
        self.cache[cpf] = data

        logger.info({"event": "consult_success", "document_id": cpf})
        return {"success": True, "data": data, "cached": False}, 200

    def consult_cnpj(self, cnpj: str) -> [dict, int]:
        """
        Consults the Serasa mock service for a company's credit report by CNPJ.
        :param cnpj: a string representing the CNPJ number, which may contain non-digit characters
        :return: a dictionary with the result of the consultation
        """
        logger.info({"event": "validate_cnpj", "cnpj": cnpj})
        if not validate_cnpj(cnpj):
            logger.error({"event": "invalid_cnpj", "cnpj": cnpj})
            return {"error": "Invalid CNPJ."}, 400

        if cnpj in self.cache:
            logger.info({"event": "cache_hit", "document_id": cnpj})
            return {"success": True, "data": self.cache[cnpj], "cached": True}, 200

        resp = self.__request_with_retry(
            f"{self.mock_url}/credit-services/business-information-report/v1/reports?reportName=RELATORIO_BASICO_PJ_PME",
            cnpj,
        )

        if resp.status_code == 404:
            logger.error({"event": "document_not_found", "document_id": cnpj})
            return {"error": "Document not found"}, 404
        if resp.status_code != 200:
            logger.error({"event": "service_error", "status_code": resp.status_code})
            return {"error": "Error in Serasa service. Please try again later."}, 503

        data = resp.json()
        self.cache[cnpj] = data
        logger.info({"event": "consult_success", "document_id": cnpj})
        return {"success": True, "data": data, "cached": False}, 200
