"""Seed NIRMAANDRISHTI with 32 realistic Indian infrastructure projects.

Usage (from backend/):
    python -m scripts.seed_data
"""

from __future__ import annotations

import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.core.database import SessionLocal, init_db  # noqa: E402
from app.models.prediction import Prediction  # noqa: E402
from app.models.project import Project  # noqa: E402
from app.models.project_update import ProjectUpdate  # noqa: E402


TODAY = date(2026, 8, 23)


def months_between(start: date, end: date) -> list[date]:
    cursor = date(start.year, start.month, 1)
    out: list[date] = []
    while cursor <= end:
        day = min(28, start.day)
        out.append(date(cursor.year, cursor.month, day))
        if cursor.month == 12:
            cursor = date(cursor.year + 1, 1, 1)
        else:
            cursor = date(cursor.year, cursor.month + 1, 1)
    return [d for d in out if start <= d <= end]


def build_history(
    start: date,
    progress: float,
    expenditure: float,
    profile: str,
    n: int = 10,
) -> list[dict]:
    """Synthesize a coherent monthly history ending at current values."""
    start_hist = start + timedelta(days=60)
    if start_hist >= TODAY - timedelta(days=60):
        start_hist = TODAY - timedelta(days=300)
    dates = months_between(start_hist, TODAY)
    if len(dates) > n:
        step = max(len(dates) // n, 1)
        dates = dates[::step][: n - 1] + [TODAY]
    if dates[-1] != TODAY:
        dates.append(TODAY)
    dates = sorted(set(dates))
    k = max(len(dates) - 1, 1)

    rows = []
    for i, d in enumerate(dates):
        t = i / k
        if profile == "deteriorating":
            # Fast early, then stall. Spend keeps climbing.
            p = progress * (0.72 * (t**0.55) + 0.28 * t)
            e = expenditure * (0.35 * t + 0.65 * (t**0.75))
        elif profile == "stalled":
            p = progress * (0.88 * min(t * 1.35, 0.92) + 0.12 * t)
            e = expenditure * (0.25 * t + 0.75 * (t**0.7))
        elif profile == "improving":
            p = progress * (t**1.35)
            e = expenditure * (t**1.15)
        elif profile == "healthy":
            p = progress * t
            e = expenditure * (t**1.08)
        else:  # stable
            p = progress * (0.15 + 0.85 * t)
            e = expenditure * (0.12 + 0.88 * t)
        if i == len(dates) - 1:
            p, e = progress, expenditure
        rows.append(
            {
                "update_date": d,
                "physical_progress_pct": round(max(p, 0.2), 1),
                "expenditure_cr": round(max(e, 1.0), 2),
                "remarks": _remark(profile, i, len(dates)),
            }
        )
    return rows


def _remark(profile: str, i: int, n: int) -> str:
    if i == n - 1:
        return "Latest official progress report."
    table = {
        "deteriorating": "Land / utility shifting delayed package award.",
        "stalled": "Work nearly paused pending clearances.",
        "improving": "Contractor mobilisation improved after review.",
        "healthy": "Works proceeding as per sanctioned programme.",
        "stable": "Routine monthly progress update.",
    }
    return table.get(profile, "Monthly progress update.")


# Each tuple drives a distinct risk personality.
PROJECTS: list[dict] = [
    {
        "project_name": "Delhi–Meerut RRTS Corridor",
        "project_code": "NCRTC-RRTS-01",
        "state": "Delhi",
        "agency": "NCRTC",
        "sector": "Metro / RRTS",
        "location": "Delhi – Ghaziabad – Meerut",
        "description": "India's first regional rapid transit system linking Delhi to Meerut with semi-high-speed trains.",
        "original_cost_cr": 30274,
        "revised_cost_cr": 34710,
        "current_expenditure_cr": 28140,
        "physical_progress_pct": 78.4,
        "start_date": date(2019, 3, 8),
        "original_completion_date": date(2025, 6, 30),
        "revised_completion_date": date(2026, 12, 31),
        "status": "Ongoing",
        "profile": "stable",
    },
    {
        "project_name": "Mumbai Coastal Road Phase II",
        "project_code": "MMRDA-MCR-02",
        "state": "Maharashtra",
        "agency": "MMRDA",
        "sector": "Urban Roads",
        "location": "Worli – Marine Drive, Mumbai",
        "description": "Sea-link and coastal freeway packages connecting the island city western waterfront.",
        "original_cost_cr": 12690,
        "revised_cost_cr": 16480,
        "current_expenditure_cr": 11210,
        "physical_progress_pct": 54.2,
        "start_date": date(2021, 1, 15),
        "original_completion_date": date(2025, 12, 31),
        "revised_completion_date": date(2027, 6, 30),
        "status": "Ongoing",
        "profile": "deteriorating",
    },
    {
        "project_name": "Char Dham All-Weather Road",
        "project_code": "MORTH-CD-UK-01",
        "state": "Uttarakhand",
        "agency": "MoRTH / BRO",
        "sector": "Highways",
        "location": "Yamunotri–Gangotri–Kedarnath–Badrinath corridors",
        "description": "All-weather connectivity to the four Himalayan shrines with slope-protection and tunnels.",
        "original_cost_cr": 11700,
        "revised_cost_cr": 14120,
        "current_expenditure_cr": 10240,
        "physical_progress_pct": 71.0,
        "start_date": date(2018, 5, 27),
        "original_completion_date": date(2024, 12, 31),
        "revised_completion_date": date(2026, 11, 30),
        "status": "Ongoing",
        "profile": "stable",
    },
    {
        "project_name": "Rishikesh–Karnaprayag Rail Link",
        "project_code": "RVNL-RK-12",
        "state": "Uttarakhand",
        "agency": "RVNL",
        "sector": "Railways",
        "location": "Rishikesh to Karnaprayag, 125 km",
        "description": "Broad-gauge Himalayan rail with 16 tunnels including a 15.1 km main tunnel.",
        "original_cost_cr": 16216,
        "revised_cost_cr": 23900,
        "current_expenditure_cr": 15480,
        "physical_progress_pct": 48.6,
        "start_date": date(2019, 10, 12),
        "original_completion_date": date(2024, 12, 31),
        "revised_completion_date": date(2028, 3, 31),
        "status": "Ongoing",
        "profile": "deteriorating",
    },
    {
        "project_name": "Bengaluru Suburban Rail",
        "project_code": "KRIDE-BSR-01",
        "state": "Karnataka",
        "agency": "K-RIDE",
        "sector": "Railways",
        "location": "Bengaluru urban & suburban corridors",
        "description": "Four-corridor suburban railway to decongest Bengaluru's radial traffic.",
        "original_cost_cr": 15767,
        "revised_cost_cr": 19540,
        "current_expenditure_cr": 6120,
        "physical_progress_pct": 22.8,
        "start_date": date(2022, 6, 20),
        "original_completion_date": date(2026, 6, 30),
        "revised_completion_date": date(2028, 12, 31),
        "status": "Ongoing",
        "profile": "stalled",
    },
    {
        "project_name": "Chennai Metro Phase II",
        "project_code": "CMRL-PH2-01",
        "state": "Tamil Nadu",
        "agency": "CMRL",
        "sector": "Metro",
        "location": "Chennai — 3 corridors, 118.9 km",
        "description": "Expansion of Chennai Metro with three new corridors and underground stretches.",
        "original_cost_cr": 63246,
        "revised_cost_cr": 63246,
        "current_expenditure_cr": 21480,
        "physical_progress_pct": 31.5,
        "start_date": date(2021, 11, 1),
        "original_completion_date": date(2026, 12, 31),
        "revised_completion_date": date(2028, 6, 30),
        "status": "Ongoing",
        "profile": "stable",
    },
    {
        "project_name": "Mumbai–Ahmedabad High Speed Rail",
        "project_code": "NHSRCL-MAHSR",
        "state": "Gujarat",
        "agency": "NHSRCL",
        "sector": "High Speed Rail",
        "location": "Mumbai – Surat – Vadodara – Ahmedabad",
        "description": "India's first bullet-train corridor using Shinkansen technology.",
        "original_cost_cr": 108000,
        "revised_cost_cr": 117000,
        "current_expenditure_cr": 48600,
        "physical_progress_pct": 36.4,
        "start_date": date(2019, 9, 14),
        "original_completion_date": date(2026, 12, 31),
        "revised_completion_date": date(2029, 8, 15),
        "status": "Ongoing",
        "profile": "deteriorating",
    },
    {
        "project_name": "Polavaram Irrigation Project",
        "project_code": "AP-POLA-01",
        "state": "Andhra Pradesh",
        "agency": "Water Resources Dept, AP",
        "sector": "Irrigation",
        "location": "Godavari river, Andhra Pradesh",
        "description": "National project for irrigation, hydropower and drinking water on the Godavari.",
        "original_cost_cr": 16010,
        "revised_cost_cr": 55548,
        "current_expenditure_cr": 31240,
        "physical_progress_pct": 52.1,
        "start_date": date(2014, 5, 1),
        "original_completion_date": date(2018, 3, 31),
        "revised_completion_date": date(2027, 12, 31),
        "status": "Ongoing",
        "profile": "stalled",
    },
    {
        "project_name": "Dedicated Freight Corridor — Eastern",
        "project_code": "DFCCIL-EDFC",
        "state": "Uttar Pradesh",
        "agency": "DFCCIL",
        "sector": "Railways",
        "location": "Ludhiana – Khurja – Dadri – Sonnagar",
        "description": "Heavy-haul freight railway decongesting the Howrah–Delhi trunk.",
        "original_cost_cr": 27202,
        "revised_cost_cr": 31390,
        "current_expenditure_cr": 28410,
        "physical_progress_pct": 89.6,
        "start_date": date(2016, 2, 10),
        "original_completion_date": date(2024, 3, 31),
        "revised_completion_date": date(2026, 10, 31),
        "status": "Ongoing",
        "profile": "improving",
    },
    {
        "project_name": "Hyderabad Metro Airport Express",
        "project_code": "LTMRHL-AX-01",
        "state": "Telangana",
        "agency": "L&T Metro Hyderabad",
        "sector": "Metro",
        "location": "Raidurg – RGIA Shamshabad",
        "description": "Airport express metro extension connecting IT corridor to RGIA.",
        "original_cost_cr": 6250,
        "revised_cost_cr": 6980,
        "current_expenditure_cr": 2140,
        "physical_progress_pct": 27.4,
        "start_date": date(2023, 4, 18),
        "original_completion_date": date(2027, 3, 31),
        "revised_completion_date": None,
        "status": "Ongoing",
        "profile": "healthy",
    },
    {
        "project_name": "Ken–Betwa Link Project Phase I",
        "project_code": "NWDA-KBLP-01",
        "state": "Madhya Pradesh",
        "agency": "NWDA",
        "sector": "Irrigation",
        "location": "Panna – Chhatarpur – Tikamgarh – Jhansi",
        "description": "Interlinking Ken and Betwa rivers with Daudhan dam and transfer canal.",
        "original_cost_cr": 44605,
        "revised_cost_cr": 44605,
        "current_expenditure_cr": 6840,
        "physical_progress_pct": 11.8,
        "start_date": date(2023, 12, 25),
        "original_completion_date": date(2030, 3, 31),
        "revised_completion_date": None,
        "status": "Ongoing",
        "profile": "stable",
    },
    {
        "project_name": "Noida International Airport, Jewar",
        "project_code": "YIDA-NIA-01",
        "state": "Uttar Pradesh",
        "agency": "YIDA / ZIAML",
        "sector": "Aviation",
        "location": "Jewar, Gautam Buddha Nagar",
        "description": "Greenfield international airport for the NCR with dual runways in phase 1.",
        "original_cost_cr": 29560,
        "revised_cost_cr": 32100,
        "current_expenditure_cr": 24890,
        "physical_progress_pct": 81.2,
        "start_date": date(2021, 10, 1),
        "original_completion_date": date(2024, 12, 31),
        "revised_completion_date": date(2026, 9, 30),
        "status": "Ongoing",
        "profile": "improving",
    },
    {
        "project_name": "Kolkata East–West Metro",
        "project_code": "KMRC-EW-01",
        "state": "West Bengal",
        "agency": "KMRC",
        "sector": "Metro",
        "location": "Howrah Maidan – Salt Lake Sector V / CBIC",
        "description": "Under-river metro connecting Howrah and Salt Lake, including India's first under-river tunnel.",
        "original_cost_cr": 4874,
        "revised_cost_cr": 8574,
        "current_expenditure_cr": 7920,
        "physical_progress_pct": 86.5,
        "start_date": date(2009, 2, 22),
        "original_completion_date": date(2015, 12, 31),
        "revised_completion_date": date(2026, 12, 31),
        "status": "Ongoing",
        "profile": "stable",
    },
    {
        "project_name": "Vadodara–Mumbai Expressway",
        "project_code": "NHAI-VME-08",
        "state": "Gujarat",
        "agency": "NHAI",
        "sector": "Highways",
        "location": "Vadodara – Bharuch – Surat – Mumbai",
        "description": "Access-controlled 8-lane expressway on the Delhi–Mumbai corridor.",
        "original_cost_cr": 38420,
        "revised_cost_cr": 42150,
        "current_expenditure_cr": 30110,
        "physical_progress_pct": 74.8,
        "start_date": date(2020, 3, 8),
        "original_completion_date": date(2025, 3, 31),
        "revised_completion_date": date(2026, 12, 31),
        "status": "Ongoing",
        "profile": "improving",
    },
    {
        "project_name": "Sivok–Rangpo Rail Link",
        "project_code": "IRCON-SR-01",
        "state": "Sikkim",
        "agency": "IRCON",
        "sector": "Railways",
        "location": "Sivok (WB) to Rangpo (Sikkim)",
        "description": "Himalayan rail gateway to Sikkim with 14 tunnels through fragile geology.",
        "original_cost_cr": 1689,
        "revised_cost_cr": 4340,
        "current_expenditure_cr": 3180,
        "physical_progress_pct": 61.3,
        "start_date": date(2010, 10, 1),
        "original_completion_date": date(2015, 12, 31),
        "revised_completion_date": date(2027, 6, 30),
        "status": "Ongoing",
        "profile": "deteriorating",
    },
    {
        "project_name": "Pune Metro Line 3 (Hinjewadi–Shivajinagar)",
        "project_code": "PMRDA-L3",
        "state": "Maharashtra",
        "agency": "Maha Metro / PMRDA",
        "sector": "Metro",
        "location": "Hinjewadi IT park to Shivajinagar",
        "description": "23.3 km elevated metro serving Pune's western IT corridor.",
        "original_cost_cr": 8320,
        "revised_cost_cr": 9904,
        "current_expenditure_cr": 5410,
        "physical_progress_pct": 46.7,
        "start_date": date(2021, 8, 5),
        "original_completion_date": date(2025, 12, 31),
        "revised_completion_date": date(2027, 9, 30),
        "status": "Ongoing",
        "profile": "stable",
    },
    {
        "project_name": "Tehri Pumped Storage Plant",
        "project_code": "THDC-PSP-1000",
        "state": "Uttarakhand",
        "agency": "THDC India",
        "sector": "Power",
        "location": "Tehri, Garhwal",
        "description": "1,000 MW pumped-storage hydro adjoining the Tehri dam complex.",
        "original_cost_cr": 5747,
        "revised_cost_cr": 8390,
        "current_expenditure_cr": 6120,
        "physical_progress_pct": 68.9,
        "start_date": date(2017, 7, 10),
        "original_completion_date": date(2023, 3, 31),
        "revised_completion_date": date(2026, 12, 31),
        "status": "Ongoing",
        "profile": "improving",
    },
    {
        "project_name": "Bhopal Metro Phase I",
        "project_code": "MPMRCL-BPL-01",
        "state": "Madhya Pradesh",
        "agency": "MPMRCL",
        "sector": "Metro",
        "location": "Bhopal — Orange & Blue lines",
        "description": "Two-corridor metro for Bhopal with a mix of elevated and underground alignment.",
        "original_cost_cr": 6941,
        "revised_cost_cr": 8704,
        "current_expenditure_cr": 2980,
        "physical_progress_pct": 29.4,
        "start_date": date(2022, 1, 20),
        "original_completion_date": date(2026, 3, 31),
        "revised_completion_date": date(2028, 3, 31),
        "status": "Ongoing",
        "profile": "deteriorating",
    },
    {
        "project_name": "Visakhapatnam Port Outer Harbour",
        "project_code": "VPA-OH-01",
        "state": "Andhra Pradesh",
        "agency": "Visakhapatnam Port Authority",
        "sector": "Ports",
        "location": "Visakhapatnam outer harbour",
        "description": "Deep-draft outer harbour and mechanised berths for cape-size vessels.",
        "original_cost_cr": 4230,
        "revised_cost_cr": 4810,
        "current_expenditure_cr": 1960,
        "physical_progress_pct": 41.2,
        "start_date": date(2022, 9, 12),
        "original_completion_date": date(2026, 9, 30),
        "revised_completion_date": None,
        "status": "Ongoing",
        "profile": "healthy",
    },
    {
        "project_name": "Ganga Expressway",
        "project_code": "UPEIDA-GE-01",
        "state": "Uttar Pradesh",
        "agency": "UPEIDA",
        "sector": "Highways",
        "location": "Meerut – Prayagraj (594 km)",
        "description": "Access-controlled expressway along the Ganga basin connecting west and east UP.",
        "original_cost_cr": 36230,
        "revised_cost_cr": 38540,
        "current_expenditure_cr": 27110,
        "physical_progress_pct": 72.6,
        "start_date": date(2021, 12, 18),
        "original_completion_date": date(2025, 12, 31),
        "revised_completion_date": date(2026, 11, 30),
        "status": "Ongoing",
        "profile": "improving",
    },
    {
        "project_name": "Kochi Water Metro Phase II",
        "project_code": "KMRL-WM-02",
        "state": "Kerala",
        "agency": "KMRL",
        "sector": "Urban Transit",
        "location": "Kochi backwaters — additional terminals",
        "description": "Expansion of the integrated water-metro network with new island terminals.",
        "original_cost_cr": 981,
        "revised_cost_cr": 1240,
        "current_expenditure_cr": 410,
        "physical_progress_pct": 33.8,
        "start_date": date(2023, 7, 1),
        "original_completion_date": date(2026, 6, 30),
        "revised_completion_date": date(2027, 3, 31),
        "status": "Ongoing",
        "profile": "stable",
    },
    {
        "project_name": "AIIMS Rishikesh Super-Specialty Block",
        "project_code": "MOHFW-AIIMS-RK",
        "state": "Uttarakhand",
        "agency": "MoHFW / HSCC",
        "sector": "Health Infrastructure",
        "location": "Virbhadra, Rishikesh",
        "description": "Additional super-specialty towers, trauma centre and residential campus.",
        "original_cost_cr": 1480,
        "revised_cost_cr": 1725,
        "current_expenditure_cr": 990,
        "physical_progress_pct": 58.4,
        "start_date": date(2021, 2, 14),
        "original_completion_date": date(2025, 3, 31),
        "revised_completion_date": date(2026, 10, 31),
        "status": "Ongoing",
        "profile": "stable",
    },
    {
        "project_name": "Jaipur Metro Phase II",
        "project_code": "JMRC-PH2",
        "state": "Rajasthan",
        "agency": "JMRC",
        "sector": "Metro",
        "location": "Sitapura – Ambabari via Civil Lines",
        "description": "North–south corridor expansion of Jaipur Metro.",
        "original_cost_cr": 2583,
        "revised_cost_cr": 4320,
        "current_expenditure_cr": 980,
        "physical_progress_pct": 16.2,
        "start_date": date(2023, 1, 9),
        "original_completion_date": date(2027, 12, 31),
        "revised_completion_date": None,
        "status": "Ongoing",
        "profile": "stalled",
    },
    {
        "project_name": "Sardar Sarovar Canal Network Modernisation",
        "project_code": "SSNNL-CAN-04",
        "state": "Gujarat",
        "agency": "SSNNL",
        "sector": "Irrigation",
        "location": "Narmada main canal command, Gujarat",
        "description": "Lining, gates and pressurised distribution to reduce conveyance losses.",
        "original_cost_cr": 6120,
        "revised_cost_cr": 6780,
        "current_expenditure_cr": 4010,
        "physical_progress_pct": 63.5,
        "start_date": date(2020, 6, 1),
        "original_completion_date": date(2025, 6, 30),
        "revised_completion_date": date(2026, 12, 31),
        "status": "Ongoing",
        "profile": "healthy",
    },
    {
        "project_name": "Samruddhi Mahamarg Remaining Packages",
        "project_code": "MSRDC-NS-REM",
        "state": "Maharashtra",
        "agency": "MSRDC",
        "sector": "Highways",
        "location": "Nagpur – Shirdi – Mumbai remaining links",
        "description": "Balance packages and interchanges on the Nagpur–Mumbai expressway.",
        "original_cost_cr": 55400,
        "revised_cost_cr": 55400,
        "current_expenditure_cr": 49810,
        "physical_progress_pct": 93.1,
        "start_date": date(2018, 12, 24),
        "original_completion_date": date(2023, 3, 31),
        "revised_completion_date": date(2026, 9, 30),
        "status": "Ongoing",
        "profile": "improving",
    },
    {
        "project_name": "Patna Metro Phase I",
        "project_code": "BMRCL-PAT-01",
        "state": "Bihar",
        "agency": "Patna Metro Rail Corp",
        "sector": "Metro",
        "location": "Danapur – Khemni Chak & Patna Jn – New ISBT",
        "description": "Two priority corridors for Patna with elevated and underground sections.",
        "original_cost_cr": 13367,
        "revised_cost_cr": 16840,
        "current_expenditure_cr": 4120,
        "physical_progress_pct": 18.9,
        "start_date": date(2022, 2, 15),
        "original_completion_date": date(2026, 2, 28),
        "revised_completion_date": date(2028, 12, 31),
        "status": "Ongoing",
        "profile": "stalled",
    },
    {
        "project_name": "Srinagar Ring Road Phase II",
        "project_code": "NHAI-SRR-02",
        "state": "Jammu & Kashmir",
        "agency": "NHAI",
        "sector": "Highways",
        "location": "Galander – Nowgam – Bemina bypass",
        "description": "Western ring road completing the Srinagar urban bypass.",
        "original_cost_cr": 2164,
        "revised_cost_cr": 2890,
        "current_expenditure_cr": 1540,
        "physical_progress_pct": 44.7,
        "start_date": date(2021, 5, 3),
        "original_completion_date": date(2025, 5, 31),
        "revised_completion_date": date(2027, 3, 31),
        "status": "Ongoing",
        "profile": "deteriorating",
    },
    {
        "project_name": "Vizhinjam International Seaport",
        "project_code": "AVPPL-VIZ-01",
        "state": "Kerala",
        "agency": "Adani Vizhinjam Port / GoK",
        "sector": "Ports",
        "location": "Vizhinjam, Thiruvananthapuram",
        "description": "Deep-water transshipment port on the international east–west shipping lane.",
        "original_cost_cr": 7525,
        "revised_cost_cr": 8890,
        "current_expenditure_cr": 7340,
        "physical_progress_pct": 88.2,
        "start_date": date(2015, 12, 5),
        "original_completion_date": date(2019, 12, 31),
        "revised_completion_date": date(2026, 8, 31),
        "status": "Ongoing",
        "profile": "improving",
    },
    {
        "project_name": "Navi Mumbai International Airport",
        "project_code": "CIDCO-NMIA",
        "state": "Maharashtra",
        "agency": "CIDCO / Adani Airport",
        "sector": "Aviation",
        "location": "Ulwe, Navi Mumbai",
        "description": "Greenfield international airport to complement CSIA Mumbai.",
        "original_cost_cr": 16700,
        "revised_cost_cr": 19650,
        "current_expenditure_cr": 15120,
        "physical_progress_pct": 79.5,
        "start_date": date(2021, 2, 18),
        "original_completion_date": date(2024, 12, 31),
        "revised_completion_date": date(2026, 10, 31),
        "status": "Ongoing",
        "profile": "stable",
    },
    {
        "project_name": "Indore Metro Phase I",
        "project_code": "MPMRCL-IDR-01",
        "state": "Madhya Pradesh",
        "agency": "MPMRCL",
        "sector": "Metro",
        "location": "Yellow Line, Indore",
        "description": "Priority corridor of Indore Metro along AB Road and MR 10.",
        "original_cost_cr": 7501,
        "revised_cost_cr": 8900,
        "current_expenditure_cr": 3640,
        "physical_progress_pct": 38.6,
        "start_date": date(2021, 6, 11),
        "original_completion_date": date(2026, 6, 30),
        "revised_completion_date": date(2027, 12, 31),
        "status": "Ongoing",
        "profile": "stable",
    },
    {
        "project_name": "Haridwar–Rishikesh Elevated Corridor",
        "project_code": "PWD-UK-HREC",
        "state": "Uttarakhand",
        "agency": "PWD Uttarakhand",
        "sector": "Urban Roads",
        "location": "Haridwar to Rishikesh NH-34",
        "description": "Elevated corridor to decongest pilgrimage traffic between Haridwar and Rishikesh.",
        "original_cost_cr": 2840,
        "revised_cost_cr": 3510,
        "current_expenditure_cr": 1680,
        "physical_progress_pct": 41.0,
        "start_date": date(2022, 3, 21),
        "original_completion_date": date(2025, 12, 31),
        "revised_completion_date": date(2027, 6, 30),
        "status": "Ongoing",
        "profile": "deteriorating",
    },
    {
        "project_name": "Kashi Vishwanath Corridor Phase II",
        "project_code": "UPSIDA-KVC-02",
        "state": "Uttar Pradesh",
        "agency": "UPSIDA / VDA",
        "sector": "Urban Development",
        "location": "Varanasi old city",
        "description": "Heritage precinct, ghat connectivity and pilgrim infrastructure around the temple.",
        "original_cost_cr": 890,
        "revised_cost_cr": 1240,
        "current_expenditure_cr": 760,
        "physical_progress_pct": 64.8,
        "start_date": date(2022, 8, 1),
        "original_completion_date": date(2025, 8, 31),
        "revised_completion_date": date(2026, 12, 31),
        "status": "Ongoing",
        "profile": "healthy",
    },
    {
        "project_name": "Chardham Heliport Network",
        "project_code": "AAI-CD-HEL",
        "state": "Uttarakhand",
        "agency": "AAI / UK Civil Aviation",
        "sector": "Aviation",
        "location": "Sahastradhara, Gauchar, Guptkashi, Kedarnath",
        "description": "All-weather heliports supporting pilgrim and emergency evacuation operations.",
        "original_cost_cr": 640,
        "revised_cost_cr": 812,
        "current_expenditure_cr": 390,
        "physical_progress_pct": 49.2,
        "start_date": date(2023, 2, 10),
        "original_completion_date": date(2026, 3, 31),
        "revised_completion_date": None,
        "status": "Ongoing",
        "profile": "stable",
    },
    {
        "project_name": "Eastern Rajasthan Canal Project",
        "project_code": "WRD-RAJ-ERCP",
        "state": "Rajasthan",
        "agency": "Water Resources Dept, Rajasthan",
        "sector": "Irrigation",
        "location": "Chambal basin — 13 districts",
        "description": "Intra-state canal linking Chambal surplus to water-stressed eastern districts.",
        "original_cost_cr": 37278,
        "revised_cost_cr": 39710,
        "current_expenditure_cr": 4210,
        "physical_progress_pct": 8.4,
        "start_date": date(2024, 1, 16),
        "original_completion_date": date(2031, 3, 31),
        "revised_completion_date": None,
        "status": "Ongoing",
        "profile": "healthy",
    },
]


def seed() -> None:
    init_db()
    db = SessionLocal()
    try:
        existing = db.query(Project).count()
        if existing:
            print(f"Clearing {existing} existing projects…")
            db.query(Prediction).delete()
            db.query(ProjectUpdate).delete()
            db.query(Project).delete()
            db.commit()

        created = 0
        for raw in PROJECTS:
            spec = dict(raw)
            profile = spec.pop("profile")
            history = build_history(
                spec["start_date"],
                spec["physical_progress_pct"],
                spec["current_expenditure_cr"],
                profile,
            )
            project = Project(**spec)
            db.add(project)
            db.flush()
            for row in history:
                db.add(ProjectUpdate(project_id=project.id, **row))
            created += 1
        db.commit()
        print(f"Seeded {created} projects with historical updates.")
    finally:
        db.close()


if __name__ == "__main__":
    seed()
