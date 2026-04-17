from __future__ import annotations

from typing import Iterable, Protocol

from .models import BudgetRow


class _WorksheetLike(Protocol):
    def get_all_records(self) -> list[dict]: ...


class _SpreadsheetLike(Protocol):
    def worksheet(self, title: str) -> _WorksheetLike: ...


class _GspreadClientLike(Protocol):
    def open_by_key(self, key: str) -> _SpreadsheetLike: ...


def _normalize(rows: Iterable[dict], week: str) -> dict[str, BudgetRow]:
    out: dict[str, BudgetRow] = {}
    for raw in rows:
        row = {str(k).strip().lower().replace(" ", "_"): v for k, v in raw.items()}
        if str(row.get("week", "")).strip() != week:
            continue
        doctor_id = str(row["doctor_id"]).strip()
        out[doctor_id] = BudgetRow(
            doctor_id=doctor_id,
            doctor_name=str(row.get("doctor_name", doctor_id)).strip(),
            week=week,
            target_patients=int(row["target_patients"]),
            target_avg_revenue=float(row["target_avg_revenue"]),
            target_revenue=float(row["target_revenue"]),
        )
    return out


def load_weekly_budget(
    sheet_id: str,
    worksheet: str,
    week: str,
    *,
    client: _GspreadClientLike | None = None,
) -> dict[str, BudgetRow]:
    """Fetch the budget rows for the given ISO week from Google Sheets.

    `client` is injectable so tests can pass a stub without touching network.
    In production it is constructed from the default service-account credentials
    referenced by GOOGLE_APPLICATION_CREDENTIALS.
    """
    if client is None:
        import gspread  # imported lazily so tests don't need network deps

        client = gspread.service_account()
    ws = client.open_by_key(sheet_id).worksheet(worksheet)
    return _normalize(ws.get_all_records(), week)
