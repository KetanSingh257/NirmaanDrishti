"""
Import historical PAIManA records into project_updates.

Usage:
    cd backend
    python scripts/import_project_updates.py
"""

import sys
from pathlib import Path

import pandas as pd

# --------------------------------------------------
# Make backend imports work
# --------------------------------------------------

BACKEND_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_DIR))

from app.core.database import SessionLocal
from app.models.project import Project
from app.models.project_update import ProjectUpdate


# --------------------------------------------------
# Configuration
# --------------------------------------------------

CSV_PATH = BACKEND_DIR / "paimana_features.csv"

# Set to None to import updates for ALL projects
MAX_PROJECTS = None


# --------------------------------------------------
# Helper functions
# --------------------------------------------------

def clean_float(value, default=0.0):
    """Safely convert a value to float."""
    try:
        if pd.isna(value):
            return default

        return float(value)

    except (ValueError, TypeError):
        return default


def parse_date(value):
    """Safely parse a date."""
    if pd.isna(value):
        return None

    try:
        parsed = pd.to_datetime(value, errors="coerce")

        if pd.isna(parsed):
            return None

        parsed_date = parsed.date()

        if parsed_date.year < 1900 or parsed_date.year > 2100:
            return None

        return parsed_date

    except Exception:
        return None


# --------------------------------------------------
# Load CSV
# --------------------------------------------------

def load_updates():

    print(f"\nLoading CSV from:\n{CSV_PATH}\n")

    if not CSV_PATH.exists():
        raise FileNotFoundError(
            f"CSV not found: {CSV_PATH}"
        )

    df = pd.read_csv(CSV_PATH)

    print(f"Total CSV rows: {len(df)}")

    # Keep only rows with the required data
    df = df[
        df["project_code"].notna()
        & df["report_month"].notna()
        & df["physical_progress_pct"].notna()
        & df["cumulative_expenditure_cr"].notna()
    ].copy()

    # Clean project codes
    df["project_code"] = (
        df["project_code"]
        .astype(str)
        .str.strip()
    )

    # Parse report date
    df["update_date_parsed"] = pd.to_datetime(
        df["report_month"],
        errors="coerce"
    )

    # Remove invalid dates
    df = df[
        df["update_date_parsed"].notna()
    ].copy()

    print(f"Valid historical update rows: {len(df)}")

    # Remove duplicate project/date combinations
    df = df.drop_duplicates(
        subset=["project_code", "update_date_parsed"],
        keep="last"
    )

    print(
        f"Rows after removing duplicate "
        f"project/date combinations: {len(df)}"
    )

    return df


# --------------------------------------------------
# Import updates
# --------------------------------------------------

def import_project_updates():

    df = load_updates()

    db = SessionLocal()

    added = 0
    skipped = 0
    failed = 0

    try:

        # ------------------------------------------
        # Create project_code -> project_id mapping
        # ------------------------------------------

        projects = db.query(
            Project.id,
            Project.project_code
        ).all()

        project_map = {
            str(project_code).strip(): project_id
            for project_id, project_code in projects
        }

        print(
            f"\nProjects found in database: "
            f"{len(project_map)}"
        )

        # ------------------------------------------
        # Optional project limit
        # ------------------------------------------

        if MAX_PROJECTS is not None:

            allowed_codes = set(
                df["project_code"]
                .drop_duplicates()
                .head(MAX_PROJECTS)
            )

            df = df[
                df["project_code"].isin(allowed_codes)
            ]

        # ------------------------------------------
        # Import each historical update
        # ------------------------------------------

        for _, row in df.iterrows():

            try:

                project_code = str(
                    row["project_code"]
                ).strip()

                project_id = project_map.get(
                    project_code
                )

                # Project does not exist in DB
                if project_id is None:
                    skipped += 1
                    continue

                update_date = (
                    row["update_date_parsed"]
                    .date()
                )

                progress = clean_float(
                    row["physical_progress_pct"]
                )

                expenditure = clean_float(
                    row["cumulative_expenditure_cr"]
                )
                expenditure = max(expenditure, 0.0)

                # Keep progress valid
                progress = max(
                    0.0,
                    min(progress, 100.0)
                )

                # ----------------------------------
                # Check duplicate
                # ----------------------------------

                existing = (
                    db.query(ProjectUpdate)
                    .filter(
                        ProjectUpdate.project_id
                        == project_id,
                        ProjectUpdate.update_date
                        == update_date
                    )
                    .first()
                )

                if existing:
                    skipped += 1
                    continue

                # ----------------------------------
                # Create update
                # ----------------------------------

                update = ProjectUpdate(

                    project_id=project_id,

                    update_date=update_date,

                    physical_progress_pct=progress,

                    expenditure_cr=expenditure,

                    remarks=(
                        "Historical update imported "
                        "from PAIManA dataset."
                    )
                )

                db.add(update)

                added += 1

                # Commit periodically for safety
                if added % 500 == 0:

                    db.commit()

                    print(
                        f"Imported {added} updates..."
                    )

            except Exception as e:

                failed += 1

                print(
                    f"Failed row: {e}"
                )

        # ------------------------------------------
        # Final save
        # ------------------------------------------

        db.commit()

        print("\n" + "=" * 55)
        print("PROJECT UPDATES IMPORT COMPLETED")
        print("=" * 55)

        print(f"Added:   {added}")
        print(f"Skipped: {skipped}")
        print(f"Failed:  {failed}")

        total_updates = (
            db.query(ProjectUpdate)
            .count()
        )

        print(
            f"\nTotal updates in database: "
            f"{total_updates}"
        )

        print("=" * 55)

    except Exception as e:

        db.rollback()

        print("\nIMPORT FAILED")
        print(e)

        raise

    finally:

        db.close()


if __name__ == "__main__":
    import_project_updates()