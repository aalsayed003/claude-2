from __future__ import annotations

import json
from pathlib import Path

import httpx
import pytest

from src.infinitydb_client import InfinityDBClient


FIXTURE = Path(__file__).parent / "fixtures" / "actuals_2026-W16.json"


def _make_transport(expected_path: str, payload: dict):
    def handler(request: httpx.Request) -> httpx.Response:
        assert request.url.path == expected_path, request.url.path
        return httpx.Response(200, json=payload)

    return httpx.MockTransport(handler)


def test_fetch_weekly_actuals_parses_rows():
    payload = json.loads(FIXTURE.read_text())
    transport = _make_transport("/demo/writeable/clinic/weekly/2026-W16", payload)

    client = InfinityDBClient(
        base_url="https://idb.example.com",
        database="demo/writeable",
        transport=transport,
    )
    rows = client.fetch_weekly_actuals("2026-W16", "clinic/weekly/{week}")
    client.close()

    by_id = {r.doctor_id: r for r in rows}
    assert set(by_id) == {"doc_smith", "doc_jones", "doc_lee"}
    assert by_id["doc_smith"].revenue == 7200.0
    assert by_id["doc_smith"].patients == 40
    assert by_id["doc_jones"].avg_revenue_per_patient == 200.0


def test_fetch_rejects_non_dict_payload():
    transport = _make_transport("/demo/writeable/clinic/weekly/2026-W16", [])
    client = InfinityDBClient(
        base_url="https://idb.example.com",
        database="demo/writeable",
        transport=transport,
    )
    with pytest.raises(ValueError):
        client.fetch_weekly_actuals("2026-W16", "clinic/weekly/{week}")
    client.close()
