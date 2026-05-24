from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_dockerfile_includes_runtime_packages_for_cloud_run_smoke_paths():
    dockerfile = (ROOT / "Dockerfile").read_text(encoding="utf-8")
    dockerignore = (ROOT / ".dockerignore").read_text(encoding="utf-8")

    assert "COPY workers ./workers" in dockerfile
    assert "COPY frontend ./frontend" in dockerfile
    assert "\nworkers\n" not in f"\n{dockerignore}\n"
    assert "\nfrontend\n" not in f"\n{dockerignore}\n"
