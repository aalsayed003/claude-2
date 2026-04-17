from __future__ import annotations

import json
from pathlib import Path

from src.budget_sheet import load_weekly_budget


FIXTURE = Path(__file__).parent / "fixtures" / "budget_2026-W16.json"


class _StubWorksheet:
    def __init__(self, rows):
        self._rows = rows

    def get_all_records(self):
        return self._rows


class _StubSpreadsheet:
    def __init__(self, rows):
        self._rows = rows

    def worksheet(self, title):
        assert title == "Weekly Budget"
        return _StubWorksheet(self._rows)


class _StubClient:
    def __init__(self, rows):
        self._rows = rows

    def open_by_key(self, key):
        assert key == "sheet-123"
        return _StubSpreadsheet(self._rows)


def test_load_weekly_budget_parses_rows():
    rows = json.loads(FIXTURE.read_text())
    budget = load_weekly_budget("sheet-123", "Weekly Budget", "2026-W16", client=_StubClient(rows))

    assert set(budget) == {"doc_smith", "doc_jones", "doc_lee"}
    assert budget["doc_smith"].target_revenue == 10000
    assert budget["doc_jones"].doctor_name == "Dr. Jones"


def test_load_weekly_budget_filters_other_weeks():
    rows = [
        {
            "doctor_id": "doc_a", "doctor_name": "A", "week": "2026-W15",
            "target_patients": 10, "target_avg_revenue": 100, "target_revenue": 1000,
        },
        {
            "doctor_id": "doc_b", "doctor_name": "B", "week": "2026-W16",
            "target_patients": 20, "target_avg_revenue": 100, "target_revenue": 2000,
        },
    ]
    budget = load_weekly_budget("sheet-123", "Weekly Budget", "2026-W16", client=_StubClient(rows))
    assert set(budget) == {"doc_b"}


def test_load_weekly_budget_handles_spaced_headers():
    rows = [
        {
            "Doctor ID": "doc_a", "Doctor Name": "A", "Week": "2026-W16",
            "Target Patients": 10, "Target Avg Revenue": 100, "Target Revenue": 1000,
        },
    ]
    budget = load_weekly_budget("sheet-123", "Weekly Budget", "2026-W16", client=_StubClient(rows))
    assert budget["doc_a"].target_revenue == 1000
