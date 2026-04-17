from __future__ import annotations

from .models import (
    BudgetRow,
    DoctorActuals,
    DoctorShortfall,
    ShortfallReport,
    Variance,
)


def _variance(actual: float, target: float) -> Variance:
    if target == 0:
        pct = 0.0 if actual == 0 else 100.0
    else:
        pct = (actual - target) / target * 100.0
    return Variance(actual=float(actual), target=float(target), variance_pct=round(pct, 2))


def compare(
    actuals: list[DoctorActuals],
    budget: dict[str, BudgetRow],
    *,
    week: str,
    threshold_pct: float = 10.0,
) -> ShortfallReport:
    """Compare actuals to budget and return a structured report.

    A doctor is flagged when revenue lands at or below -threshold_pct versus
    target (i.e. variance_pct <= -threshold_pct).
    """
    doctors: list[DoctorShortfall] = []
    flagged: list[str] = []

    total_actual_rev = 0.0
    total_target_rev = 0.0
    total_actual_pat = 0
    total_target_pat = 0

    for a in actuals:
        b = budget.get(a.doctor_id)
        if b is None:
            continue
        rev_var = _variance(a.revenue, b.target_revenue)
        pat_var = _variance(a.patients, b.target_patients)
        avg_var = _variance(a.avg_revenue_per_patient, b.target_avg_revenue)

        seen = a.cash_patients + a.insurance_patients
        cash_pct = (a.cash_patients / seen * 100.0) if seen else 0.0
        ins_pct = (a.insurance_patients / seen * 100.0) if seen else 0.0

        is_flagged = rev_var.variance_pct <= -threshold_pct
        if is_flagged:
            flagged.append(a.doctor_id)

        doctors.append(
            DoctorShortfall(
                doctor_id=a.doctor_id,
                doctor_name=a.doctor_name,
                patients=pat_var,
                avg_revenue=avg_var,
                revenue=rev_var,
                cash_mix_pct=round(cash_pct, 2),
                insurance_mix_pct=round(ins_pct, 2),
                flagged=is_flagged,
            )
        )

        total_actual_rev += a.revenue
        total_target_rev += b.target_revenue
        total_actual_pat += a.patients
        total_target_pat += b.target_patients

    return ShortfallReport(
        week=week,
        threshold_pct=threshold_pct,
        clinic_revenue=_variance(total_actual_rev, total_target_rev),
        clinic_patients=_variance(total_actual_pat, total_target_pat),
        doctors=doctors,
        flagged_doctors=flagged,
    )
