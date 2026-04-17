from __future__ import annotations

from src.analyzer import compare
from src.models import BudgetRow, DoctorActuals


def _actual(**kw):
    defaults = dict(
        doctor_id="doc_a",
        doctor_name="Dr. A",
        patients=50,
        avg_revenue_per_patient=200.0,
        cash_patients=20,
        insurance_patients=30,
        revenue=10000.0,
    )
    defaults.update(kw)
    return DoctorActuals(**defaults)


def _budget(**kw):
    defaults = dict(
        doctor_id="doc_a",
        doctor_name="Dr. A",
        week="2026-W16",
        target_patients=50,
        target_avg_revenue=200.0,
        target_revenue=10000.0,
    )
    defaults.update(kw)
    return BudgetRow(**defaults)


def test_no_shortfall_when_on_budget():
    report = compare([_actual()], {"doc_a": _budget()}, week="2026-W16", threshold_pct=10)
    assert report.flagged_doctors == []
    assert report.has_shortfall is False
    assert report.clinic_revenue.variance_pct == 0.0


def test_flags_doctor_below_threshold():
    a = _actual(revenue=8500.0)  # -15%
    report = compare([a], {"doc_a": _budget()}, week="2026-W16", threshold_pct=10)
    assert report.flagged_doctors == ["doc_a"]
    assert report.doctors[0].revenue.variance_pct == -15.0


def test_exact_boundary_is_flagged():
    a = _actual(revenue=9000.0)  # -10.0%
    report = compare([a], {"doc_a": _budget()}, week="2026-W16", threshold_pct=10)
    assert report.flagged_doctors == ["doc_a"]


def test_just_inside_threshold_is_not_flagged():
    a = _actual(revenue=9010.0)  # -9.9%
    report = compare([a], {"doc_a": _budget()}, week="2026-W16", threshold_pct=10)
    assert report.flagged_doctors == []


def test_cash_insurance_mix():
    a = _actual(cash_patients=15, insurance_patients=35)
    report = compare([a], {"doc_a": _budget()}, week="2026-W16")
    d = report.doctors[0]
    assert d.cash_mix_pct == 30.0
    assert d.insurance_mix_pct == 70.0


def test_clinic_totals_roll_up():
    actuals = [
        _actual(doctor_id="a", revenue=9000, patients=45),
        _actual(doctor_id="b", doctor_name="Dr. B", revenue=11000, patients=55),
    ]
    budget = {
        "a": _budget(doctor_id="a"),
        "b": _budget(doctor_id="b", doctor_name="Dr. B"),
    }
    report = compare(actuals, budget, week="2026-W16", threshold_pct=10)
    assert report.clinic_revenue.actual == 20000
    assert report.clinic_revenue.target == 20000
    assert report.clinic_revenue.variance_pct == 0.0
    assert report.clinic_patients.actual == 100


def test_doctors_without_budget_are_ignored():
    actuals = [_actual(doctor_id="ghost", revenue=5000)]
    report = compare(actuals, {}, week="2026-W16")
    assert report.doctors == []
