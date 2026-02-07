import os
from dataclasses import asdict
from pathlib import Path

import polars as pl

from src.domain.state import State
from src.providers.ibge import IBGEClient
from src.storage.minio import MinioClient, minio_client


async def sync(local_data_path: str):

    async with IBGEClient() as client:
        raw_data = await client.get("/v1/localidades/estados")

    states = [
        State(
            id_state=raw["id"],
            name=raw["nome"],
            short_name=raw["sigla"],
            region=raw["regiao"]["nome"],
            region_short_name=raw["regiao"]["sigla"],
        )
        for raw in raw_data
    ]

    upload_states(states, minio_client, local_data_path)


def save_local_parquet(states: list[State], path: str):
    schema = {
        "id_state": pl.Int64,
        "name": pl.Utf8,
        "short_name": pl.Utf8,
        "region": pl.Utf8,
        "region_short_name": pl.Utf8,
    }

    rows = [asdict(state) for state in states]
    df = pl.DataFrame(rows, schema)

    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(path)


def upload_states(states: list[State], minio: MinioClient, local_data_path: str):

    local_path = f"{local_data_path}/br/states.parquet"

    save_local_parquet(states, local_path)

    bucket = os.getenv("BUCKET", "")
    object_name = "br/states.parquet"

    minio.upload_file(bucket, object_name, local_path)
