# FreteHub Firebase

Frontend MVP completo rodando 100% no Firebase (Firestore + Hosting).

## Stack

- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Autenticação**: Firebase Authentication
- **Banco de Dados**: Cloud Firestore
- **Hospedagem**: Firebase Hosting

## Estrutura

```
projetouber/
├── public/                  # Arquivos para Firebase Hosting
│   ├── index.html          # Login/cadastro
│   ├── dashboard.html      # Painel principal
│   ├── css/style.css       # Estilos
│   └── js/app.js           # Lógica (Firestore direto)
├── firebase.json           # Config Firebase Hosting
├── .firebaserc             # Projeto Firebase
└── FIREBASE.md             # Este arquivo
```

## Configuração Firestore

### Regras do Firestore (dev)

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    match /freights/{freightId} {
      allow read: if request.auth != null;
      allow create: if request.auth != null;
      allow update, delete: if request.auth != null && resource.data.customerId == request.auth.uid;
    }
    match /tracking/{trackingId} {
      allow read, write: if request.auth != null;
    }
  }
}
```

### Índices

Crie os seguintes índices compostos no Firestore:
- `freights` → `customerId` (asc) + `createdAt` (desc)

## Coleções Firestore

### users
```json
{
  "name": "João Silva",
  "email": "joao@email.com",
  "phone": "(11) 99999-9999",
  "documentType": "CPF",
  "documentNumber": "12345678901",
  "userType": "PF",
  "createdAt": "timestamp",
  "updatedAt": "timestamp"
}
```

### freights
```json
{
  "customerId": "firebase-uid",
  "customerName": "João Silva",
  "originAddress": "São Paulo, SP",
  "originLat": -23.5505,
  "originLng": -46.6333,
  "destinationAddress": "Rio de Janeiro, RJ",
  "destLat": -22.9068,
  "destLng": -43.1729,
  "cargoCategory": "EQUIPMENTS",
  "cargoDescription": "Geladeira",
  "estimatedWeight": 80,
  "estimatedVolume": 1.5,
  "vehicleType": "BOX_TRUCK",
  "requiresHelper": false,
  "requiresInsurance": true,
  "status": "requested",
  "estimatedPrice": 250.00,
  "createdAt": "timestamp",
  "updatedAt": "timestamp"
}
```

### tracking
```json
{
  "freightId": "frete-id",
  "eventType": "order_created",
  "description": "Pedido criado",
  "latitude": -23.5505,
  "longitude": -46.6333,
  "timestamp": "timestamp"
}
```

## Deploy

```bash
# 1. Instale Firebase CLI
npm install -g firebase-tools

# 2. Login
firebase login

# 3. Deploy
firebase deploy
```

## Funcionalidades MVP

### Autenticação
- [x] Login com e-mail/senha
- [x] Cadastro de usuários
- [x] Login com Google
- [x] Logout

### Dashboard
- [x] Estatísticas de fretes
- [x] Lista de fretes
- [x] Navegação entre páginas

### Fretes
- [x] Criar novo frete
- [x] Listar fretes do usuário
- [x] Filtrar por status
- [x] Cálculo de preço automático
- [x] Rastreamento por código

### Perfil
- [x] Ver dados do perfil
- [x] Atualizar telefone

## Preços (Cálculo MVP)

```
Preço = 50 (base) 
      + (peso_kg × 0.50)
      + (volume_m3 × 100)
      + (100 se ajudante)
      + (80 se seguro)
```

## Limitações do MVP

1. **Sem backend Django** - Todos os dados no Firestore
2. **Sem pagamento real** - Apenas simulação
3. **Sem matching real** - Motoristas fictícios
4. **Sem push notifications** - Futuro recurso

## Próximos Passos

- [ ] Notificações push via FCM
- [ ] Mapa em tempo real
- [ ] Chat com motorista
- [ ] Pagamento via Stripe/Asaas
- [ ]后台/admin panel
