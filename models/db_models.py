import uuid
from sqlalchemy import Column, String, Text, ForeignKey, Integer, DateTime, JSON
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime, timezone

Base = declarative_base()


def generate_uuid():
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    name = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    resumes = relationship("Resume", back_populates="owner")
    jds = relationship("JobDescription", back_populates="owner")


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    resume_url = Column(Text, nullable=True)
    parsed_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="resumes")
    reports = relationship("ATSReport", back_populates="resume")


class JobDescription(Base):
    __tablename__ = "job_descriptions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    jd_text = Column(Text, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    owner = relationship("User", back_populates="jds")
    reports = relationship("ATSReport", back_populates="jd")


class ATSReport(Base):
    __tablename__ = "ats_reports"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    resume_id = Column(String(36), ForeignKey("resumes.id"), nullable=False)
    jd_id = Column(String(36), ForeignKey("job_descriptions.id"), nullable=False)
    ats_score = Column(Integer, nullable=False)
    match_score = Column(Integer, nullable=False)
    report_json = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    resume = relationship("Resume", back_populates="reports")
    jd = relationship("JobDescription", back_populates="reports")
    optimized_resume = relationship("OptimizedResume", back_populates="report", uselist=False)


class OptimizedResume(Base):
    __tablename__ = "optimized_resumes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    report_id = Column(String(36), ForeignKey("ats_reports.id"), nullable=False)
    original_resume = Column(Text, nullable=True)
    optimized_resume = Column(Text, nullable=True)
    download_url = Column(Text, nullable=True)

    report = relationship("ATSReport", back_populates="optimized_resume")
