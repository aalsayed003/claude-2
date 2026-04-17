from __future__ import annotations

from pathlib import Path

from .models import Campaign, ShortfallReport


def _format_variance_line(label: str, actual: float, target: float, pct: float) -> str:
    return f"- **{label}:** {actual:,.1f} vs target {target:,.1f} ({pct:+.1f}%)"


def _write_readme(out_dir: Path, report: ShortfallReport, campaign: Campaign | None) -> None:
    lines: list[str] = [
        f"# Weekly campaign drafts — {report.week}",
        "",
        f"Shortfall threshold: {report.threshold_pct}%.",
        "",
        "## Clinic totals",
        _format_variance_line(
            "Revenue",
            report.clinic_revenue.actual,
            report.clinic_revenue.target,
            report.clinic_revenue.variance_pct,
        ),
        _format_variance_line(
            "Patients",
            report.clinic_patients.actual,
            report.clinic_patients.target,
            report.clinic_patients.variance_pct,
        ),
        "",
        "## Doctors",
    ]
    for d in report.doctors:
        tag = " :rotating_light:" if d.flagged else ""
        lines.append(f"### {d.doctor_name} ({d.doctor_id}){tag}")
        lines.append(
            _format_variance_line(
                "Revenue", d.revenue.actual, d.revenue.target, d.revenue.variance_pct
            )
        )
        lines.append(
            _format_variance_line(
                "Patients", d.patients.actual, d.patients.target, d.patients.variance_pct
            )
        )
        lines.append(
            _format_variance_line(
                "Avg revenue / patient",
                d.avg_revenue.actual,
                d.avg_revenue.target,
                d.avg_revenue.variance_pct,
            )
        )
        lines.append(
            f"- Cash mix: {d.cash_mix_pct:.1f}% / Insurance mix: {d.insurance_mix_pct:.1f}%"
        )
        lines.append("")

    if campaign is None:
        if report.has_shortfall:
            lines += [
                "## Campaign",
                f"_Shortfall detected (flagged: {', '.join(report.flagged_doctors) or 'clinic-wide'}) but campaign generation was skipped (dry-run)._",
            ]
        else:
            lines += ["## Campaign", "_No shortfall detected — no campaign generated._"]
    else:
        lines += [
            "## Campaign",
            f"**Diagnosis:** {campaign.diagnosis}",
            f"**Angle:** {campaign.angle}",
            "",
            "See `instagram.md` and `linkedin.md` for the drafts.",
        ]

    (out_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")


def _write_instagram(out_dir: Path, campaign: Campaign) -> None:
    lines = [f"# Instagram drafts — {campaign.week}", ""]
    for i, p in enumerate(campaign.posts.instagram, 1):
        lines += [
            f"## Post {i} — {p.day}",
            "",
            "**Caption:**",
            "",
            p.caption,
            "",
            "**Hashtags:** " + " ".join(p.hashtags),
            "",
            "**Image prompt:**",
            "",
            f"> {p.image_prompt}",
            "",
            "---",
            "",
        ]
    (out_dir / "instagram.md").write_text("\n".join(lines), encoding="utf-8")


def _write_linkedin(out_dir: Path, campaign: Campaign) -> None:
    lines = [f"# LinkedIn drafts — {campaign.week}", ""]
    for i, p in enumerate(campaign.posts.linkedin, 1):
        lines += [
            f"## Post {i} — {p.day}",
            "",
            p.post_text,
            "",
            "---",
            "",
        ]
    (out_dir / "linkedin.md").write_text("\n".join(lines), encoding="utf-8")


def write_drafts(
    root: Path | str,
    report: ShortfallReport,
    campaign: Campaign | None,
) -> Path:
    out_dir = Path(root) / report.week
    out_dir.mkdir(parents=True, exist_ok=True)

    (out_dir / "report.json").write_text(
        report.model_dump_json(indent=2), encoding="utf-8"
    )
    if campaign is not None:
        (out_dir / "campaign.json").write_text(
            campaign.model_dump_json(indent=2), encoding="utf-8"
        )
        _write_instagram(out_dir, campaign)
        _write_linkedin(out_dir, campaign)

    _write_readme(out_dir, report, campaign)
    return out_dir
