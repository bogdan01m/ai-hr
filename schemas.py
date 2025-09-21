from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

class WorkFormat(str, Enum):
    OFFICE = "office"
    REMOTE = "remote"
    HYBRID = "hybrid"

class PositionInfo(BaseModel):
    title: Optional[str] = None
    experience_years: Optional[int] = None
    company_field: Optional[str] = None

class HardSkills(BaseModel):
    programming_languages: Optional[List[str]] = None
    frameworks: Optional[List[str]] = None
    tools: Optional[List[str]] = None
    certifications: Optional[List[str]] = None

class SoftSkills(BaseModel):
    personal_qualities: Optional[List[str]] = None
    communication_skills: Optional[List[str]] = None
    team_skills: Optional[List[str]] = None
    leadership_skills: Optional[List[str]] = None

class WorkConditions(BaseModel):
    work_format: Optional[WorkFormat] = None
    salary_expectations: Optional[str] = None
    benefits: Optional[List[str]] = None
    travel_readiness: Optional[bool] = None

class CandidateProfile(BaseModel):
    position: PositionInfo = PositionInfo()
    hard_skills: HardSkills = HardSkills()
    soft_skills: SoftSkills = SoftSkills()
    work_conditions: WorkConditions = WorkConditions()

    def is_position_complete(self) -> bool:
        return all([
            self.position.title,
            self.position.experience_years is not None,
            self.position.company_field
        ])

    def is_hard_skills_complete(self) -> bool:
        return any([
            self.hard_skills.programming_languages,
            self.hard_skills.frameworks,
            self.hard_skills.tools
        ])

    def is_soft_skills_complete(self) -> bool:
        return any([
            self.soft_skills.personal_qualities,
            self.soft_skills.communication_skills,
            self.soft_skills.team_skills
        ])

    def is_work_conditions_complete(self) -> bool:
        return all([
            self.work_conditions.work_format,
            self.work_conditions.salary_expectations
        ])
    

class ProfileContext(BaseModel):
    profile: CandidateProfile = CandidateProfile()
    current_stage: str = "position"  # position -> hard_skills -> soft_skills -> work_conditions -> complete

    def get_current_stage(self) -> str:
        if not self.profile.is_position_complete():
            return "position"
        elif not self.profile.is_hard_skills_complete():
            return "hard_skills"
        elif not self.profile.is_soft_skills_complete():
            return "soft_skills"
        elif not self.profile.is_work_conditions_complete():
            return "work_conditions"
        else:
            return "complete"