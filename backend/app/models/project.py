"""Project ORM model."""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_name: Mapped[str] = mapped_column(String(255), nullable=False)
    project_code: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    state: Mapped[str] = mapped_column(String(80), index=True)
    agency: Mapped[str] = mapped_column(String(120), index=True)
    sector: Mapped[str] = mapped_column(String(80), index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    original_cost_cr: Mapped[float] = mapped_column(Float, nullable=False)
    revised_cost_cr: Mapped[float] = mapped_column(Float, nullable=False)
    current_expenditure_cr: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    physical_progress_pct: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    start_date: Mapped[date] = mapped_column(Date, nullable=False)
    original_completion_date: Mapped[date] = mapped_column(Date, nullable=False)
    revised_completion_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    status: Mapped[str] = mapped_column(String(40), default="Ongoing", index=True)
    location: Mapped[str | None] = mapped_column(String(255), nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    updates: Mapped[list["ProjectUpdate"]] = relationship(
        "ProjectUpdate",
        back_populates="project",
        cascade="all, delete-orphan",
        order_by="ProjectUpdate.update_date",
    )
    predictions: Mapped[list["Prediction"]] = relationship(
        "Prediction",
        back_populates="project",
        cascade="all, delete-orphan",
    )
