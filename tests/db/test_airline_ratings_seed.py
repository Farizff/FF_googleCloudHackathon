import json
from pathlib import Path

SEED_PATH = Path(__file__).resolve().parents[2] / "db" / "seed" / "airline_ratings.json"
FLIGHT_SEED_PATH = Path(__file__).resolve().parents[2] / "db" / "seed" / "seed_flight_performance.json"

REQUIRED_PRD_IATA = {
    "UA", "DL", "AA", "AS", "B6", "WN",
    "BA", "AF", "KL", "LH", "IB", "FR", "U2",
    "NH", "JL", "KE", "OZ", "SQ", "CX", "TG", "MH", "GA",
    "EK", "EY", "QR", "SV",
    "QF", "JQ", "VA",
}
REQUIRED_FIELDS = {"iata", "name", "skytrax_rating", "airhelp_score", "last_verified"}


def load_ratings() -> list[dict]:
    return json.loads(SEED_PATH.read_text(encoding="utf-8"))


def test_airline_ratings_seed_covers_prd_major_airlines_and_demo_flights():
    """Risk scoring needs ratings for PRD major airlines plus every demo flight airline."""
    ratings = load_ratings()
    ratings_by_iata = {rating["iata"]: rating for rating in ratings}
    flight_records = json.loads(FLIGHT_SEED_PATH.read_text(encoding="utf-8"))
    demo_airlines = {record["airline_iata"] for record in flight_records}

    assert REQUIRED_PRD_IATA <= set(ratings_by_iata)
    assert demo_airlines <= set(ratings_by_iata)
    assert len(ratings) >= len(REQUIRED_PRD_IATA)


def test_airline_ratings_records_have_required_scoring_fields():
    ratings = load_ratings()
    iata_codes = [rating["iata"] for rating in ratings]

    assert iata_codes == sorted(iata_codes)
    assert len(iata_codes) == len(set(iata_codes))

    for rating in ratings:
        assert set(rating) == REQUIRED_FIELDS
        assert len(rating["iata"]) == 2
        assert rating["name"]
        assert 1 <= rating["skytrax_rating"] <= 5
        assert 0 <= rating["airhelp_score"] <= 10
        assert rating["last_verified"] == "2026-05-23"


def test_airline_ratings_preserve_low_risk_demo_airlines():
    """ANA and JAL should score highly enough to support the low-risk demo cards."""
    ratings_by_iata = {rating["iata"]: rating for rating in load_ratings()}

    assert ratings_by_iata["NH"]["skytrax_rating"] == 5
    assert ratings_by_iata["JL"]["skytrax_rating"] == 5
    assert ratings_by_iata["NH"]["airhelp_score"] >= 8
    assert ratings_by_iata["JL"]["airhelp_score"] >= 8
