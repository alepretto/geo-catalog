# Geo Catalog

Pipeline em Python para coletar dados geográficos do IBGE, transformar em arquivos Parquet e publicar em um bucket compatível com S3 (como MinIO).

## O que o projeto faz

Atualmente o fluxo sincroniza as seguintes entidades do Brasil:

- **Estados** (`br/states.parquet`)
- **Países** (`br/countries.parquet`)
- **Cidades** (`br/cities.parquet`)
- **Distritos** (`br/districts.parquet`)

A coleta é feita pela API pública de localidades do IBGE e os dados são serializados com **Polars**.

## Stack

- Python 3.12+
- httpx (requisições assíncronas)
- polars (transformação e escrita Parquet)
- minio + boto3 (integração com armazenamento S3)
- python-dotenv (variáveis de ambiente)

## Estrutura do projeto

```text
src/
  domain/            # Modelos de dados (dataclasses)
  providers/         # Clientes de APIs externas (IBGE)
  pipeline/br/       # Pipelines de sincronização por entidade
  storage/           # Clientes de armazenamento (MinIO/S3)
main.py              # Orquestra a execução das sincronizações
```

## Pré-requisitos

- Python **>= 3.12**
- Um bucket S3/MinIO acessível
- Credenciais válidas para leitura e escrita no bucket

## Configuração

Crie um arquivo `.env` na raiz do projeto:

```env
MINIO_ENDPOINT=localhost:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin
MINIO_REGION=us-east-1
BUCKET=geo-catalog
```

> Se `MINIO_ENDPOINT` não tiver `http://` ou `https://`, o cliente boto3 adiciona `http://` automaticamente.

## Instalação

Com `uv` (recomendado):

```bash
uv sync
```

Ou com `pip`:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Como executar

```bash
python main.py
```

A execução padrão faz, em ordem:

1. Sincronização de países
2. Sincronização de estados
3. Sincronização de cidades (usa estados já publicados)
4. Sincronização de distritos (usa cidades já publicadas)

Arquivos temporários locais são gerados em `./data/br/` antes do upload.

## Observações importantes

- As etapas de **cidades** e **distritos** dependem de arquivos já existentes no bucket:
  - `states.parquet` para buscar as UFs
  - `cities.parquet` para buscar os IDs de municípios
- Falhas de conectividade na API do IBGE ou no bucket interrompem a execução.
- O projeto usa chamadas assíncronas, mas os loops de sincronização são processados de forma sequencial por estado/cidade.

## Desenvolvimento

Para validar sintaxe rapidamente:

```bash
python -m compileall main.py src
```

## Licença

Este projeto está licenciado sob a licença MIT. Veja [LICENSE](./LICENSE).
