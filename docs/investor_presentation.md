# 📊 FreteHub — Slide Deck para Investidores (Pitch Deck)

Este documento descreve a estrutura sugerida de slides e narrativa para a apresentação ao investidor. Você pode usar este roteiro para montar sua apresentação de slides (ex: PowerPoint, Google Slides ou Canva).

---

## Slide 1: A Capa
* **Título**: **FreteHub** — Logística Inteligente Sob Demanda
* **Subtítulo**: Conectando embarcadores e transportadores autônomos por meio de tecnologia e inteligência geográfica.
* **Apoio Visual**: Logotipo do FreteHub e imagens modernas de caminhões em rodovias (visual premium escuro).

---

## Slide 2: O Problema
* **Título**: O Gargalo do Transporte Rodoviário no Brasil
* **Pontos Chave**:
  - **Inabilidade no Matching**: Embarcadores levam horas ou dias para encontrar o veículo adequado e disponível.
  - **Avarias e Desperdício**: Falha na compatibilidade de cargas e veículos (ex: carregar soja em caçamba inadequada ou geladeira deitada).
  - **Falta de Visibilidade**: Rastreamento precário das cargas em trânsito e ETAs (estimativa de chegada) imprecisas.
  - **Falta de Segurança e Compliance**: Alto risco de fraudes documentais e falta de trilhas de auditoria.

---

## Slide 3: A Solução (FreteHub)
* **Título**: O Ecossistema Logístico FreteHub
* **Pontos Chave**:
  - **Pareamento Instantâneo (Matching Engine)**: Algoritmo proprietário que pontua e seleciona o motorista ideal em segundos.
  - **Heurísticas Inteligentes**: Validação de compatibilidade física da carga com o veículo na origem.
  - **Telemetria de Ponta**: Rastreamento geográfico contínuo com recálculo de ETA em tempo real alimentado por Redis.
  - **Compliance Nativo**: Backoffice completo para checagem documental e logs de auditoria imutáveis.

---

## Slide 4: O Produto / Demonstração
* **Título**: Demonstração em Tempo Real (Live Demo)
* **Pontos Chave**:
  - *[Mostrar a interface do FreteHub em execução local]*
  - Demonstração prática do **Embarcador** criando uma ordem de frete de *Geladeira Doméstica*.
  - Demonstração do **Motorista** aceitando o frete e atualizando a localização geolocalizada.
  - O painel executivo dinâmico (`DEMO_MODE=True`) atualizando em tempo real com estatísticas de GMV e taxas de serviço.

---

## Slide 5: Tamanho de Mercado (TAM, SAM, SOM)
* **Título**: Mercado de Logística e Fretes no Brasil
* **Pontos Chave**:
  - **TAM (Mercado Total)**: R$ 350 Bilhões (Setor de transporte rodoviário de cargas no Brasil).
  - **SAM (Mercado Endereçável)**: R$ 45 Bilhões (Fretes autônomos e spot digitalizáveis).
  - **SOM (Mercado Focado)**: R$ 900 Milhões (Nossa meta de captura nos primeiros 3 anos em rotas estratégicas do agro e eletrodomésticos).

---

## Slide 6: Modelo de Negócios (Business Model)
* **Título**: Como Monetizamos?
* **Pontos Chave**:
  - **Take-rate de 15%**: Cobramos uma taxa de serviço sobre o valor bruto de cada frete intermediado.
  - **Unidades Econômicas (Exemplo de R$ 1.000 de frete)**:
    - R$ 850 repassados diretamente ao motorista autônomo.
    - R$ 150 retidos pelo FreteHub (R$ 120 margem de contribuição, R$ 30 impostos e custos transacionais).
  - **Modelo SaaS Corporativo (Futuro)**: Assinatura mensal para grandes transportadoras gerenciarem suas frotas próprias no nosso ecossistema.

---

## Slide 7: Tração e Métricas Atuais (Demo Metrics)
* **Título**: Indicadores de Performance Operacional
* **Pontos Chave**:
  - **GMV Transacionado (Simulado)**: R$ 450.000 no último trimestre.
  - **Motoristas Cadastrados**: +1.200 caminhoneiros homologados.
  - **Taxa de Conclusão**: 97.8% de entregas realizadas com sucesso no prazo.
  - **Tempo Médio de Matching**: Menos de 4 minutos para aceite da carga.

---

## Slide 8: O Plano de Expansão (A Oportunidade)
* **Título**: Rodada de Investimento Seed (R$ 2.000.000)
* **Destinação dos Recursos**:
  - **60% Produto & Engenharia**: Escalabilidade da infraestrutura de rede, IA preditiva para match de rotas e apps móveis nativos.
  - **30% Comercial & Marketing**: Aquisição e incentivo de motoristas nas principais rotas agro-industriais.
  - **10% Operações & Jurídico**: Compliance, suporte técnico 24/7 e seguros de carga.
* **Contato**: `investidores@fretehub.com` | `www.fretehub.com`
