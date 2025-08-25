# Projeto Serasa Mock Service

## Description
This project provides a RESTful API to query CPFs and CNPJs using a mock Serasa service. Features:
- CPF and CNPJ validation;
- Result caching to reduce repeated requests;
- JSON logging with `correlation_id`;
- Rate limiting;
- Health and metrics endpoints.

## Requirements
- Python 3.9+
- Flask
- Requests
- Cachetools
- Flasgger (Swagger docs)

## Installation
Clone the repository and install dependencies:

1. Clone the repository:
```shell
git clone https://github.com/luizcartolano2/serasa-credit-check.git
cd serasa-mock
```

2. Create and activate a virtual environment:
- Linux/Mac: `python -m venv venv` and `source venv/bin/activate`
- Windows: `python -m venv venv` and `venv\Scripts\activate`

3. Install dependencies:
```shell
pip install -r requirements.txt
```

## Configuration
Set environment variables:
```shell
- MOCK_URL=http://mock-serasa
- SERASA_AUTH_TOKEN=seu_token
- SERASA_CACHE_TTL=300  (TTL for cache)
```

## Running Locally
Run the application:
```shell
python app.py
```

API available at `http://localhost:3000`.

## Running with Docker
1. Build Docker image:
```shell
docker build -t serasa-mock .
```

2. Run the container:
```shell
docker run -d -p 3000:3000 \
  -e MOCK_URL=http://mock-serasa \
  -e SERASA_AUTH_TOKEN=your_token \
  -e SERASA_CACHE_TTL=300 \
  serasa-mock
```

API available at `http://localhost:3000`.

## Endpoints
- GET /api/v1/consulta/cpf/<cpf> – CPF lookup
- GET /api/v1/consulta/cnpj/<cnpj> – CNPJ lookup
- GET /metrics – Service metrics
- GET /api/v1/health – Health check

## Tests
Run unit and integration tests:
```shell
pytest --cov=. --cov-report=term
```