# FreteHub Firebase MVP

Plataforma de logística inteligente que conecta embarcadores, motoristas e transportadoras. Este é o **MVP (Minimum Viable Product)** rodando 100% no Firebase.

## 🚀 Visão Geral

**FreteHub** é uma plataforma para solicitação e rastreamento de fretes em tempo real, similar ao Uber, mas para transporte de cargas.

### URLs

- **Aplicação**: https://projetouber-24a49.web.app
- **Console Firebase**: https://console.firebase.google.com/project/projetouber-24a49

## 🛠️ Stack Tecnológica

| Serviço | Tecnologia |
|--------|-----------|
| Frontend | HTML5, CSS3, JavaScript (ES6+) |
| Autenticação | Firebase Authentication |
| Banco de Dados | Cloud Firestore |
| Hospedagem | Firebase Hosting |
| Notificações | SweetAlert2 (toast) |

## 📁 Estrutura de Arquivos

```
projetouber/
├── public/                      # Arquivos estáticos para Firebase Hosting
│   ├── index.html              # Página de login/cadastro
│   ├── dashboard.html          # Painel principal com tracking
│   ├── setup-admin.html        # Script para criar admin
│   ├── seed-data.html         # Script para criar dados demo
│   ├── css/
│   │   └── style.css          # Estilos globais (laranja #FF6B00)
│   └── js/
│       └── app.js              # Lógica completa (600+ linhas)
├── firebase.json               # Configuração Firebase Hosting
├── .firebaserc                 # Projeto Firebase
└── FIREBASE.md                 # Documentação
```

## ⚡ Funcionalidades Implementadas

### Autenticação
- [x] Login com e-mail/senha
- [x] Cadastro de novos usuários
- [x] Login com Google (OAuth)
- [x] Logout
- [x] Criação de admin com superpoderes

### Dashboard
- [x] Estatísticas em tempo real (total, pendentes, em trânsito, concluídos)
- [x] Lista de fretes recentes
- [x] Navegação SPA (Single Page Application)
- [x] Atualização em tempo real via Firestore

### Fretes
- [x] Criação de novo frete (origem, destino, carga)
- [x] Cálculo automático de preço
- [x] Seleção de tipo de veículo
- [x] Opções de ajudante e seguro
- [x] Lista de fretes do usuário
- [x] Filtragem por status

### Rastreamento (Estilo Uber)
- [x] Mapa visual com ícone do caminhão
- [x] Marcadores de origem e destino
- [x] Card de informações do motorista
- [x] Tempo estimado de chegada (ETA)
- [x] Distância restante
- [x] Barra de progresso de status
- [x] Simulação de movimento do motorista
- [x] Timeline de eventos

### Perfil
- [x] Visualização de dados cadastrais
- [x] Atualização de telefone
- [x] Exibição de tipo de conta

### Scripts de Setup
- [x] **setup-admin.html** - Criar usuário admin
- [x] **seed-data.html** - Popular banco com dados demo

## 💰 Cálculo de Preço

```
Preço = R$ 50,00 (tarifa base)
      + R$ 0,50 por kg
      + R$ 100,00 por m³
      + R$ 100,00 (se ajudante)
      + R$ 80,00 (se seguro)
```

## 📊 Coleções Firestore

### `users`
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

### `freights`
```json
{
  "customerId": "firebase-uid",
  "customerName": "João Silva",
  "originAddress": "Av. Paulista, 1000 - São Paulo, SP",
  "originLat": -23.5629,
  "originLng": -46.6544,
  "destinationAddress": "Av. Brasil, 2000 - Rio de Janeiro, RJ",
  "destLat": -22.9000,
  "destLng": -43.1700,
  "cargoCategory": "EQUIPMENTS",
  "cargoDescription": "Geladeira frost free 300L",
  "estimatedWeight": 80,
  "estimatedVolume": 1.5,
  "vehicleType": "BOX_TRUCK",
  "requiresHelper": false,
  "requiresInsurance": true,
  "status": "in_transit",
  "driverId": "motorista-uid",
  "driverName": "Carlos Silva",
  "driverPhone": "(11) 99999-1111",
  "estimatedPrice": 330.00,
  "createdAt": "timestamp",
  "updatedAt": "timestamp"
}
```

