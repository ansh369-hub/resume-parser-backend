from pydantic import BaseModel, Field
from typing import List, Dict

class Project(BaseModel):
    name: str = ""
    description: str = ""
    technologies: List[str] = Field(default_factory=list)

class Education(BaseModel):
    degree: str = ""
    institution: str = ""
    start_date: str = ""
    end_date: str = ""
    cgpa: str = ""

class Resume(BaseModel):
    name: str = ""
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    github: str = ""
    location: str = ""
    work_experience: str = ""  
    job_roles: List[str] = Field(default_factory=list)
    summary: str = ""
    skills: Dict[str, List[str]] = Field(default_factory=dict)
    experience: List[dict] = Field(default_factory=list)
    projects: List[Project] = Field(default_factory=list)
    education: List[Education] = Field(default_factory=list)
    certifications: List[str] = Field(default_factory=list)
    achievements: List[str] = Field(default_factory=list)
