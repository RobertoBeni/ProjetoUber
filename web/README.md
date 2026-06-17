# FreteHub Web - Frontend MVP

Frontend em HTML/JS vanilla para consumo das APIs do FreteHub (Django REST).

## Stack

- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Auth**: Firebase Authentication
- **Backend API**: FreteHub Django REST (localhost:8000)

## Estrutura de Arquivos

```
web/
├── index.html        # Página de login/cadastro
├── dashboard.html    # Painel principal
├── css/
│   └── style.css     # Estilos globais
├── js/
│   ├── config.js     # Configuração Firebase + API
│   └── app.js        # Lógica da aplicação
└── assets/           # Imagens e ícones
```

## Configuração

### 1. Backend (Django)

O frontend consome a API REST do Django. Asegure-se que o backend está rodando:

```bash
# Na pasta raiz do projeto
docker compose up --build
# ou
python manage.py runserver
```

A API deve estar acessível em `http://localhost:8000/api/`

### 2. Frontend

O frontend pode ser servido de duas formas:

**Opção A: Abrir diretamente (file://)**
- Abra `web/index.html` no navegador
- Limitação: Firebase Auth funciona, mas可能会有一些问题

**Opção B: Servidor HTTP (recomendado)**
```bash
# Python 3
cd web
python -m http.server 3000

# ou Node.js
npx serve web
```

Acesse: `http://localhost:3000`

## Funcionalidades

### Autenticação
- [x] Login com e-mail/senha
- [x] Cadastro de novos usuários
- [x] Login com Google (Firebase)
- [x] Logout

### Dashboard
- [x] Estatísticas de fretes
- [x] Lista de fretes recentes
- [x] Navegação entre páginas

### Fretes
- [x] Criar novo frete
- [x] Listar fretes do usuário
- [x] Filtrar por status
- [x] Ver detalhes do frete

### Rastreamento
- [x] Buscar frete por ID
- [x] Timeline de eventos
- [ ] Mapa em tempo real (futuro)

### Perfil
- [x] Ver dados do perfil
- [x] Atualizar telefone

## API Endpoints Utilizados

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/auth/register/` | Cadastro de usuário |
| POST | `/api/auth/login/` | Login JWT |
| GET | `/api/users/me/` | Perfil do usuário |
| PATCH | `/api/users/me/` | Atualizar perfil |
| GET | `/api/freight-orders/` | Listar fretes |
| POST | `/api/freight-orders/` | Criar frete |

## Firebase Configuration

O projeto usa Firebase Authentication com as seguintes configurações (plano Spark):

```javascript
const firebaseConfig = {
    apiKey: "AIzaSyAwaKjK61ziUEipF_o_zuOQNdFyMgpy4fc",
    authDomain: "projetouber-24a49.firebaseapp.com",
    projectId: "projetouber-24a49",
    storageBucket: "projetouber-24a49.firebasestorage.app",
    messagingSenderId: "567136926588",
    appId: "1:567136926588:web:78a5dba385965f2bdf02f9",
    measurementId: "G-JG61V2G29F"
};
```

## Limitações do MVP

1. **Sem banco de dados próprio**: Todos os dados são armazenados no backend Django (PostgreSQL)
2. **Sem Storage Firebase**: Uploads de documentos vão para o backend
3. **Sem Firestore**: Dados em tempo real são gerenciados pela API REST
4. **Sem Cloud Functions**: Lógica serverless não implementada

## Próximos Passos

- [ ] Implementar busca de fretes por código
- [ ] Adicionar mapa interativo com Leaflet
- [ ] Notificações push via Firebase Cloud Messaging
- [ ] Firestore para cache local
- [ ] Progressive Web App (PWA)
