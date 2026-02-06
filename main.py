import asyncio

from src.pipeline.br import sync_ibge_county


def main():

    asyncio.run(sync_ibge_county.sync())


if __name__ == "__main__":
    main()
