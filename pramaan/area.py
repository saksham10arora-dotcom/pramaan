"""Minimum built-up area for an Engineering and Technology UG institution, from Annexure 3 of the handbook."""
import math


def engineering_ug(courses: int, intake_per_year: int, years: int = 4, division: int = 60) -> dict:
    """Square metres needed, with the working shown. Assumes divisions of 60 and no X-category workshops."""
    intake = intake_per_year * years
    divisions = math.ceil(intake_per_year / division)
    rooms = math.ceil(divisions * years * 0.5)
    extra = 1 if intake > 600 else 0
    ina = {
        "classrooms": rooms * 66,
        "tutorial rooms": math.ceil(rooms * 0.25) * 33,
        "first year labs": 4 * 66,
        "other labs": 2 * courses * (years - 1) * 66,
        "workshop": (1 + extra) * 200,
        "CAD centre": (1 + extra) * 132,
        "computer centre": (1 + extra) * 150,
        "seminar hall": 132,
        "library": 400 + 50 * math.ceil(max(0, intake - 420) / 60),
        "language lab": 33,
    }
    scale = max(1, intake / 300)  # the handbook gives 750 and 500 up to intake 300; pro rata beyond is our reading
    ada, ama = 750 * scale, 500 * scale
    carpet = sum(ina.values()) + ada + ama
    return {"intake": intake, "instructional": sum(ina.values()), "administrative": ada, "amenities": ama,
            "circulation": carpet * 0.25, "total": carpet * 1.25, "rooms": ina}
