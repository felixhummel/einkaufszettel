from dataclasses import dataclass
from pathlib import Path
import httpx
import ssl


@dataclass
class ZettelClient:
    url: str
    token: str
    # TODO: use truststore https://www.python-httpx.org/advanced/ssl/#configuring-client-instances
    cafile: Path | str | None = None

    _ssl_ctx: bool | ssl.SSLContext = True

    def __post_init__(self):
        self._headers = {'Authorization': f'Bearer {self.token}'}
        if self.cafile is not None:
            self._ssl_ctx = ssl.create_default_context(
                cafile=str(Path(self.cafile).expanduser())
            )

    def get_client(self):
        return httpx.Client(
            base_url=self.url,
            headers=self._headers,
            verify=self._ssl_ctx,
        )

    def health(self):
        with self.get_client() as client:
            response = client.get('/')
            return response.status_code == 200
