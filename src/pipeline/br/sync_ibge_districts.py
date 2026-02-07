import os
from dataclasses import asdict
from io import BytesIO
from pathlib import Path

import polars as pl

from src.domain.district import District
from src.providers.ibge import IBGEClient
from src.storage.boto3 import s3_client
from src.storage.minio import MinioClient, minio_client


async def sync(local_data_path: str):
    cities = get_cities()
    list_districs = []

    async with IBGEClient() as client:
        for id_city in cities:
            raw_data = await client.get(
                f"/v1/localidades/municipios/{id_city}/distritos"
            )

            districs = [
                District(
                    id_distric=raw["id"],
                    name=raw["nome"],
                    id_city=raw["municipio"]["id"],
                )
                for raw in raw_data
            ]

            list_districs.extend(districs)

    upload_districs(list_districs, minio_client, local_data_path)


def get_cities() -> list[int]:

    obj = s3_client.get_object(Bucket=os.getenv("BUCKET"), Key="/br/cities.parquet")
    data = obj["Body"].read()

    df_cities = pl.read_parquet(BytesIO(data))

    return df_cities.select(pl.col("id_city")).unique().to_series().to_list()


def save_districs_as_local_parquet(list_districts: list[District], path: str):

    Path(path).parent.mkdir(parents=True, exist_ok=True)

    schema = {
        "id_distric": pl.Int64,
        "name": pl.Utf8,
        "id_city": pl.Int64,
    }

    rows = [asdict(row) for row in list_districts]
    df_distric = pl.DataFrame(rows, schema)
    df_distric.write_parquet(path)


def upload_districs(
    list_districs: list[District], minio: MinioClient, local_data_path: str
):

    path = f"{local_data_path}/br/districs.parquet"

    save_districs_as_local_parquet(list_districs, path)

    bucket = os.getenv("BUCKET", "")
    object_name = "/br/districs.parquet"
    minio.upload_file(bucket, object_name, path)
