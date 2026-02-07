import asyncio
from pathlib import Path

import dotenv

from src.pipeline.br import sync_ibge_county, sync_ibge_state


async def main():

    dotenv.load_dotenv()

    LOCAL_DATA_PATH = f"{Path(__file__).parent}/data"

    # await sync_ibge_county.sync(LOCAL_DATA_PATH)
    await sync_ibge_state.sync(LOCAL_DATA_PATH)


if __name__ == "__main__":
    asyncio.run(main())
