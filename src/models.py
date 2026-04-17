from __future__ import annotations

from pydantic import BaseModel, Field


class DoctorActuals(BaseModel):
    doctor_id: str
    doctor_name: str
    patients: int
    avg_revenue_per_patient: float
    cash_patients: int
    insurance_patients: int
    revenue: float


class BudgetRow(BaseModel):
    doctor_id: str
    doctor_name: str
    week: str
    target_patients: int
    target_avg_revenue: float
    target_revenue: float


class Variance(BaseModel):
    actual: float
    target: float
    variance_pct: float


class DoctorShortfall(BaseModel):
    doctor_id: str
    doctor_name: str
    patients: Variance
    avg_revenue: Variance
    revenue: Variance
    cash_mix_pct: float
    insurance_mix_pct: float
    flagged: bool


class ShortfallReport(BaseModel):
    week: str
    threshold_pct: float
    clinic_revenue: Variance
    clinic_patients: Variance
    doctors: list[DoctorShortfall]
    flagged_doctors: list[str] = Field(default_factory=list)

    @property
    def has_shortfall(self) -> bool:
        return bool(self.flagged_doctors) or self.clinic_revenue.variance_pct <= -self.threshold_pct


class InstagramPost(BaseModel):
    day: str
    caption: str
    hashtags: list[str]
    image_prompt: str


class LinkedInPost(BaseModel):
    day: str
    post_text: str


class CampaignPosts(BaseModel):
    instagram: list[InstagramPost] = Field(default_factory=list)
    linkedin: list[LinkedInPost] = Field(default_factory=list)


class Campaign(BaseModel):
    week: str
    diagnosis: str
    angle: str
    posts: CampaignPosts
