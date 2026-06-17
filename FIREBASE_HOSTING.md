# Firebase Hosting

## Configuração para deploy

### 1. Instale o Firebase CLI

```bash
npm install -g firebase-tools
```

### 2. Faça login no Firebase

```bash
firebase login
```

### 3. Inicialize o Firebase Hosting

```bash
firebase init hosting
```

Quando asked:
- **Public directory**: `web`
- **Single-page app**: `Yes` (ou `No`, depende)
- **Dist folder**: `web`

### 4. Deploy

```bash
firebase deploy
```

## Estrutura

```
fretehub/
├── firebase.json      # Configuração do Firebase Hosting
├── web/               # Arquivos públicos (HTML, CSS, JS)
│   ├── index.html
│   ├── dashboard.html
│   ├── css/
│   └── js/
```

## URLs após deploy

- Site: `https://projetouber-24a49.web.app`
- Ou custom domain se configurado

## Observações

- O backend Django continua rodando separadamente (localhost:8000 ou deployado)
- Para produção, altere `API_BASE_URL` no `web/js/config.js` para URL do backend
