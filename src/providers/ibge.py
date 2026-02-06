from dataclasses import dataclass

import httpx


@dataclass
class IBGEClient:
    BASE_URL: str = "https://servicodados.ibge.gov.br/api/"
    timeout: float = 15
    headers: dict[str, str] = {"Accept": "application/json"}
    limits: httpx.Limits = httpx.Limits(
        max_connections=20, max_keepalive_connections=10
    )
    _client: httpx.AsyncClient | None = None

    async def __aexit__(self, exc_type, exc, tb) -> None:
        await self.aclose()

    async def aclose(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def get(self, path: str, *, params: dict | None = None) -> object:
        if self._client is None:
            raise RuntimeError(
                "Use 'async with IBGEClient() as c' para inicializar o client"
            )

        path = path.lstrip("/")
        url = f"{self.BASE_URL}/{path}"

        resp = await self._client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()
