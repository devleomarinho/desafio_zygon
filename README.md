# Desafio Técnico Zygon - Analista de Dados JR. 

Este projeto coleta dados da playlist do YouTube fornecida, utilizando a YouTube Data API v3. Todo o processo de coleta, tratamento e exportação está em um único arquivo Python conforme solicitado.

## Funcionalidades

- ✅ Coleta dados dos vídeos da playlist do YouTube
- ✅ Extrai todas as informações obrigatórias: ID, título, descrição, data de publicação, likes, views, comentários e thumbnail
- ✅ Trata os dados (remove duplicatas, ordena, valida)
- ✅ Exporta os dados para arquivo CSV
- ✅ Carrega os dados no BigQuery

## Arquivos principais

| Arquivo | Descrição |
|--------|-----------|
| `yt_data.py` | Script principal contendo toda a lógica de coleta, tratamento e exportação |
| `youtube_data.csv` | Arquivo gerado com os dados coletados |
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

    -O caminho para sua credencial do BigQuery (GOOGLE_APPLICATION_CREDENTIALS)

    -ENABLE_BIGQUERY=True 

## Execução

```bash
python yt_data.py
```

O script executará automaticamente:
1. **Coleta**: Busca vídeos da playlist
2. **Tratamento**: Remove duplicatas, ordena por views, valida dados
3. **Exportação**: Salva em CSV com todas as informações obrigatórias

## Dados Coletados

O arquivo CSV gerado contém as seguintes colunas **obrigatórias**:

| Coluna | Descrição |
|--------|-----------|
| `video_id` | ID único do vídeo |
| `title` | Título do vídeo |
| `description` | Descrição do vídeo |
| `published_date` | Data de publicação (YYYY-MM-DD) |
| `likes` | Número de likes |
| `views` | Número de visualizações |
| `comments` | Número de comentários |
| `thumbnail_url` | URL da thumbnail |

**Colunas extras adicionadas**:
- `video_url`: URL completa do vídeo
- `ranking_views`: Ranking baseado em visualizações
- `data_coleta`: Data e hora da coleta

## Segurança

Este projeto não inclui chaves sensíveis. Para executar corretamente:

    - Crie seu próprio .env

    - Obtenha sua chave de API do YouTube: https://console.developers.google.com/

    - Crie uma credencial de serviço no GCP com o acesso ao BigQuery e salve como .json

## Exemplo de Saída






