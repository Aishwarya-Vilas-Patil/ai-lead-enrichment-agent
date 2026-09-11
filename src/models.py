from pydantic import BaseModel, Field
from typing import List, Optional


class TeamMember(BaseModel):
    name: str
    role: str
    linkedin_url: Optional[str] = None


class CompanyData(BaseModel):
    domain: str

    company_overview: str = Field(
        description="A concise 2-sentence summary of the company."
    )

    target_audience: str = Field(
        description="The ideal customer profile or target audience."
    )

    contact_points: List[str] = Field(
        default_factory=list,
        description="Generic or public email addresses found on the website."
    )

    leadership: List[TeamMember] = Field(
        default_factory=list,
        description="Key leadership or team members discovered."
    )

    confidence_score: float = Field(
        ge=0.0,
        le=1.0,
        description="Confidence in the completeness and accuracy of the extracted data."
    )