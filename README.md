   # Desafio Técnico Zygon Digital - Analista de Dados 

Este projeto coleta dados da playlist do YouTube fornecida, utilizando a YouTube Data API v3, exporta para um arquivo CSV e também faz a persistência em uma tabela no BigQuery. Todo o processo de coleta, tratamento e exportação está em um único arquivo Python conforme solicitado.

## Funcionalidades

- Coleta dados dos vídeos da playlist do YouTube fornecida
- Extrai todas as informações necessárias: ID, título, descrição, data de publicação, likes, views, comentários e thumbnail
- Trata os dados (remove duplicatas, ordena, valida, define tipos das colunas)
- Exporta os dados para arquivo CSV
- Carrega os dados no BigQuery

## Arquivos principais

| Arquivo | Descrição |
|--------|-----------|
| `yt_data.py` | Script principal contendo toda a lógica de coleta, tratamento e exportação |
| `youtube_data.csv` | Arquivo gerado com os dados coletados |
| `dashboard.pbix` | Dashboard criado no Microsoft Power BI |
| `.env.example` | Modelo para configuração das chaves de acesso |
| `requirements.txt` | Dependências do projeto |


## Configuração Rápida

### 1. Obter API Key do YouTube Data API

1. Acesse o [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione um existente
3. Ative a YouTube Data API v3:
   - Navegue para "APIs & Services" > "Library"
   - Procure por "YouTube Data API v3"
   - Clique em "Enable"
4. Crie credenciais:
   - Vá para "APIs & Services" > "Credentials"
   - Clique em "Create Credentials" > "API Key"
   - Copie a chave gerada

### 2. Instalação

```bash
# Clone o repositório
git clone https://github.com/devleomarinho/desafio_zygon
cd desafio_zygon

# Crie um ambiente virtual
python -m venv venv
venv\Scripts\activate 

# Instale as dependências
pip install -r requirements.txt
```
### 3. Configuração

Configure suas variáveis de ambiente
- Copie o arquivo .env.example para .env:

```bash
copy .env.example .env
```
- Preencha o .env com:

    - Sua chave da YouTube API (YOUTUBE_API_KEY)

    - O caminho para sua credencial do BigQuery (GOOGLE_APPLICATION_CREDENTIALS)

    - ENABLE_BIGQUERY=True 

## Execução

```bash
python yt_data.py
```

O script executará automaticamente:
1. **Coleta**: Busca vídeos da playlist fornecida: https://www.youtube.com/playlist?list=PLMC9KNkIncKtPzgY-5rmhvj7fax8fdxoj
2. **Tratamento**: Remove duplicatas, ordena por views, valida dados, define tipos das colunas
3. **Exportação**: Salva em CSV com todas as informações obrigatórias

## Dados Coletados

O arquivo CSV gerado contém as seguintes colunas:

| Coluna           | Tipo            | Descrição                                      |
|------------------|------------------|-----------------------------------------------|
| `video_id`       | `string`         | ID único do vídeo                             |
| `title`          | `string`         | Título do vídeo                               |
| `description`    | `string`         | Descrição do vídeo (limitada a 500 caracteres)|
| `published_date` | `date`           | Data de publicação (YYYY-MM-DD)               |
| `likes`          | `int64`          | Número de likes                               |
| `views`          | `int64`          | Número de visualizações                       |
| `comments`       | `int64`          | Número de comentários                         |
| `thumbnail_url`  | `string`         | URL da thumbnail em alta resolução            |
| `video_url`      | `string`         | URL completa do vídeo no YouTube              |
| `ranking_views`  | `int64`          | Posição no ranking por número de views        |
| `data_coleta`    | `timestamp`      | Data e hora em que os dados foram coletados   |


## Segurança

Este projeto não inclui chaves sensíveis. Para executar corretamente:

    - Crie seu próprio .env

    - Obtenha sua chave de API do YouTube: https://console.developers.google.com/

    - Crie uma credencial de serviço no GCP com o acesso ao BigQuery e salve como .json

    - Para que o upload funcione, a conta de serviço usada no script precisa ter permissão de **Editor** no dataset, neste caso o `yt_playlist_collector`.


## Exemplo de Execução do Script

![image](https://github.com/user-attachments/assets/561d197d-0edb-4339-a7f9-6910c4bb88f0)
![image](https://github.com/user-attachments/assets/82246ea6-ec9d-406b-851d-ca4ce31c2c2a)

## Visualização do arquivo CSV gerado
![image](https://github.com/user-attachments/assets/3c3924d3-2b9b-4f8b-b86e-889d8fb029f5)

## Visualização do esquema e tabela no BigQuery
![image](https://github.com/user-attachments/assets/dca030f4-b25e-4737-aa19-7788c95b257b)


![image](https://github.com/user-attachments/assets/e0daa13c-ccb2-48a1-83c1-724305801882)

---
## Dashboard Analítico no Power BI

O dashboard foi desenvolvido no Power BI a partir do arquivo `youtube_data.csv`. Ele apresenta uma visão analítica da performance dos vídeos da playlist, com foco em **alcance**, **engajamento** e **distribuição temporal**.

### Resumo no topo do dashboard

No topo da tela, são exibidos **indicadores-chave (KPI Cards)** para rápida visualização dos números gerais:

-  **Total de Vídeos**
-  **Total de Visualizações**
-  **Total de Curtidas**
-  **Total de Comentários**
-  **Taxa Média de Engajamento**

Esses cartões oferecem uma visão geral instantânea do volume e da qualidade do engajamento gerado pelos vídeos analisados.

---

### 🔹 Visuais incluídos:

- **Top 10 Vídeos Mais Visualizados**  
  Gráfico de barras empilhadas destacando os vídeos com maior número de visualizações.

- **Top 10 Vídeos Mais Curtidos**  
  Mostra os vídeos com maior volume de likes, permitindo identificar o conteúdo mais apreciado pelo público.

- **Top 10 Vídeos com Maior Taxa de Engajamento**  
  Baseado na métrica `(likes + comentários) ÷ views`, esse gráfico evidencia os vídeos que geram mais interação proporcional ao seu alcance.

- **Evolução Temporal das Publicações**  
  Gráfico de linha mostrando a quantidade de vídeos publicados ao longo do tempo, útil para entender a frequência e distribuição das postagens.

- **Tabela de Detalhamento**  
  Tabela interativa com informações completas por vídeo:
  - Ranking por views
  - Título
  - Número de visualizações
  - Curtidas
  - Comentários
  - Link clicável para o vídeo

---

### Filtros disponíveis:

- Segmentações por **Ano** e **Mês de publicação**, possibilitando análises sazonais
- Slicer por **faixa de ranking (Top 10, Top 11–50, etc.)** para refinar as análises por performance

---

![image](https://github.com/user-attachments/assets/10ccb473-452a-4a8a-ae3e-e0629095178a)










