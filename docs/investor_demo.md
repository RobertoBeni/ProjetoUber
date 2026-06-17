# 🚀 FreteHub — Guia de Demonstração para Investidores (Versão Enxuta)

Bem-vindo ao **FreteHub**, a plataforma de logística inteligente de próxima geração que conecta embarcadores e transportadores autônomos. Este guia foi projetado para conduzir um investidor ou parceiro de negócios em uma simulação ponta a ponta do ecossistema FreteHub, destacando nossos principais diferenciais competitivos, modelo de negócios e eficiência tecnológica.

---

## 💡 A Proposta de Valor do FreteHub

O FreteHub resolve a ineficiência do transporte de cargas de médio e grande porte utilizando três pilares fundamentais:
1. **Heurísticas e Regras de Negócio de Carga**: Classificação automática de carga e recomendação instantânea do veículo ideal, prevenindo avarias e otimizando o frete.
2. **Motor de Pareamento Inteligente (Matching Engine)**: Pontuação em tempo real que avalia proximidade geográfica, conformidade documental, histórico do motorista e especificações do veículo.
3. **Telemetria e Rastreamento em Tempo Real**: Atualizações de coordenadas via Redis com recálculo dinâmico de tempo estimado de chegada (ETA) e alertas automatizados de trânsito.

---

## 🛠️ Credenciais de Demonstração (Seed Data)

Para a simulação, utilize as contas padrão criadas pelo nosso script de semente inicial (`seed_initial_data`):

| Perfil | E-mail | Senha | Descrição |
| :--- | :--- | :--- | :--- |
| **Administrador** | `admin@fretehub.com` | `AdminPassword123` | Acesso total ao painel administrativo e auditoria de logs. |
| **Cliente PF** | `pf_client@fretehub.com` | `ClientPassword123` | Usuário final / Embarcador para fretes avulsos e rápidos. |
| **Cliente PJ** | `pj_client@fretehub.com` | `ClientPassword123` | Empresa com perfil corporativo para grandes volumes. |
| **Motorista** | `driver@fretehub.com` | `DriverPassword123` | Caminhoneiro autônomo com perfil e veículo homologados. |
| **Transportadora** | `carrier@fretehub.com` | `ClientPassword123` | Gestora de frota corporativa. |
| **Suporte/Operador** | `support@fretehub.com` | `OperatorPassword123` | Operador do painel de suporte para aprovação de documentos e tickets. |

---

## 🔄 Roteiro da Demonstração (Passo a Passo)

### Passo 1: Inicialização do Sistema
Execute o script de automação no terminal para preparar o ambiente:
```powershell
./run_project_final.ps1
```
> [!NOTE]
> Este script limpa o banco de dados anterior, aplica as migrações, popula os dados de demonstração (incluindo o dashboard executivo com dados dinâmicos simulados) e roda a suíte de testes de integridade.

### Passo 2: O Dashboard Executivo (`DEMO_MODE=True`)
1. Acesse o portal administrativo em: `http://localhost:8000/admin/` (ou a rota de dashboard correspondente).
2. Autentique-se com o usuário **Administrador**.
3. Demonstre os gráficos dinâmicos de faturamento, volume de cargas por categoria, taxa de conversão do funil de vendas e distribuição geográfica de motoristas ativos.
4. Explique que o sistema roda nativamente em modo de demonstração, simulando métricas de mercado realistas para pitch decks.

### Passo 3: Criação de Solicitação de Frete Inteligente (Cliente)
1. Faça login na API ou no portal web como **Cliente PF** (`pf_client@fretehub.com`).
2. Vá para a seção de simulação e crie uma nova ordem de frete informando a categoria da carga (ex: *Geladeira Doméstica* ou *Soja a Granel*).
3. **Ponto de Destaque**: Mostre como o sistema aplica regras dinâmicas e recomenda o veículo ideal (VUC para geladeiras, Graneleiro com lona obrigatória para Soja), calculando taxas estimadas de seguro e ajudante automaticamente.

### Passo 4: Pagamento e Execução do Matching
1. Simule a confirmação do pagamento via PIX.
2. Explique o funcionamento do **Matching Engine**: o sistema busca no banco motoristas que estão online (`is_online=True`) em um raio de até 50km, aplicando penalidades caso o motorista não tenha o tipo de carroceria necessário, e ordena-os por pontuação de reputação.
3. O motorista ideal (`driver@fretehub.com`) é notificado para aceitar o frete.

### Passo 5: Rastreamento, Telemetria e Conclusão
1. Faça login como **Motorista** e simule a aceitação da ordem de frete.
2. Inicie a telemetria enviando coordenadas de GPS atualizadas de forma contínua.
3. **Ponto de Destaque**: Mostre o painel do cliente atualizando a localização geográfica no mapa em tempo real e recalculando o ETA automaticamente a cada alteração de tráfego.
4. Conclua a entrega e veja o processamento do repasse financeiro do motorista (líquido) e a taxa de serviço capturada pelo FreteHub.

---

## 🔒 Segurança e Rastreabilidade do Investimento
Toda ação executada na plataforma (de uploads de documentos confidenciais de motoristas à alteração de status de pagamentos) gera um registro inalterável de auditoria no app `audit`.
Isso garante conformidade total com a LGPD e regras financeiras rígidas (compliance), um fator crucial para rodadas de investimento série A/Semente.
