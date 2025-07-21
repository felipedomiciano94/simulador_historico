# simulador_historico
===========================================
📘 DOCUMENTAÇÃO DO PROJETO
Simulador Histórico de Demandas - DataLake
===========================================

🔍 Descrição Geral
-------------------
Este projeto consiste em uma aplicação interativa desenvolvida com Streamlit para análise retroativa de viagens logísticas. A ferramenta permite que analistas e gestores avaliem se as modalidades de transporte utilizadas (Frota Própria, Agregado, Terceiro) foram as mais econômicas, com base em uma tabela de custos consolidada.

A análise é feita a partir de dados históricos exportados do DataLake da empresa, e o sistema compara automaticamente o custo real da viagem com o custo ideal (melhor opção) e calcula o saving potencial.

🎯 Objetivos
-------------
- Automatizar a análise de alocação de modais logísticos;
- Identificar decisões ineficientes na alocação de Frota vs. Agregado;
- Apoiar estratégias de redução de custos com base em dados históricos;
- Gerar relatórios com indicadores e gráficos que facilitam a tomada de decisão.

🧱 Estrutura Esperada da Base de Dados
---------------------------------------
1. **Base Histórica (Excel - simulador_datalake.xlsx)**

| Coluna               | Descrição                             |
|----------------------|----------------------------------------|
| SOLICITACAO_CARGA_ID | Identificador único da viagem          |
| DATA_CARGA           | Data da operação                       |
| MODALIDADE           | Modalidade utilizada (FROTA, AGREGADO, TERCEIRO) |
| ORIGEM E UF          | Local de origem padronizado            |
| DESTINO E UF         | Local de destino padronizado           |

2. **Base de Custos Consolidados (CSV - custos_consolidados.csv)**

| Coluna         | Descrição                          |
|----------------|-------------------------------------|
| ORIGEM         | Cidade/UF de origem                |
| DESTINO        | Cidade/UF de destino               |
| CUSTO_FROTA    | Custo com frota própria            |
| CUSTO_AGREGADO | Custo com agregado                 |

🛠 Funcionalidades do Simulador
-------------------------------
- Upload de arquivos históricos;
- Cálculo do melhor modal por rota;
- Comparação com a modalidade realizada;
- Cálculo automático do saving potencial;
- Tabela com dados detalhados;
- Painel de resumo com:
  - Total de viagens por tipo;
  - Custo realizado vs. custo otimizado;
  - Tabela mensal por modalidade;
  - Gráfico com linha do tempo do saving.

📦 Requisitos
-------------
- Python 3.8+
- streamlit
- pandas
- openpyxl
- unidecode
- matplotlib

▶️ Execução
------------
1. Instale os pacotes:

   pip install -r requirements_simulador_datalake.txt

2. Execute o sistema com:

   streamlit run simulador_datalake_resumo_grafico_corrigido.py

3. Faça o upload dos arquivos solicitados via interface.

📈 Resultado Esperado
----------------------
- Visão clara dos custos realizados vs. custos ideais;
- Identificação de oportunidades de economia;
- Análise mensal consolidada por tipo de transporte;
- Apoio direto à estratégia logística e ao planejamento operacional.

📬 Contato
-----------
Projeto desenvolvido pela área de Inovação da Movecta.

Simulador Histórico de programação
