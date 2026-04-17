from __future__ import annotations

import json
from pathlib import Path

from src.analyzer import compare
from src.drafts_writer import write_drafts
from src.models import BudgetRow, DoctorActuals


FIXTURES = Path(__file__).parent / "fixtures"


def test_fixture_pipeline_flags_dr_smith_and_writes_drafts(tmp_path):
    actuals_payload = json.loads((FIXTURES / "actuals_2026-W16.json").read_text())
    actuals = [
        DoctorActuals(doctor_id=doc_id, **row)
        for doc_id, row in actuals_payload.items()
    ]

    budget_payload = json.loads((FIXTURES / "budget_2026-W16.json").read_text())
    budget = {row["doctor_id"]: BudgetRow(**row) for row in budget_payload}

    report = compare(actuals, budget, week="2026-W16", threshold_pct=10.0)

    # Smith is 28% below target; others are on budget.
    assert report.flagged_doctors == ["doc_smith"]
    assert report.has_shortfall is True

    out = write_drafts(tmp_path, report, campaign=None)
    assert (out / "report.json").exists()
    assert (out / "README.md").exists()
    # No campaign generated in this --dry-run-equivalent path.
    assert not (out / "campaign.json").exists()
