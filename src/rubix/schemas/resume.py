"""
Resume data schemas and models for the Rubix application.

This module defines Pydantic models for structured resume data representation.
It provides schemas for parsing and validating resume information including
personal details, work experience, education, skills, projects, and interests.

The schemas are designed to handle optional fields gracefully, making them
suitable for parsing resumes with varying levels of completeness.
"""

from typing import List, Optional
from pydantic import BaseModel


class Experience(BaseModel):
    """
    Represents a work experience entry in a resume.

    This model captures the essential information about a job position
    including the role, company, time period, and job description.

    Attributes:
        title (Optional[str]): The job title or position held
        company (Optional[str]): The name of the company or organization
        dates (Optional[str]): The employment period (e.g., "Jan 2020 - Present")
        description (Optional[str]): Detailed description of responsibilities and achievements
    """

    title: Optional[str] = None
    company: Optional[str] = None
    dates: Optional[str] = None
    description: Optional[str] = None


class Education(BaseModel):
    """
    Represents an education entry in a resume.

    This model captures academic qualifications including the degree,
    institution, and completion dates.

    Attributes:
        degree (Optional[str]): The academic degree or qualification earned
        university (Optional[str]): The name of the educational institution
        dates (Optional[str]): The period of study (e.g., "2016 - 2020")
    """

    degree: Optional[str] = None
    university: Optional[str] = None
    dates: Optional[str] = None


class Project(BaseModel):
    """
    Represents a project entry in a resume.

    This model captures information about personal or professional projects
    including the project name, timeline, and description.

    Attributes:
        name (Optional[str]): The name or title of the project
        dates (Optional[str]): The project timeline or completion date
        description (Optional[str]): Detailed description of the project and technologies used
    """

    name: Optional[str] = None
    dates: Optional[str] = None
    description: Optional[str] = None


class ResumeSchema(BaseModel):
    """
    Complete resume data structure.

    This is the main schema for representing a full resume with all its components.
    All fields are optional to accommodate resumes with varying levels of detail
    and completeness.

    Attributes:
        name (Optional[str]): Full name of the person
        email (Optional[str]): Email address for contact
        phone (Optional[str]): Phone number for contact
        summary (Optional[str]): Professional summary or objective statement
        experience (Optional[List[Experience]]): List of work experience entries
        education (Optional[List[Education]]): List of educational qualifications
        skills (Optional[List[str]]): List of technical and soft skills
        projects (Optional[List[Project]]): List of notable projects
        interests (Optional[List[str]]): List of personal interests or hobbies
    """

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
                description="Lead development of API services.",
            )
        ],
        education=[
            Education(
                degree="B.Sc. in Computer Science",
                university="University of Example",
                dates="2016 - 2020",
            )
        ],
        skills=["Python", "Django", "PostgreSQL"],
        projects=[
            Project(
                name="Inventory Management System",
                dates="2021",
                description="Built using Django and PostgreSQL.",
            )
        ],
        interests=["Hiking", "Photography"],
    )

    # Export to JSON
    print(resume.model_dump_json(indent=2))
