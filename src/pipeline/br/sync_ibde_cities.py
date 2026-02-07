import os
from dataclasses import asdict
from io import BytesIO
from pathlib import Path

import polars as pl

from src.domain.city import City
from src.providers.ibge import IBGEClient
from src.storage.boto3 import s3_client
from src.storage.minio import MinioClient, minio_client


async def sync(local_data_path: str):

    states = get_list_states()
    list_cities = []

    async with IBGEClient() as client:
        for state in states:
            raw_data = await client.get(f"/v1/localidades/estados/{state}/municipios")

            cities = [
                City(
                    id_city=raw["id"],
                    name=raw["nome"],
                    intermediate_region=raw["regiao-imediata"]["nome"],
                    id_state=raw["regiao-imediata"]["regiao-intermediaria"]["UF"]["id"],
                )
                for raw in raw_data
            ]
            list_cities.extend(cities)

    upload_cities(list_cities, minio_client, local_data_path)


def get_list_states() -> list[str]:
    obj = s3_client.get_object(Bucket=os.getenv("BUCKET"), Key="/br/states.parquet")
    data = obj["Body"].read()

    df_states = pl.read_parquet(BytesIO(data))

    return df_states.select("short_name").unique().to_series().to_list()


def save_cities_as_local_parquet(cities: list[City], path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)

    schema = {
        "id_city": pl.Int64,
        "name": pl.Utf8,
        "micro_region": pl.Utf8,
        "id_state": pl.Int64,
    }
    rows = [asdict(city) for city in cities]
    df_cities = pl.DataFrame(rows, schema)
    df_cities.write_parquet(path)


def upload_cities(cities: list[City], minio: MinioClient, local_data_path: str):

    path = f"{local_data_path}/br/cities.parquet"
    save_cities_as_local_parquet(cities, path)

    bucket = os.getenv("BUCKET", "")
    obj_name = "/br/cities.parquet"

    minio_client.upload_file(bucket, obj_name, path)
