import os, time
import httpx
from dotenv import load_dotenv

load_dotenv()

TOKEN_URL = "https://tdx.transportdata.tw/auth/realms/TDXConnect/protocol/openid-connect/token"
BASE = "https://tdx.transportdata.tw/api/basic"

class TDXClient:
    def __init__(self):
        self.client_id = os.getenv("TDX_CLIENT_ID")
        self.client_secret = os.getenv("TDX_CLIENT_SECRET")
        self._token = None
        self._exp = 0

    async def token(self) -> str:
        now = time.time()
        if self._token and now < self._exp - 60:
            return self._token

        async with httpx.AsyncClient(timeout=20) as c:
            r = await c.post(
                TOKEN_URL,
                data={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
                headers={"content-type": "application/x-www-form-urlencoded"},
            )
            r.raise_for_status()
            data = r.json()
            self._token = data["access_token"]
            self._exp = now + int(data.get("expires_in", 86400))
            return self._token

    async def get(self, path: str, params: dict | None = None):
        t = await self.token()
        async with httpx.AsyncClient(timeout=20) as c:
            r = await c.get(f"{BASE}{path}", params=params, headers={"Authorization": f"Bearer {t}"})
            r.raise_for_status()
            return r.json()

    async def stations(self):
        return await self.get("/v2/Rail/TRA/Station", {"$format": "JSON"})
