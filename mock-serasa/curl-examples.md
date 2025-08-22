# Exemplos de cURL - Mock Serasa Server

## 1. Health Check (Não requer autenticação)
```bash
curl -X GET "http://localhost:3006/health"
```

## 2. Login - Obter Token
```bash
# Criar credenciais Base64
CREDENTIALS=$(echo -n "usuario:senha" | base64)

# Fazer login
curl -X POST "http://localhost:3006/security/iam/v1/client-identities/login" \
  -H "Authorization: Basic $CREDENTIALS" \
  -H "Content-Type: application/json"
```

Resposta esperada:
```json
{
  "accessToken": "eyJwYXlsb2FkIjp7ImNsaWVudElkIj...",
  "tokenType": "Bearer",
  "expiresIn": "3600",
  "scope": ["read", "write"]
}
```

## 3. Consultar Relatório PF (CPF)
```bash
# Usar o token obtido no login
TOKEN="seu_token_aqui"

curl -X GET "http://localhost:3006/credit-services/person-information-report/v1/creditreport?reportName=RELATORIO_BASICO_PF_PME" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Document-id: 12345678901" \
  -H "Content-Type: application/json"
```

## 4. Consultar Relatório PJ (CNPJ)
```bash
# Usar o token obtido no login
TOKEN="seu_token_aqui"

curl -X GET "http://localhost:3006/credit-services/business-information-report/v1/reports?reportName=RELATORIO_BASICO_PJ_PME" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Document-id: 12345678000195" \
  -H "Content-Type: application/json"
```

## 5. Teste Completo em Uma Linha

### Login e salvar token em variável:
```bash
TOKEN=$(curl -s -X POST "http://localhost:3006/security/iam/v1/client-identities/login" \
  -H "Authorization: Basic $(echo -n 'test:test' | base64)" \
  -H "Content-Type: application/json" | jq -r '.accessToken')
```

### Usar o token para consultar CPF:
```bash
curl -X GET "http://localhost:3006/credit-services/person-information-report/v1/creditreport?reportName=RELATORIO_BASICO_PF_PME" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Document-id: 12345678901" | jq '.'
```

## 6. Testar Rate Limiting

### Fazer múltiplas requisições rapidamente:
```bash
# Fazer 10 requisições em sequência
for i in {1..10}; do
  curl -s -o /dev/null -w "Request $i: HTTP %{http_code}\n" \
    -X GET "http://localhost:3006/health"
done
```

### Verificar se foi bloqueado (HTTP 429):
```bash
curl -v -X GET "http://localhost:3006/health" 2>&1 | grep "< HTTP"
```

## 7. Testar Erros

### Token inválido (deve retornar 401):
```bash
curl -X GET "http://localhost:3006/credit-services/person-information-report/v1/creditreport?reportName=RELATORIO_BASICO_PF_PME" \
  -H "Authorization: Bearer token_invalido" \
  -H "X-Document-id: 12345678901"
```

### Sem header X-Document-id (deve retornar 400):
```bash
curl -X GET "http://localhost:3006/credit-services/person-information-report/v1/creditreport?reportName=RELATORIO_BASICO_PF_PME" \
  -H "Authorization: Bearer $TOKEN"
```

### Report name inválido (deve retornar 400):
```bash
curl -X GET "http://localhost:3006/credit-services/person-information-report/v1/creditreport?reportName=INVALIDO" \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-Document-id: 12345678901"
```

## 8. Comandos Úteis

### Ver apenas o código HTTP da resposta:
```bash
curl -s -o /dev/null -w "%{http_code}\n" -X GET "http://localhost:3006/health"
```

### Ver headers da resposta:
```bash
curl -I -X GET "http://localhost:3006/health"
```

### Salvar resposta em arquivo:
```bash
curl -X GET "http://localhost:3006/health" -o response.json
```

### Ver tempo de resposta:
```bash
curl -w "\nTempo total: %{time_total}s\n" -X GET "http://localhost:3006/health"
```

## Scripts de Teste Disponíveis

- `./test-curls.sh` - Testa todos os endpoints com vários cenários
- `./test-rate-limit.sh` - Testa especificamente o rate limiting
- `./test-rate-limit-concurrent.sh` - Testa rate limiting com requisições paralelas

Execute com:
```bash
chmod +x *.sh
./test-curls.sh
```