import pandas as pd
from googleapiclient.discovery import build
from datetime import datetime
import re
import time
import sys
from dotenv import load_dotenv
import os

load_dotenv()

# =============================================================================
# CREDENCIAIS
# =============================================================================

# Chave da API do YouTube Data API v3
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")

PLAYLIST_ID = "PLMC9KNkIncKtPzgY-5rmhvj7fax8fdxoj"

# Número máximo de vídeos para coletar
MAX_RESULTS = 300

# Nome do arquivo CSV de saída
CSV_FILENAME = "youtube_data.csv"

# Configurações do BigQuery
BIGQUERY_PROJECT_ID = "desafio-zygon"
BIGQUERY_DATASET_ID = "yt_playlist_collector"
BIGQUERY_TABLE_ID = "yt_data"
ENABLE_BIGQUERY = os.getenv("ENABLE_BIGQUERY", "False") == "True"

# =============================================================================
# CLASSE PRINCIPAL
# =============================================================================

class YouTubeDataCollector:
    """Classe para coletar os dados da playlist """
    
    def __init__(self, api_key):
        """Inicializa o coletor com a chave da API"""
        self.api_key = api_key
        self.youtube = build('youtube', 'v3', developerKey=api_key)
        self.collected_data = []
    
    def get_playlist_videos(self, playlist_id, max_results=50):
        """
        Coleta os IDs dos vídeos de uma playlist
        
        Args:
            playlist_id (str): ID da playlist do YouTube
            max_results (int): Número máximo de vídeos a coletar
            
        Returns:
            list: Lista de IDs dos vídeos
        """
        video_ids = []
        next_page_token = None
        
        print(f"Buscando vídeos da playlist...")
        
        while len(video_ids) < max_results:
            try:
                request = self.youtube.playlistItems().list(
                    part='snippet',
                    playlistId=playlist_id,
                    maxResults=min(50, max_results - len(video_ids)),
                    pageToken=next_page_token
                )
                
                response = request.execute()
                
                for item in response['items']:
                    video_ids.append(item['snippet']['resourceId']['videoId'])
                
                next_page_token = response.get('nextPageToken')
                if not next_page_token:
                    break
                
                print(f"Encontrados {len(video_ids)} vídeos até agora...")
                
            except Exception as e:
                print(f"Erro ao buscar vídeos: {str(e)}")
                break
        
        return video_ids[:max_results]
    
    def get_video_details(self, video_ids):
        """
        Coleta detalhes dos vídeos usando os IDs
        
        Args:
            video_ids (list): Lista de IDs dos vídeos
        """
        total_videos = len(video_ids)
        processed = 0
        
        print(f"Coletando detalhes de {total_videos} vídeos...")
        
        
        for i in range(0, len(video_ids), 50):
            batch_ids = video_ids[i:i+50]
            
            try:
                request = self.youtube.videos().list(
                    part='snippet,statistics,contentDetails',
                    id=','.join(batch_ids)
                )
                
                response = request.execute()
                
                for item in response['items']:
                    video_data = self.extract_video_data(item)
                    self.collected_data.append(video_data)
                    processed += 1
                    
                    if processed % 10 == 0:
                        print(f"Processados {processed}/{total_videos} vídeos...")
                
                # Pequena pausa para evitar rate limiting
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Erro ao processar lote de vídeos: {str(e)}")
                continue
        
        print(f"Total processado: {processed}/{total_videos} vídeos")
    
    def extract_video_data(self, video_item):
        """
        Extrai e trata os dados necessários de um vídeo
        
        Args:
            video_item (dict): Item do vídeo retornado pela API
            
        Returns:
            dict: Dados tratados do vídeo
        """
        snippet = video_item['snippet']
        statistics = video_item['statistics']
        content_details = video_item.get('contentDetails', {})
        
        # TRATAMENTO DA DATA DE PUBLICAÇÃO
        published_at = snippet['publishedAt']
        published_date = datetime.strptime(published_at, '%Y-%m-%dT%H:%M:%SZ')
        
        # TRATAMENTO DA URL DA THUMBNAIL (prioriza alta qualidade)
        thumbnails = snippet.get('thumbnails', {})
        thumbnail_url = (
            thumbnails.get('maxres', {}).get('url') or
            thumbnails.get('high', {}).get('url') or
            thumbnails.get('medium', {}).get('url') or
            thumbnails.get('default', {}).get('url') or
            ''
        )
        
        # TRATAMENTO DE ESTATÍSTICAS (alguns vídeos podem não ter todos os dados)
        views = int(statistics.get('viewCount', 0))
        likes = int(statistics.get('likeCount', 0))
        comments = int(statistics.get('commentCount', 0))
        
        # TRATAMENTO DA DURAÇÃO DO VÍDEO
        duration = content_details.get('duration', 'PT0S')
        duration_formatted = self.parse_duration(duration)
        
        # TRATAMENTO DO TÍTULO E DESCRIÇÃO (limpeza)
        title = snippet.get('title', '').strip()
        description = snippet.get('description', '').strip()
        
        # LIMPEZA COMPLETA DA DESCRIÇÃO
        description = description.replace('\n', ' ').replace('\r', ' ')
        description = re.sub(r'\s+', ' ', description) # Remove múltiplos espaços
        description = description.replace('"', '""') 

        # Limitar descrição a 300 caracteres para o CSV
        if len(description) > 300:
            description = description[:300] + "..."
        
        return {
            'video_id': video_item['id'],
            'title': title,
            'description': description,
            'published_date': published_date.strftime('%Y-%m-%d'),
            'likes': likes,
            'views': views,
            'comments': comments,
            'thumbnail_url': thumbnail_url,
            'video_url': f"https://www.youtube.com/watch?v={video_item['id']}"
        }
    
    def parse_duration(self, duration):
        """
        Converte duração ISO 8601 para formato legível
        
        Args:
            duration (str): Duração no formato ISO 8601 (ex: PT4M13S)
            
        Returns:
            str: Duração em formato MM:SS ou HH:MM:SS
        """
        if not duration or duration == 'PT0S':
            return '00:00'
        
        pattern = r'PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?'
        match = re.match(pattern, duration)
        
        if match:
            hours = int(match.group(1) or 0)
            minutes = int(match.group(2) or 0)
            seconds = int(match.group(3) or 0)
            
            if hours > 0:
                return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                return f"{minutes:02d}:{seconds:02d}"
        
        return '00:00'
    
    def treat_data(self):
        """
        Trata os dados coletados
        - Remove duplicatas
        - Ordena por views
        - Adiciona rankings
        - Valida dados
        """
        if not self.collected_data:
            print("Nenhum dado para tratar!")
            return None
        
        print("Tratando dados...")
        
        # Criar DataFrame
        df = pd.DataFrame(self.collected_data)
        
        # Remover duplicatas baseadas no video_id
        initial_count = len(df)
        df = df.drop_duplicates(subset=['video_id'], keep='first')
        final_count = len(df)
        
        if initial_count != final_count:
            print(f"Removidas {initial_count - final_count} duplicatas")
        
        # Ordenar por views (decrescente)
        df = df.sort_values('views', ascending=False)
        
        # Adicionar ranking baseado em views
        df['ranking_views'] = range(1, len(df) + 1)
        
        # Validar dados (remover vídeos sem título)
        df = df[df['title'].str.strip() != '']
        
        # Adicionar data de coleta
        df['data_coleta'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Converter tipos de dados das colunas
        print("Convertendo tipos de dados das colunas do dataframe...")
        try:
            df['video_id'] = df['video_id'].astype(str)
            df['title'] = df['title'].astype(str)
            df['description'] = df['description'].astype(str)
            df['thumbnail_url'] = df['thumbnail_url'].astype(str)
            df['video_url'] = df['video_url'].astype(str)

            df['views'] = df['views'].astype('int64')
            df['likes'] = df['likes'].astype('int64')
            df['comments'] = df['comments'].astype('int64')
            df['ranking_views'] = df['ranking_views'].astype('int64')

            df['published_date'] = pd.to_datetime(df['published_date'], format='%Y-%m-%d')
            df['data_coleta'] = pd.to_datetime(df['data_coleta'], format='%Y-%m-%d %H:%M:%S')
        except Exception as e:
            print(f"Erro na conversão de tipos: {e}")
        
            print(f"Dados tratados: {len(df)} vídeos válidos")
        
        return df
    
    def export_to_csv(self, df, filename):
        """
        Exporta os dados para CSV
        
        Args:
            df (pd.DataFrame): DataFrame com os dados
            filename (str): Nome do arquivo CSV
        """
        if df is None or df.empty:
            print(" Nenhum dado para exportar!")
            return
        
        print(f" Exportando dados para {filename}...")
        
        # Reorganizar colunas na ordem desejada
        columns_order = [
            'video_id', 'title', 'description', 'published_date',
            'likes', 'views', 'comments', 'thumbnail_url',
            'video_url', 'ranking_views', 'data_coleta'
        ]
        
        # Manter apenas as colunas que existem
        available_columns = [col for col in columns_order if col in df.columns]
        df_export = df[available_columns]
        
        # Salvar CSV
        df_export.to_csv(filename, index=False, encoding='utf-8')
        
        print(f" Dados exportados para {filename}")
        
        # Mostrar estatísticas
        self.show_statistics(df)
    
    def show_statistics(self, df):
        """Exibe estatísticas dos dados coletados"""
        print("\n" + "="*60)
        print("ESTATÍSTICAS DOS DADOS COLETADOS")
        print("="*60)
        
        print(f"Total de vídeos coletados: {len(df):,}")
        print(f"Total de visualizações: {df['views'].sum():,}")
        print(f"Total de likes: {df['likes'].sum():,}")
        print(f"Total de comentários: {df['comments'].sum():,}")
        
        print(f"\n TOP 3 VÍDEOS MAIS VISUALIZADOS:")
        top_3 = df.head(3)
        for i, row in top_3.iterrows():
            print(f"{row['ranking_views']}. {row['title'][:50]}...")
            print(f"{row['views']:,} views | {row['likes']:,} likes")
        
        print(f"\n MÉDIAS:")
        print(f" Média de views: {df['views'].mean():,.0f}")
        print(f" Média de likes: {df['likes'].mean():,.0f}")
        print(f" Média de comentários: {df['comments'].mean():,.0f}")
        
        print("="*60)
    
    def collect_playlist_data(self, playlist_id, max_results, csv_filename):
        """
        Método principal que executa todo o processo:
        1. Coleta dados da playlist
        2. Trata os dados
        3. Exporta para CSV
        """
        print("="*60)
        print("INICIANDO COLETA DE DADOS DO YOUTUBE")
        print("="*60)
        
        # 1. COLETA - Buscar IDs dos vídeos
        video_ids = self.get_playlist_videos(playlist_id, max_results)
        
        if not video_ids:
            print(" Nenhum vídeo encontrado na playlist!")
            return None
        
        print(f" Encontrados {len(video_ids)} vídeos na playlist")
        
        # 2. COLETA - Buscar detalhes dos vídeos
        self.get_video_details(video_ids)
        
        # 3. TRATAMENTO - Tratar os dados coletados
        df = self.treat_data()
        
        # 4. EXPORTAÇÃO - Salvar em CSV
        self.export_to_csv(df, csv_filename)
        
        return df

# =============================================================================
# FUNÇÃO PARA CARREGAR NO BIGQUERY 
# =============================================================================

def upload_to_bigquery(df, project_id, dataset_id, table_id):
    """
    Carrega os dados para o BigQuery 
    
    Args:
        df (pd.DataFrame): DataFrame com os dados
        project_id (str): ID do projeto no GCP
        dataset_id (str): ID do dataset no BigQuery
        table_id (str): ID da tabela no BigQuery
    """
    key_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    if key_path:
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = key_path

    try:
        from google.cloud import bigquery
        
        print("Carregando dados no BigQuery...")
        
        client = bigquery.Client(project=project_id)
        
        # Configurar o job de carregamento
        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_TRUNCATE",  # Sobrescreve a tabela
            autodetect=True,  # Detecta automaticamente o schema
        )
        
        # Carregar dados
        table_ref = client.dataset(dataset_id).table(table_id)
        print(f"Enviando {len(df)} registros para o BigQuery...")
        job = client.load_table_from_dataframe(df, table_ref, job_config=job_config)
        
        job.result()  # Aguarda a conclusão
        
        print(f"Dados carregados no BigQuery: {project_id}.{dataset_id}.{table_id}")
        
    except ImportError:
        print(" Biblioteca google-cloud-bigquery não instalada.")
        print(" Para instalar: pip install google-cloud-bigquery")
    except Exception as e:
        print(f" Erro ao carregar dados no BigQuery: {str(e)}")

# =============================================================================
# FUNÇÃO PRINCIPAL
# =============================================================================

def main():
    """Função principal que executa todo o processo"""
    
      
    try:
        # Inicializar o coletor
        collector = YouTubeDataCollector(YOUTUBE_API_KEY)
        
        # Executar todo o processo (coleta, tratamento e exportação)
        df = collector.collect_playlist_data(
            playlist_id=PLAYLIST_ID,
            max_results=MAX_RESULTS,
            csv_filename=CSV_FILENAME
        )
        
        # Carregar no BigQuery 
        if ENABLE_BIGQUERY and df is not None:
            upload_to_bigquery(df, BIGQUERY_PROJECT_ID, BIGQUERY_DATASET_ID, BIGQUERY_TABLE_ID)
        
        print("\nPROCESSO CONCLUÍDO COM SUCESSO!")
        
        
    except Exception as e:
        print(f" Erro durante a execução: {str(e)}")
      
        sys.exit(1)

# =============================================================================
# EXECUÇÃO
# =============================================================================

if __name__ == "__main__":
    main()