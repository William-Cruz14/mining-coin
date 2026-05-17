# HashPilot

Automação de mineração de criptomoedas que seleciona automaticamente a moeda mais lucrativa para minerar com base no hardware da máquina.

## Como funciona

A cada 2 horas o script:

1. Coleta benchmarks reais da API do XMRig filtrando por CPU, SO e data
2. Calcula o hashrate mediano e o consumo de energia da máquina
3. Consulta a API do WhatToMine para estimar o lucro de cada moeda
4. Escolhe a moeda com maior lucro nas últimas 24h entre as suportadas
5. Inicia o XMRig com os parâmetros otimizados e envia notificação via Discord e e-mail

## Moedas suportadas

| Moeda | Algoritmo | Pool |
|-------|-----------|------|
| XMR   | rx/0      | HeroMiners |
| ZEPH  | rx/0      | HeroMiners |
| QRL   | rx/0      | HeroMiners |

## Pré-requisitos

- Python >= 3.14
- Poetry
- XMRig (baixado automaticamente pelo script)

## Instalação (Requer instalação do pipx, em seguida o poetry)

```bash
poetry install
```
```bash
playwright install
```

Configure o arquivo `.env` na raiz do projeto:

```env
WHAT_TO_MINE_URL=
WHAT_TO_MINE_API=
WALLET_XMR=
WALLET_ZEPH=
WALLET_QRL=
DISCORD_WEBHOOK_URL=
```

## Uso

```bash
poetry run python src/main.py
```

O XMRig será baixado automaticamente na primeira execução caso não esteja presente.

## Tarefas disponíveis

```bash
poe install   # instala dependências
poe lint      # checa o código com Ruff
poe fmt       # formata o código
poe fmt-fix   # mostra diff de formatação sem aplicar
poe test      # executa os testes
poe ci        # lint + fmt + test
```

## Estrutura

```
src/
├── main.py                  # entrypoint
├── orchestrator_miner.py    # lógica de seleção e inicialização
├── benchmark_provider.py    # busca benchmarks na API do XMRig
├── benchmark_selector.py    # calcula hashrate, threads e potência
├── whattomine_provider.py   # consulta lucratividade via WhatToMine
├── xmrig.py                 # download, start e stop do minerador
├── coins.py                 # enum com as moedas suportadas
├── machine_attributes.py    # informações de hardware da máquina
└── power_cpu.py             # banco de dados de consumo por CPU
```
