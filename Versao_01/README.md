# Uber da Logística — Sistema Inteligente de Logística

Plataforma inteligente de intermediação de fretes e gerenciamento de cargas, operando com arquitetura modular, suporte a transações em tempo real (WebSockets), agendamentos de segundo plano (Celery/Redis) e auditoria de segurança rigorosa.

---

## 🚀 Tecnologias e Stack Utilizada

- **Linguagem**: Python 3.11
- **Framework Web**: Django & Django REST Framework
- **Bancos de Dados**: PostgreSQL & PostGIS (Suporte Geográfico)
- **Cache & Mensageria**: Redis
- **Fila de Tarefas**: Celery & Celery Beat
- **Comunicação em Tempo Real**: Django Channels & Daphne ASGI
- **Autenticação**: JSON Web Tokens (SimpleJWT)
- **Containerização**: Docker & Docker Compose

---

## 📁 Estrutura de Diretórios (Módulo 1)

O projeto está organizado com uma arquitetura modular por aplicativos Django independentes:

```
e:\ProjetoUber\
├── Dockerfile                  # Empacotamento do servidor ASGI Django
├── docker-compose.yml          # Definição dos containers de serviços
├── requirements.txt            # Dependências Python
├── manage.py                   # CLI padrão do Django
├── config/                     # Configurações globais
│   ├── asgi.py                 # Protocol Type Router (Channels/ASGI)
│   ├── wsgi.py                 # Padrão síncrono WSGI
│   ├── celery.py               # Instanciação do celery worker/beat
│   ├── urls.py                 # Roteamento raiz
│   └── settings/               # Divisão de ambientes (base, development, production)
└── apps/                       # Diretório contendo os apps modulares
    ├── core/                   # Modelos base UUID, Renderers e Comandos de Semeio
    ├── accounts/               # Custom User, JWT Autenticação e Perfis de Acesso
    ├── companies/              # Perfis Corporativos (PJ) e Transportadoras
    ├── audit/                  # Registro automático de Logs de Auditoria
    └── [drivers, vehicles, cargo, freight, pricing, matching, routing, tracking, eta, payments, documents, notifications, support, ai_assistant] (Estruturas esqueléticas preparadas para os Módulos 2-5)
```

---

## 📦 Como Executar o Projeto Localmente

### 1. Preparação

Copie o arquivo de variáveis de ambiente de exemplo para criar a sua configuração local:
```bash
cp .env.example .env
```

### 2. Inicializando os Serviços com Docker Compose

Suba todos os serviços (Banco, Redis, Django, Celery Workers, Celery Beat, pgAdmin e Mailhog) com um único comando:
```bash
docker compose up --build
```

O servidor web Django/Daphne estará ouvindo na porta `8000`.

### 3. Executando Migrations do Banco de Dados

Rode as migrações dentro do container web:
```bash
docker compose exec web python manage.py migrate
```

### 4. Semeando Dados Iniciais (Seed)

Popule o banco de dados com contas de demonstração (Administrador, Cliente PF, Cliente PJ, Motorista, Transportadora, Suporte, Financeiro, Logístico):
```bash
docker compose exec web python manage.py seed_initial_data
```

As credenciais geradas no semeio são:
- **Administrador**: `admin@uberlogistica.com` | Senha: `AdminPassword123`
- **Cliente PF**: `pf_client@uberlogistica.com` | Senha: `ClientPassword123`
- **Cliente PJ**: `pj_client@uberlogistica.com` | Senha: `ClientPassword123`
- **Motorista**: `driver@uberlogistica.com` | Senha: `DriverPassword123`
- **Transportadora**: `carrier@uberlogistica.com` | Senha: `CarrierPassword123`
- **Suporte/Financeiro/Logístico**: `<perfil>@uberlogistica.com` | Senha: `OperatorPassword123`

### 5. Executando a Suíte de Testes Automatizados

Rode os testes unitários e de integração para validar a consistência cadastral e regras de segurança:
```bash
docker compose exec web python manage.py test apps.accounts.tests apps.companies.tests apps.audit.tests
```

---

## 🛡️ Lista de APIs & Endpoints (Módulo 1)

Todas as requisições e respostas de APIs seguem o padrão padronizado encapsulado:
- **Sucesso (2xx)**: `{"success": true, "data": {...}, "message": "Operação realizada com sucesso."}`
- **Erro (4xx/5xx)**: `{"success": false, "errors": {...}, "message": "Erro ao processar solicitação."}`

### Autenticação & Gestão de Usuários (Accounts)

| Método | Endpoint | Permissão | Descrição |
|---|---|---|---|
| `POST` | `/api/auth/register/` | Público | Autocadastro de Usuário (PF, PJ, DRIVER, CARRIER) |
| `POST` | `/api/auth/login/` | Público | Login de usuário, retorna tokens JWT e detalhes cadastrais |
| `POST` | `/api/auth/refresh/` | Público | Atualiza Token de Acesso usando Token de Atualização |
| `POST` | `/api/auth/logout/` | Autenticado | Efetua logout, invalidando (blacklisting) o token de atualização |
| `GET` | `/api/auth/me/` | Autenticado | Retorna detalhes cadastrais do usuário autenticado |
| `GET` | `/api/users/me/` | Autenticado | Consulta perfil detalhado do usuário atual |
| `PATCH` | `/api/users/me/` | Autenticado | Atualiza informações cadastrais do usuário atual |

### Perfis Corporativos & Transportadoras (Companies)

| Método | Endpoint | Permissão | Descrição |
|---|---|---|---|
| `POST` | `/api/companies/` | Autenticado (Apenas PJ) | Cria perfil de Pessoa Jurídica (CompanyProfile) |
| `GET` | `/api/companies/me/` | Autenticado (PJ/Admin) | Consulta perfil corporativo do usuário logado |
| `PATCH` | `/api/companies/{id}/` | Dono ou Admin | Atualiza dados do perfil de empresa do ID especificado |
| `POST` | `/api/carriers/` | Autenticado (Carrier) | Cria perfil operacional de Transportadora (CarrierCompany) |
| `GET` | `/api/carriers/me/` | Autenticado (Carrier/Admin)| Consulta dados da transportadora do usuário logado |
| `PATCH` | `/api/carriers/{id}/` | Dono ou Admin | Atualiza dados operacionais da transportadora especificada |

### Logs de Segurança e Auditoria (Audit)

| Método | Endpoint | Permissão | Descrição |
|---|---|---|---|
| `GET` | `/api/audit-logs/` | Admin ou Suporte | Lista o histórico detalhado de logs do sistema |
| `GET` | `/api/audit-logs/{id}/`| Admin ou Suporte | Consulta um registro de auditoria isolado por ID |
