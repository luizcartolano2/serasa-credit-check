# Mock Serasa Server

Servidor mock modernizado para simular a API Serasa com TypeScript e melhores práticas.

## Recursos

- ✅ TypeScript com tipagem completa
- ✅ Arquitetura modular e escalável
- ✅ Docker e Docker Compose
- ✅ Autenticação JWT segura
- ✅ Logging estruturado com Winston
- ✅ Validação de requisições com Joi
- ✅ Testes unitários com Jest
- ✅ Middlewares de segurança (Helmet, CORS)
- ✅ Compressão de respostas
- ✅ Health check endpoint
- ✅ Limpeza automática de tokens expirados

## Pré-requisitos

- Node.js 20+ (para desenvolvimento)
- Docker e Docker Compose (para produção)
- Arquivos `payload-pf.json` e `payload-pj.json` no diretório raiz

## Instalação

### Desenvolvimento

```bash
# Instalar dependências
npm install

# Copiar arquivo de configuração
cp .env.example .env

# Executar em modo desenvolvimento
npm run dev
```

### Produção com Docker

```bash
# Construir e executar com Docker Compose
docker-compose up -d

# Ver logs
docker-compose logs -f

# Parar servidor
docker-compose down
```

## Scripts Disponíveis

- `npm run dev` - Executa em modo desenvolvimento com hot reload
- `npm run build` - Compila TypeScript para JavaScript
- `npm start` - Executa servidor compilado
- `npm test` - Executa testes unitários
- `npm run test:coverage` - Executa testes com cobertura
- `npm run lint` - Verifica código com ESLint
- `npm run typecheck` - Verifica tipos TypeScript

## Endpoints

### Autenticação
```
POST /security/iam/v1/client-identities/login
Headers: Authorization: Basic <base64>
```

### Relatório PF
```
GET /credit-services/person-information-report/v1/creditreport?reportName=RELATORIO_BASICO_PF_PME
Headers: 
  - Authorization: Bearer <token>
  - X-Document-id: <cpf>
```

### Relatório PJ
```
GET /credit-services/business-information-report/v1/reports?reportName=RELATORIO_BASICO_PJ_PME
Headers:
  - Authorization: Bearer <token>
  - X-Document-id: <cnpj>
```

### Health Check
```
GET /health
```

## Variáveis de Ambiente

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| PORT | Porta do servidor | 3006 |
| NODE_ENV | Ambiente (development/production) | development |
| JWT_SECRET | Chave secreta para JWT | - |
| TOKEN_EXPIRY | Tempo de expiração do token (segundos) | 3600 |
| RATE_LIMIT_WINDOW_MS | Janela para rate limiting (ms) | 900000 |
| RATE_LIMIT_MAX_REQUESTS | Máximo de requisições por janela | 100 |
| LOG_LEVEL | Nível de log | info |
| MIN_DELAY | Delay mínimo de resposta (ms) | 2000 |
| MAX_DELAY | Delay máximo de resposta (ms) | 60000 |

## Estrutura do Projeto

```
.
├── src/
│   ├── config/          # Configurações
│   ├── controllers/     # Controladores
│   ├── middleware/      # Middlewares
│   ├── routes/          # Rotas
│   ├── services/        # Serviços de negócio
│   ├── types/           # Tipos TypeScript
│   ├── utils/           # Utilitários
│   └── index.ts         # Entry point
├── Dockerfile           # Imagem Docker
├── docker-compose.yml   # Orquestração Docker
├── package.json         # Dependências
├── tsconfig.json        # Configuração TypeScript
└── jest.config.js       # Configuração Jest
```

## Segurança

- Tokens JWT com HMAC SHA-256
- Rate limiting para prevenir abuso
- Helmet para headers de segurança
- Validação de entrada com Joi
- Usuário não-root no Docker
- Secrets através de variáveis de ambiente

## Monitoramento

- Health check endpoint com status dos payloads
- Logging estruturado com níveis configuráveis
- Contagem de tokens ativos
- Métricas de tempo de resposta nos logs