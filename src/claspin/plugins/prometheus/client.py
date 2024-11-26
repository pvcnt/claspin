from datetime import datetime, timedelta
from typing import Tuple

import httpx
from pydantic import BaseModel


class Histogram(BaseModel):
    count: str
    sum: str
    buckets: list[Tuple[int, str, str, str]]


class RangeVector(BaseModel):
    metric: dict[str, str]
    values: list[Tuple[float, str]] | None = None
    histograms: list[Tuple[float, Histogram]] | None = None


class RangeQueryData(BaseModel):
    result: list[RangeVector]


class RangeQueryResponse(BaseModel):
    data: RangeQueryData


class LabelResponse(BaseModel):
    data: list[str]


class PrometheusClient:
    def __init__(
        self,
        url: str,
        auth: Tuple[str, str] | None = None,
        headers: dict[str, str] | None = None,
        timeout: timedelta | None = None,
    ) -> None:
        self._client = httpx.AsyncClient(
            base_url=url,
            headers=headers,
            auth=auth,
            timeout=timeout.total_seconds() if timeout is not None else None,
        )

    async def range_query(
        self,
        query: str,
        start: datetime,
        end: datetime,
        step: timedelta,
        timeout: timedelta | None = None,
    ) -> RangeQueryData:
        params = {
            "query": query,
            "start": str(start.timestamp()),
            "end": str(end.timestamp()),
            "step": str(step.total_seconds()),
        }
        if timeout is not None:
            params["timeout"] = self._get_duration(timeout)
        # Prefer using POST in case there is a long expression.
        resp = await self._client.post(
            "/api/v1/query_range",
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
            },
            data=params,
        )
        resp.raise_for_status()
        return RangeQueryResponse.model_validate_json(await resp.aread()).data

    async def label_names(
        self,
        start: datetime,
        end: datetime,
        match: str | None = None,
        limit: int | None = None,
    ) -> list[str]:
        params = {"start": str(start.timestamp()), "end": str(end.timestamp())}
        if match is not None:
            params["match"] = match
        if limit is not None:
            params["limit"] = str(limit)
        resp = await self._client.get("/api/v1/labels", params=params)
        resp.raise_for_status()
        return LabelResponse.model_validate_json(await resp.aread()).data

    async def label_values(
        self,
        label: str,
        start: datetime,
        end: datetime,
        match: str | None = None,
        limit: int | None = None,
    ) -> list[str]:
        params = {"start": str(start.timestamp()), "end": str(end.timestamp())}
        if match is not None:
            params["match"] = match
        if limit is not None:
            params["limit"] = str(limit)
        resp = await self._client.get(f"/api/v1/label/{label}/values", params=params)
        resp.raise_for_status()
        return LabelResponse.model_validate_json(await resp.aread()).data

    async def close(self) -> None:
        await self._client.aclose()

    def _get_duration(self, d: timedelta) -> str:
        return f"{int(d.total_seconds() * 1000)}ms"
