"""Verify Firebase Realtime Database readiness for Bounce.

This script uses the current gcloud access token and never prints credentials.
It checks whether the GCP project has been added to Firebase and whether RTDB
instances exist.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


@dataclass(frozen=True)
class FirebaseReadinessResult:
    project_id: str
    firebase_project_exists: bool
    database_instances: tuple[str, ...]


def get_gcloud_access_token() -> str:
    gcloud = shutil.which("gcloud") or shutil.which("gcloud.cmd") or shutil.which("gcloud.bat")
    if not gcloud:
        raise FileNotFoundError("gcloud CLI was not found on PATH")

    completed = subprocess.run(
        [gcloud, "auth", "print-access-token"],
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def request_json(url: str, token: str, quota_project: str) -> dict[str, Any]:
    request = Request(
        url,
        headers={
            "Authorization": f"Bearer {token}",
            "x-goog-user-project": quota_project,
        },
    )
    with urlopen(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def verify_firebase_rtdb(project_id: str, token: str | None = None) -> FirebaseReadinessResult:
    access_token = token or get_gcloud_access_token()

    project_url = f"https://firebase.googleapis.com/v1beta1/projects/{project_id}"
    instances_url = f"https://firebasedatabase.googleapis.com/v1beta/projects/{project_id}/locations/-/instances"

    firebase_project_exists = False
    database_instances: tuple[str, ...] = ()

    try:
        request_json(project_url, access_token, project_id)
        firebase_project_exists = True
    except HTTPError as exc:
        if exc.code != 404:
            raise

    if firebase_project_exists:
        instances_payload = request_json(instances_url, access_token, project_id)
        database_instances = tuple(instance.get("name", "") for instance in instances_payload.get("instances", []))

    return FirebaseReadinessResult(
        project_id=project_id,
        firebase_project_exists=firebase_project_exists,
        database_instances=database_instances,
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Verify Bounce Firebase RTDB readiness without printing credentials.")
    parser.add_argument("--project", default="project-411e0419-48bd-4b5b-97f", help="Google Cloud/Firebase project ID.")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    try:
        result = verify_firebase_rtdb(project_id=args.project)
    except (HTTPError, URLError, subprocess.CalledProcessError) as exc:  # pragma: no cover - live CLI path
        print(f"Firebase RTDB readiness check failed: {exc}", file=sys.stderr)
        return 1

    print(f"project={result.project_id}")
    print(f"firebase_project_exists={'yes' if result.firebase_project_exists else 'no'}")
    print(f"database_instances={','.join(result.database_instances) if result.database_instances else 'none'}")

    if not result.firebase_project_exists:
        return 2
    if not result.database_instances:
        return 3
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
