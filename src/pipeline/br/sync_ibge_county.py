import os
from dataclasses import asdict
from pathlib import Path

import polars as pl

from src.domain.country import Country
from src.providers.ibge import IBGEClient
from src.storage import minio_client
from src.storage.minio_client import MinioClient


async def sync(local_data_path: str):

    async with IBGEClient() as client:
        raw_data = await client.get("/v1/localidades/paises")

    countries = [
        Country(
            m49=raw["id"]["M49"],
            iso2=raw["id"]["ISO-ALPHA-2"],
            iso3=raw["id"]["ISO-ALPHA-3"],
            name=raw["nome"],
            region=raw["sub-regiao"]["regiao"]["nome"],
            sub_region=raw["sub-regiao"]["nome"],
            intermediate_region=raw["regiao-intermediaria"]["nome"]
            if raw["regiao-intermediaria"]
            else None,
        )
        for raw in raw_data
    ]

    upload_countries(countries, minio_client, local_data_path)


def save_as_local_parquet(countries: list[Country], path: str):

    schema = {
        "m49": pl.Int64,
        "iso2": pl.Utf8,
        "iso3": pl.Utf8,
        "name": pl.Utf8,
        "region": pl.Utf8,
        "sub_region": pl.Utf8,
        "intermediate_region": pl.Utf8,
    }
    rows = [asdict(country) for country in countries]
    df = pl.DataFrame(rows, schema)

    Path(path).parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(path)


def upload_countries(
    countries: list[Country], minio: MinioClient, local_data_path: str
):

    local_path = f"{local_data_path}/br/countries.parquet"

    save_as_local_parquet(countries, local_path)

    bucket = os.getenv("BUCKET", "")
    object_name = "br/countries.parquet"

    minio.upload_file(bucket, object_name, local_path)