### `drivers`
```json
{
  "userId": "firebase-uid",
  "name": "Carlos Silva",
  "rating": 4.8,
  "vehicleType": "TRUCK",
  "vehiclePlate": "ABC-1234",
  "available": true,
  "currentLocation": { "lat": -23.5, "lng": -46.6 },
  "createdAt": "timestamp"
}
```

### `tracking`
```json
{
  "freightId": "frete-id",
  "eventType": "in_transit",
  "description": "Entrega em andamento",
  "latitude": -23.5,
  "longitude": -46.6,
  "timestamp": "timestamp"
}
```

## 🔒 Regras de Segurança Firestore

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
    match /drivers/{driverId} {
      allow read, write: if request.auth != null;
    }
    match /tracking/{trackingId} {
      allow read, write: if request.auth != null;
    }
  }
}
```

## 📑 Índices Necessários

Criar no Firebase Console > Firestore > Índices:

1. **freights** → `customerId` (asc) + `createdAt` (desc)

## 🚀 Deploy

### Firebase Hosting

```bash
# 1. Instale Firebase CLI
npm install -g firebase-tools

# 2. Login
firebase login

# 3. Deploy (projeto já configurado)
firebase deploy
```

### Scripts de Setup

Acesse via navegador:

1. **Criar Admin**: `https://projetouber-24a49.web.app/setup-admin.html`
   - Email: admin@admin.com
   - Senha: 123456

2. **Popular Dados Demo**: `https://projetouber-24a49.web.app/seed-data.html`
   - Cria 3 usuários
   - Cria 2 motoristas
   - Cria 5 fretes em diferentes status
   - Cria eventos de rastreamento

## 👥 Tipos de Usuário

| Tipo | Código | Descrição |
|------|--------|-----------|
| Cliente PF | `PF` | Pessoa física embarcadora |
| Cliente PJ | `PJ` | Pessoa jurídica embarcadora |
| Motorista | `DRIVER` | Profissional que executa fretes |
| Transportadora | `CARRIER` | Empresa de logística |
| Administrador | `ADMIN` | Gestão da plataforma |

## 🚚 Status dos Fretes

| Status | Descrição |
|--------|-----------|
| `requested` | Solicitado pelo cliente |
| `waiting_driver` | Aguardando motorista |
| `driver_found` | Motorista encontrado |
| `driver_going_to_pickup` | Motorista a caminho |
| `arrived_at_origin` | Chegou na origem |
| `cargo_collected` | Carga coletada |
| `in_transit` | Em trânsito |
| `temporarily_stopped` | Parado temporariamente |
| `near_destination` | Próximo ao destino |
| `arrived_at_destination` | Chegou ao destino |
| `delivered` | Entregue |
| `completed` | Finalizado |
| `cancelled` | Cancelado |

## 🎨 Design

- **Cor primária**: Laranja (#FF6B00)
- **Cor secundária**: Azul escuro (#1A1A2E)
- **Tipografia**: Segoe UI, sans-serif
- **Ícones**: SVG inline (Uber-style)
- **Layout**: Cards com sombras suaves

## ⚠️ Limitações do MVP

1. **Sem backend Django** - Dados apenas no Firestore
2. **Sem pagamento real** - Simulação apenas
3. **Sem matching real** - Motoristas fictícios
4. **Sem push notifications** - Toast alerts apenas
5. **Mapa simulado** - Sem Google Maps/Leaflet

## 🔮 Próximos Passos

- [ ] Mapa interativo com Leaflet/OpenStreetMap
- [ ] Notificações push via FCM
- [ ] Chat em tempo real entre cliente/motorista
- [ ] Pagamento via integração (Stripe/Asaas)
- [ ] Painel admin completo
- [ ] Matching automático motorasha/carga
- [ ] Geofencing e alertas

## 📱 Responsivo

O layout é **mobile-first** e funciona em:
- Desktop (1920px+)
- Tablet (768px - 1919px)
- Mobile (320px - 767px)

---

**FreteHub** - O hub inteligente que conecta cargas, motoristas e transportadoras.
