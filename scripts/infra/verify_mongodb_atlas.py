"""Verify and optionally bootstrap the live MongoDB Atlas database for Bounce.

This script intentionally never prints the MongoDB connection string. It can be
run locally with `MONGODB_CONNECTION_STRING` set, or with a URI supplied through
another secret-fetching wrapper.
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from typing import Any

from pymongo import MongoClient

EXPECTED_COLLECTIONS = (
    "traveller_profiles",
    "group_trips",
    "itineraries",
    "flight_performance",
    "airline_ratings",
    "visa_requirements",
    "venue_enrichment",
    "expenses",
    "suggestions",
    "notification_log",
)


@dataclass(frozen=True)
class MongoReadinessResult:
    database: str
    existing_collections: tuple[str, ...]
    missing_collections: tuple[str, ...]
    created_collections: tuple[str, ...]
    write_probe_ok: bool


def _collection_names(database: Any) -> set[str]:
    return set(database.list_collection_names())


def ensure_expected_collections(database: Any, create_missing: bool = False) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Return missing collections and collections created during this run."""
    existing = _collection_names(database)
    missing = tuple(name for name in EXPECTED_COLLECTIONS if name not in existing)

    created: list[str] = []
    if create_missing:
        for name in missing:
            database.create_collection(name)
            created.append(name)

    return missing, tuple(created)


def run_write_probe(database: Any) -> bool:
    """Do a minimal read/write/delete probe against a PRD collection."""
    collection = database["notification_log"]
    marker = "bnc-017-readiness-probe"
    document = {
        "notification_id": marker,
        "trip_id": "readiness",
        "recipient": "system",
        "channel": "readiness",
        "status": "probe",
    }
    collection.delete_many({"notification_id": marker})
    collection.insert_one(document)
    found = collection.find_one({"notification_id": marker})
    collection.delete_many({"notification_id": marker})
    return bool(found and found.get("notification_id") == marker)


def verify_mongodb_atlas(
    uri: str,
    database_name: str = "bounce",
    create_missing: bool = False,
    write_probe: bool = False,
    client_factory: Any = MongoClient,
) -> MongoReadinessResult:
    """Verify Atlas connectivity, expected collections, and optional write access."""
    if not uri.strip():
        raise ValueError("MongoDB URI is required; set MONGODB_CONNECTION_STRING or pass --uri-env.")

    client = client_factory(uri, serverSelectionTimeoutMS=5000)
    client.admin.command("ping")
    database = client[database_name]

    missing_before_create, created = ensure_expected_collections(database, create_missing=create_missing)
    existing_after_create = tuple(sorted(_collection_names(database)))
    missing_after_create = tuple(name for name in EXPECTED_COLLECTIONS if name not in existing_after_create)

    probe_ok = False
    if write_probe:
        probe_ok = run_write_probe(database)

    return MongoReadinessResult(
        database=database_name,
        existing_collections=tuple(name for name in EXPECTED_COLLECTIONS if name in existing_after_create),
        missing_collections=missing_after_create if create_missing else missing_before_create,
        created_collections=created,
        write_probe_ok=probe_ok,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify Bounce MongoDB Atlas readiness without printing secrets.")
    parser.add_argument("--uri-env", default="MONGODB_CONNECTION_STRING", help="Environment variable containing the MongoDB URI.")
    parser.add_argument("--database", default=os.getenv("MONGODB_DATABASE", "bounce"), help="MongoDB database name.")
    parser.add_argument("--create-missing", action="store_true", help="Create any missing PRD collections.")
    parser.add_argument("--write-probe", action="store_true", help="Verify read/write/delete access via notification_log.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    uri = os.getenv(args.uri_env, "")

    try:
        result = verify_mongodb_atlas(
            uri=uri,
            database_name=args.database,
            create_missing=args.create_missing,
            write_probe=args.write_probe,
        )
    except Exception as exc:  # pragma: no cover - exercised by live CLI use
        print(f"MongoDB readiness check failed: {exc}", file=sys.stderr)
        return 1

    print(f"database={result.database}")
    print(f"expected_collections={len(EXPECTED_COLLECTIONS)}")
    print(f"existing_expected_collections={len(result.existing_collections)}")
    print(f"missing_collections={','.join(result.missing_collections) if result.missing_collections else 'none'}")
    print(f"created_collections={','.join(result.created_collections) if result.created_collections else 'none'}")
    print(f"write_probe={'ok' if result.write_probe_ok else 'not_run'}")

    if result.missing_collections:
        return 2
    if args.write_probe and not result.write_probe_ok:
        return 3
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
