import time
import requests
from dataclasses import dataclass

@dataclass
class BolToken:
    access_token: str
    expires_at: float

class BolClient:
    def __init__(self, client_id: str, client_secret: str, api_base: str):
        self.client_id = client_id
        self.client_secret = client_secret
        self.api_base = api_base.rstrip("/")
        self._token: BolToken | None = None

    def _get_token(self) -> str:
        if self._token and time.time() < (self._token.expires_at - 30):
            return self._token.access_token

        resp = requests.post(
            "https://login.bol.com/token",
            auth=(self.client_id, self.client_secret),
            data={"grant_type": "client_credentials"},
            timeout=30,
        )
        resp.raise_for_status()
        payload = resp.json()

        access_token = payload["access_token"]
        expires_in = float(payload.get("expires_in", 300))
        self._token = BolToken(access_token=access_token, expires_at=time.time() + expires_in)
        return access_token

    def _headers(self) -> dict:
        token = self._get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.retailer.v10+json",
        }

    def list_orders(self, fulfilment_method: str = "FBR") -> dict:
        url = f"{self.api_base}/orders"
        params = {"fulfilment-method": fulfilment_method}
        resp = requests.get(url, headers=self._headers(), params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()

    def get_order(self, order_id: str) -> dict:
        url = f"{self.api_base}/orders/{order_id}"
        resp = requests.get(url, headers=self._headers(), timeout=30)
        resp.raise_for_status()
        return resp.json()
