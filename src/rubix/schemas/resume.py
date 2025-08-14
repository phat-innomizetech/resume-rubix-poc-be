from typing import List, Optional
from pydantic import BaseModel


class Experience(BaseModel):
    title: Optional[str] = None
    company: Optional[str] = None
    dates: Optional[str] = None
    description: Optional[str] = None


class Education(BaseModel):
    degree: Optional[str] = None
    university: Optional[str] = None
    dates: Optional[str] = None


class Project(BaseModel):
    name: Optional[str] = None
    dates: Optional[str] = None
    description: Optional[str] = None


class ResumeSchema(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    summary: Optional[str] = None
    experience: Optional[List[Experience]] = None
    education: Optional[List[Education]] = None
    skills: Optional[List[str]] = None
    projects: Optional[List[Project]] = None
    interests: Optional[List[str]] = None


# ===== Example usage =====
if __name__ == "__main__":
    resume = ResumeSchema(
        name="Alice Johnson",
        email="alice@example.com",
        phone="+1-202-555-0183",
        summary="Experienced backend developer.",
        experience=[
            Experience(
                title="Senior Backend Engineer",
                company="TechCorp Inc.",
                dates="Jan 2020 - Present",
                description="Lead development of API services."
            )
        ],
        education=[
            Education(
                degree="B.Sc. in Computer Science",
                university="University of Example",
                dates="2016 - 2020"
            )
        ],
        skills=["Python", "Django", "PostgreSQL"],
        projects=[
            Project(
                name="Inventory Management System",
                dates="2021",
                description="Built using Django and PostgreSQL."
            )
        ],
        interests=["Hiking", "Photography"]
    )

    # Export to JSON (null fields become `null`)
    print(resume.json(indent=2, ensure_ascii=False))
