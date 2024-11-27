from datetime import timedelta
from functools import cached_property

from claspin.model.datasource import DatasourcePlugin
from claspin.plugins.prometheus.client import PrometheusClient


class PrometheusDatasource(DatasourcePlugin):
    url: str
    username: str | None = None
    password: str | None = None
    headers: dict[str, str] | None = None
    timeout: timedelta = timedelta(seconds=60)

    @cached_property
    def client(self) -> PrometheusClient:
        auth = (self.username, self.password) if self.username is not None and self.password is not None else None
        return PrometheusClient(
            url=self.url.rstrip("/"),
            auth=auth,
            headers=self.headers,
            timeout=self.timeout,
        )

    async def close(self) -> None:
        await self.client.close()
