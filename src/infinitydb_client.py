from __future__ import annotations

from typing import Any

import httpx

from .models import DoctorActuals


class InfinityDBClient:
    """Thin wrapper around the InfinityDB REST interface.

    InfinityDB exposes data as nested trees under `<base_url>/<database>/<path>`.
    A GET returns the subtree at that path as JSON. We assume actuals are laid
    out as:

        <actuals_path_template(week)> -> { doctor_id: { doctor_name, patients,
            avg_revenue_per_patient, cash_patients, insurance_patients, revenue } }
    """

    def __init__(
        self,
        base_url: str,
        database: str,
        *,
        user: str | None = None,
        password: str | None = None,
        transport: httpx.BaseTransport | None = None,
        timeout: float = 30.0,
    ) -> None:
        auth = (user, password) if user and password else None
        self._client = httpx.Client(
            base_url=base_url.rstrip("/"),
            auth=auth,
            transport=transport,
            timeout=timeout,
            headers={"Accept": "application/json"},
        )
        self._database = database.strip("/")

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "InfinityDBClient":
        return self

    def __exit__(self, *_exc: Any) -> None:
        self.close()

    def _get(self, path: str) -> Any:
        url = f"/{self._database}/{path.strip('/')}"
        resp = self._client.get(url)
        resp.raise_for_status()
        return resp.json()

    def fetch_weekly_actuals(self, week: str, path_template: str) -> list[DoctorActuals]:
        path = path_template.format(week=week)
        payload = self._get(path)
        if not isinstance(payload, dict):
            raise ValueError(
                f"expected dict at {path}, got {type(payload).__name__}"
            )

        actuals: list[DoctorActuals] = []
        for doctor_id, row in payload.items():
            if not isinstance(row, dict):
                continue
            actuals.append(
                DoctorActuals(
                    doctor_id=str(doctor_id),
                    doctor_name=str(row.get("doctor_name", doctor_id)),
                    patients=int(row["patients"]),
                    avg_revenue_per_patient=float(row["avg_revenue_per_patient"]),
                    cash_patients=int(row["cash_patients"]),
                    insurance_patients=int(row["insurance_patients"]),
                    revenue=float(row["revenue"]),
                )
            )
        return actuals
