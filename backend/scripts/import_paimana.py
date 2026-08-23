"""
Import cleaned PAIManA project data into the NirmaanDrishti SQLite database.

Usage:
    cd backend
    python scripts/import_paimana.py
"""

import sys
from pathlib import Path
from datetime import date, timedelta

import pandas as pd

# --------------------------------------------------
# Make backend imports work when running the script
# --------------------------------------------------

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.core.database import SessionLocal
from app.models.project import Project


# --------------------------------------------------
# Configuration
# --------------------------------------------------

CSV_PATH = BACKEND_DIR / "paimana_features.csv"

# For demo purposes.
# Change to None if you eventually want all projects.
MAX_PROJECTS = None


# --------------------------------------------------
# Helper functions
# --------------------------------------------------

def clean_text(value, default="Unknown"):
    """Clean text values safely."""
    if pd.isna(value):
        return default

    value = str(value).strip()

    if not value or value.lower() == "nan":
        return default

    return value


def clean_float(value, default=0.0):
    """Convert values safely to float."""
    try:
        if pd.isna(value):
            return default

        return float(value)

    except (ValueError, TypeError):
        return default


def parse_date(value):
    """
    Safely parse dates.

    Returns None if the date is missing or invalid.
    """
    if pd.isna(value):
        return None

    try:
        parsed = pd.to_datetime(value, errors="coerce")

        if pd.isna(parsed):
            return None

        parsed_date = parsed.date()

        # Reject obviously invalid dates
        if parsed_date.year < 1900 or parsed_date.year > 2100:
            return None

        return parsed_date

    except Exception:
        return None


def determine_status(progress, days_overdue):
    """Generate a project status."""

    if progress >= 99.5:
        return "Completed"

    if days_overdue > 0:
        return "Delayed"

    return "Ongoing"


# --------------------------------------------------
# Load CSV
# --------------------------------------------------

def load_projects():

    print(f"\nLoading CSV from:\n{CSV_PATH}\n")

    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"CSV not found: {CSV_PATH}\n"
            "Put paimana_features.csv inside the backend folder."
        )

    df = pd.read_csv(CSV_PATH)

    print(f"Total rows in CSV: {len(df)}")

    # --------------------------------------------------
    # Remove summary/category rows
    # Keep rows that have actual project information
    # --------------------------------------------------

    df = df[
        df["project_name"].notna()
        & df["original_cost_cr"].notna()
        & df["physical_progress_pct"].notna()
    ].copy()

    print(f"Valid project rows after cleaning: {len(df)}")

    # --------------------------------------------------
    # Clean report month
    # --------------------------------------------------

    df["report_month_parsed"] = pd.to_datetime(
        df["report_month"],
        errors="coerce"
    )

    # Put invalid dates first
    df = df.sort_values(
        "report_month_parsed",
        ascending=True,
        na_position="first"
    )

    # --------------------------------------------------
    # Keep latest observation for each project
    # --------------------------------------------------

    df["project_code"] = df["project_code"].astype(str).str.strip()

    df = (
        df.groupby("project_code", as_index=False)
        .tail(1)
        .copy()
    )

    print(f"Unique projects after removing duplicates: {len(df)}")

    # --------------------------------------------------
    # Limit number of projects for demo
    # --------------------------------------------------

    if MAX_PROJECTS is not None:
        df = df.head(MAX_PROJECTS)

    print(f"Projects selected for import: {len(df)}\n")

    return df


# --------------------------------------------------
# Import into database
# --------------------------------------------------

def import_projects():

    df = load_projects()

    db = SessionLocal()

    added = 0
    skipped = 0
    failed = 0

    try:

        for _, row in df.iterrows():

            try:

                # ------------------------------------------
                # Basic project information
                # ------------------------------------------

                project_name = clean_text(row["project_name"])
                project_code = clean_text(row["project_code"])

                # ------------------------------------------
                # Skip if already in database
                # ------------------------------------------

                existing = (
                    db.query(Project)
                    .filter(Project.project_code == project_code)
                    .first()
                )

                if existing:
                    skipped += 1
                    continue

                # ------------------------------------------
                # Financial information
                # ------------------------------------------

                original_cost = clean_float(
                    row["original_cost_cr"],
                    0.0
                )

                revised_cost = clean_float(
                    row["revised_cost_cr"],
                    original_cost
                )

                if revised_cost <= 0:
                    revised_cost = original_cost

                expenditure = clean_float(
                    row["cumulative_expenditure_cr"],
                    0.0
                )
                expenditure = max(expenditure, 0.0)

                progress = clean_float(
                    row["physical_progress_pct"],
                    0.0
                )

                # Keep progress inside valid range
                progress = max(0.0, min(progress, 100.0))

                # ------------------------------------------
                # Dates
                # ------------------------------------------

                # Prefer actual start_date
                start_date = parse_date(row.get("start_date"))

                # Otherwise use approval_date
                if start_date is None:
                    start_date = parse_date(
                        row.get("approval_date")
                    )

                # Final fallback
                if start_date is None:
                    start_date = date(2015, 1, 1)

                # Original completion date
                original_completion = parse_date(
                    row.get("original_doc")
                )

                # If missing, estimate one year after start
                if original_completion is None:
                    original_completion = (
                        start_date + timedelta(days=365)
                    )

                # Revised completion date
                revised_completion = parse_date(
                    row.get("revised_doc")
                )

                # ------------------------------------------
                # Status
                # ------------------------------------------

                days_overdue = clean_float(
                    row.get("days_overdue"),
                    0.0
                )

                status = determine_status(
                    progress,
                    days_overdue
                )

                # ------------------------------------------
                # Create project
                # ------------------------------------------

                project = Project(

                    project_name=project_name,
                    project_code=project_code,

                    state=clean_text(row["state"]),
                    agency=clean_text(row["agency"]),

                    # CSV has no reliable sector column
                    sector="Infrastructure",

                    description=(
                        f"Infrastructure project imported "
                        f"from PAIManA dataset."
                    ),

                    original_cost_cr=original_cost,
                    revised_cost_cr=revised_cost,
                    current_expenditure_cr=expenditure,
                    physical_progress_pct=progress,

                    start_date=start_date,

                    original_completion_date=(
                        original_completion
                    ),

                    revised_completion_date=(
                        revised_completion
                    ),

                    status=status,

                    location=clean_text(
                        row["state"],
                        default=None
                    ),
                )

                db.add(project)

                added += 1

            except Exception as e:

                failed += 1

                print(
                    f"Failed to import "
                    f"{row.get('project_name', 'Unknown')}: {e}"
                )

        # ------------------------------------------
        # Save everything
        # ------------------------------------------

        db.commit()

        print("\n" + "=" * 50)
        print("IMPORT COMPLETED")
        print("=" * 50)

        print(f"Added:   {added}")
        print(f"Skipped: {skipped}")
        print(f"Failed:  {failed}")

        total_projects = db.query(Project).count()

        print(f"\nTotal projects in database: {total_projects}")
        print("=" * 50)

    except Exception as e:

        db.rollback()

        print("\nIMPORT FAILED")
        print(e)

        raise

    finally:

        db.close()


if __name__ == "__main__":
    import_projects()