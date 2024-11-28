from datetime import datetime, timedelta
from typing import Iterator

import pytest
from pytest_httpx import HTTPXMock

from claspin.plugins.prometheus import (
    PrometheusClient,
    RangeQueryData,
    RangeVector,
)


@pytest.fixture
def client() -> Iterator[PrometheusClient]:
    client = PrometheusClient(url="http://localhost")
    yield client
    client.close()


def test_range_query(client: PrometheusClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url="http://localhost/api/v1/query_range",
        method="POST",
        match_headers={
            "Content-Type": "application/x-www-form-urlencoded",
        },
        match_content=b"query=up&start=1732402800.0&end=1732406400.0&step=3600.0",
        json={
            "data": {
                "result": [
                    {
                        "metric": {"__name__": "up", "service.name": "login"},
                        "values": [[1732402800.0, "1"], [1732406400.0, "1"]],
                    },
                    {
                        "metric": {"__name__": "up", "service.name": "user"},
                        "values": [[1732402800.0, "1"], [1732406400.0, "1"]],
                    },
                ],
            },
        },
    )

    data = client.range_query(
        query="up",
        start=datetime(2024, 11, 24, 0),
        end=datetime(2024, 11, 24, 1),
        step=timedelta(seconds=3600),
    )
    assert data == RangeQueryData(
        result=[
            RangeVector(
                metric={"__name__": "up", "service.name": "login"},
                values=[(1732402800.0, "1"), (1732406400.0, "1")],
            ),
            RangeVector(
                metric={"__name__": "up", "service.name": "user"},
                values=[(1732402800.0, "1"), (1732406400.0, "1")],
            ),
        ],
    )


def test_range_query_with_timeout(
    client: PrometheusClient,
    httpx_mock: HTTPXMock,
):
    httpx_mock.add_response(
        url="http://localhost/api/v1/query_range",
        method="POST",
        match_headers={
            "Content-Type": "application/x-www-form-urlencoded",
        },
        match_content=b"query=up&start=1732402800.0&end=1732406400.0&step=3600.0&timeout=1000ms",
        json={"data": {"result": []}},
    )

    client.range_query(
        query="up",
        start=datetime(2024, 11, 24, 0),
        end=datetime(2024, 11, 24, 1),
        step=timedelta(seconds=3600),
        timeout=timedelta(seconds=1),
    )


def test_label_names(client: PrometheusClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url="http://localhost/api/v1/labels?start=1732402800.0&end=1732406400.0",
        method="GET",
        json={"data": ["__name__", "service.name"]},
    )

    data = client.label_names(
        start=datetime(2024, 11, 24, 0),
        end=datetime(2024, 11, 24, 1),
    )
    assert data == ["__name__", "service.name"]


def test_label_names_with_match(client: PrometheusClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url="http://localhost/api/v1/labels?start=1732402800.0&end=1732406400.0&match=up",
        method="GET",
        json={"data": []},
    )

    client.label_names(
        start=datetime(2024, 11, 24, 0),
        end=datetime(2024, 11, 24, 1),
        match=["up"],
    )


def test_label_names_with_limit(client: PrometheusClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url="http://localhost/api/v1/labels?start=1732402800.0&end=1732406400.0&limit=1",
        method="GET",
        json={"data": []},
    )

    client.label_names(
        start=datetime(2024, 11, 24, 0),
        end=datetime(2024, 11, 24, 1),
        limit=1,
    )


def test_label_values(client: PrometheusClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url="http://localhost/api/v1/label/service.name/values?start=1732402800.0&end=1732406400.0",
        method="GET",
        json={"data": ["login", "user"]},
    )

    data = client.label_values(
        label="service.name",
        start=datetime(2024, 11, 24, 0),
        end=datetime(2024, 11, 24, 1),
    )
    assert data == ["login", "user"]


def test_label_values_with_match(client: PrometheusClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url="http://localhost/api/v1/label/service.name/values?start=1732402800.0&end=1732406400.0&match=up",
        method="GET",
        json={"data": []},
    )

    client.label_values(
        label="service.name",
        start=datetime(2024, 11, 24, 0),
        end=datetime(2024, 11, 24, 1),
        match=["up"],
    )


def test_label_values_with_limit(client: PrometheusClient, httpx_mock: HTTPXMock):
    httpx_mock.add_response(
        url="http://localhost/api/v1/label/service.name/values?start=1732402800.0&end=1732406400.0&limit=1",
        method="GET",
        json={"data": []},
    )

    client.label_values(
        label="service.name",
        start=datetime(2024, 11, 24, 0),
        end=datetime(2024, 11, 24, 1),
        limit=1,
    )
