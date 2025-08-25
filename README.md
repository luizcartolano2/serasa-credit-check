# Projeto Serasa Mock Service

## Descrição
Este projeto fornece uma API RESTful para consultar CPFs e CNPJs utilizando um serviço mock da Serasa. Inclui:
- Consulta de CPF e CNPJ com validação;
- Cache de resultados para reduzir chamadas repetidas;
- Logs em formato JSON com `correlation_id`;
- Limite de requisições (rate limiter);
- Endpoints de saúde e métricas.

## Requisitos
- Python 3.9+
- Flask
- Requests
- Cachetools
- Flasgger (para documentação Swagger)

## Instalação
Clone o repositório e instale as dependências:

1. Clonar o repositório:
   ```shell
    git clone https://github.com/luizcartolano2/serasa-credit-check.git
    cd serasa-mock
    ```
2. Criar e ativar o ambiente virtual:
   - Linux/Mac: `python -m venv venv` e `source venv/bin/activate`
   - Windows: `python -m venv venv` e `venv\Scripts\activate`

3. Instalar as dependências:
```shell
pip install -r requirements.txt
```

## Configuração
Defina as variáveis de ambiente:
```shell
- MOCK_URL=http://mock-serasa
- SERASA_AUTH_TOKEN=seu_token
- SERASA_CACHE_TTL=300  (TTL da cache em segundos)
```

## Executando Localmente
Rode a aplicação com:
```shell
python app.py
```

A API estará disponível em `http://localhost:3000`.

## Executando com Docker
1. Build da imagem Docker:
```shell
docker build -t serasa-mock .
```
2. Rodando o container:
```shell
docker run -d -p 3000:3000 \
  -e MOCK_URL=http://mock-serasa \
  -e SERASA_AUTH_TOKEN=seu_token \
  -e SERASA_CACHE_TTL=300 \
  serasa-mock
```

A API estará disponível em `http://localhost:3000`.

## Endpoints
- GET /api/v1/consulta/cpf/<cpf> – Consulta de CPF
- GET /api/v1/consulta/cnpj/<cnpj> – Consulta de CNPJ
- GET /metrics – Métricas do serviço
- GET /api/v1/health – Health check

## Testes
Rode os testes unitários e de integração:
```shell
pytest --cov=. --cov-report=term
```

