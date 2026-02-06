from src.domain.country import Country
from src.providers.ibge import IBGEClient


async def sync():

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

    print(countries[0])
