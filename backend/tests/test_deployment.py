from pathlib import Path
import yaml

ROOT = Path(__file__).parents[1]


def test_compose_declares_postgres_healthcheck_and_migrating_api():
    compose = yaml.safe_load((ROOT / "docker-compose.yml").read_text())
    assert compose["services"]["postgres"]["image"].startswith("pgvector/pgvector:")
    assert (
        compose["services"]["api"]["depends_on"]["postgres"]["condition"]
        == "service_healthy"
    )
    dockerfile = (ROOT / "Dockerfile").read_text()
    assert "alembic upgrade head" in dockerfile and "USER lifeos" in dockerfile
