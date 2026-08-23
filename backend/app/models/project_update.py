"""Historical project update ORM model — fuel for the Trend Engine."""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Float, ForeignKey, Integer, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship


from app.core.database import Base


class ProjectUpdate(Base):
    __tablename__ = "project_updates"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("projects.id", ondelete="CASCADE"), index=True
    )
    update_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)
    physical_progress_pct: Mapped[float] = mapped_column(Float, nullable=False)
    expenditure_cr: Mapped[float] = mapped_column(Float, nullable=False)
    remarks: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    project: Mapped["Project"] = relationship("Project", back_populates="updates")
