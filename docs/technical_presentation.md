# 🎓 FreteHub — Apresentação Técnica para Banca Acadêmica (Trabalho Acadêmico)

Este roteiro descreve a estrutura sugerida de slides e conceitos técnicos para defender a arquitetura, segurança e engenharia de software por trás do FreteHub perante uma banca avaliadora acadêmica.

---

## Slide 1: Capa Acadêmica
* **Título**: **FreteHub** — Arquitetura Distribuidora e Pareamento Inteligente para Transporte de Carga Spot
* **Foco**: Arquitetura de Software, Algoritmos de Pareamento e Conformidade de Dados (LGPD/Segurança).
* **Autores**: *[Seu Nome]*
* **Instituição**: *[Nome da Faculdade]*

---

## Slide 2: Contexto Técnico & Arquitetural
* **Título**: Padrão de Arquitetura de Sistema
* **Descrição Visual**: Padrão MVC/MTV acoplado com arquitetura orientada a serviços e barramento assíncrono.
* **Componentes Principais**:
  - **Backend Core**: Django REST Framework (DRF) para APIs e ORM.
  - **Caching & Tempo Real**: Redis armazenando coordenadas dinâmicas e pub/sub de telemetria.
  - **Servidor Assíncrono (ASGI)**: Daphne integrado ao Django Channels para WebSockets.
  - **Banco de Dados**: PostgreSQL (Produção/Docker) & SQLite (Desenvolvimento/Testes).
  - **Barramento de Mensageria (Workers)**: Celery com Redis Broker para processar matching assíncrono pesado e envio de notificações/e-mails.

---

## Slide 3: O Diagrama de Rede (Network Architecture)
* **Título**: Arquitetura de Infraestrutura e Isolamento de Rede
* **Pontos Chave**:
  - **Isolamento de Banco de Dados**: PostgreSQL e Redis rodam em subredes privadas no Docker Compose, inacessíveis de forma direta de IPs externos.
  - **Proxy Reverso (Gateway)**: Nginx/Traefik terminando conexões SSL/TLS e encaminhando tráfego HTTP/WS para o Daphne (porta 8000).
  - **Separação de Workers**: Celery operando em contêineres separados compartilhando apenas o broker de mensagens (Redis) e as credenciais encriptadas do DB.
  - Apoio Visual: Referência ao documento local [arquitetura_de_rede.pdf](file:///e:/ProjetoUber/arquitetura_de_rede.pdf).

---

## Slide 4: Fluxo de Dados e Sequenciamento
* **Título**: Ciclo de Vida da Ordem de Frete (Sequenciamento)
* **Pontos Chave**:
  - Solicitação de Frete (Cliente) $\rightarrow$ Cálculo de Heurísticas de Compatibilidade $\rightarrow$ Cálculo Dinâmico de Preços (Fatores: peso, volume, distância, helper, seguro).
  - Confirmação de Pagamento Simulado (Webhook) $\rightarrow$ Liberação para Matching Engine $\rightarrow$ Seleção e ranqueamento de candidatos motoristas baseados em distância euclidiana/Geohash e conformidade documental.
  - Aceitação do Motorista $\rightarrow$ Envio de Telemetria Contínua (Redis) $\rightarrow$ Cálculo dinâmico de ETA (Estimativa de Chegada) $\rightarrow$ Entrega Física $\rightarrow$ Transição de Status e Auditoria de Transação.
  - Apoio Visual: Referência ao documento local [diagrama_de_sequencia.pdf](file:///e:/ProjetoUber/diagrama_de_sequencia.pdf).

---

## Slide 5: Motor de Pareamento Inteligente (Matching Engine)
* **Título**: Algoritmo de Ranqueamento de Transportadores
* **Fórmula Operacional**:
  - $Score = (Reputação \times W_r) + (Proximidade \times W_p) - Penalidades$
  - Proximidade calculada via raio geográfico.
  - Penalidades aplicadas caso o veículo do motorista não atenda exatamente aos requisitos da carga (ex: falta de lona para grãos ou falta de carroceria baú para geladeira).
  - O motorista com maior Score recebe a proposta primeiro (Despacho Sequencial Assíncrono via Celery).

---

## Slide 6: Rastreamento em Tempo Real & Telemetria
* **Título**: Arquitetura de Telemetria Híbrida (Redis + DB)
* **Pontos Chave**:
  - **Escrita Otimizada**: As atualizações de GPS enviadas pelos motoristas a cada 30 segundos são armazenadas primeiro no Redis (chave-valor rápida na memória) para não sobrecarregar o banco de dados relacional.
  - **Atualização Dinâmica do Cliente**: WebSocket notifica o cliente instantaneamente a cada nova coordenada.
  - **Recálculo de ETA**: Integração com rotas offline de fallback baseadas em velocidade média se o serviço de mapa falhar.
  - **Persistência em Lote**: Histórico de tracking gravado no PostgreSQL de forma agendada.

---

## Slide 7: Segurança da Informação & Compliance (LGPD)
* **Título**: Governança de Dados, Consentimento e Auditoria
* **Pontos Chave**:
  - **Termos de Consentimento (LGPD)**: Implementação de modelo explícito de consentimento e aceite de políticas de privacidade (`UserConsent` persistido com IP e data).
  - **Segurança de Documentos**: Envio de documentos sensíveis (CNH, CRLV) criptografados com checagem rigorosa de permissão (apenas o motorista dono e operadores de suporte com staff privileg podem ver os arquivos).
  - **Trilha de Auditoria (Audit App)**: Logs de auditoria gerados de forma automática em ações críticas (alteração de status de pagamento, criação de lead, aprovação de documentos). Esses registros contêm o usuário associado, timestamp, tipo de ação e dados modificados.

---

## Slide 8: Garantia de Qualidade & Testabilidade
* **Título**: Pirâmide de Testes e Resultados
* **Pontos Chave**:
  - **Cobertura de 100% dos Fluxos Críticos**: 13 módulos de teste cobrindo cadastro, autenticação JWT, compatibilidade de cargas, matching engine, telemetria/ETA e segurança.
  - **Total**: 52 casos de testes automatizados executando de forma integrada.
  - **Pipeline de Integração Contínua (CI)**: Script `run_project_final.ps1` simulando o pipeline de CI, destruindo banco de dados legado, criando banco limpo, semeando dados comerciais e de compliance, e validando todos os assertions em 212 segundos.
