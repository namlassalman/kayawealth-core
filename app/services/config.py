"""Validated, dependency-free environment settings for the local prototype."""

from dataclasses import dataclass
from pathlib import Path
from typing import Mapping


PROFILE_DEFAULTS = {
    "DEV": {"cache_ttl_seconds": 10, "queue_job_ttl_seconds": 600},
    "TEST": {"cache_ttl_seconds": 60, "queue_job_ttl_seconds": 3_600},
    "PROD": {"cache_ttl_seconds": 300, "queue_job_ttl_seconds": 86_400},
}
DEFAULT_REDIS_URL = "redis://127.0.0.1:6379/0"


@dataclass(frozen=True)
class EnvironmentSettings:
    environment: str
    redis_url: str
    cache_ttl_seconds: int
    queue_job_ttl_seconds: int


def load_settings(env_file: Path, overrides: Mapping[str, str] | None = None) -> EnvironmentSettings:
    """Load `.env` values, then apply explicit process-environment overrides."""
    values = _read_env_file(env_file)
    if overrides:
        values.update({key: value for key, value in overrides.items() if value is not None})

    environment = values.get("AURAWEALTH_ENV", "PROD").strip().upper()
    if environment not in PROFILE_DEFAULTS:
        raise ValueError("AURAWEALTH_ENV must be one of DEV, TEST, or PROD.")

    redis_url = values.get("REDIS_URL", DEFAULT_REDIS_URL).strip()
    if not redis_url.startswith(("redis://", "rediss://")):
        raise ValueError("REDIS_URL must use redis:// or rediss://.")

    defaults = PROFILE_DEFAULTS[environment]
    return EnvironmentSettings(
        environment=environment,
        redis_url=redis_url,
        cache_ttl_seconds=_positive_int(values.get("CACHE_TTL_SECONDS"), "CACHE_TTL_SECONDS", defaults["cache_ttl_seconds"]),
        queue_job_ttl_seconds=_positive_int(values.get("QUEUE_JOB_TTL_SECONDS"), "QUEUE_JOB_TTL_SECONDS", defaults["queue_job_ttl_seconds"]),
    )


def _read_env_file(env_file: Path) -> dict[str, str]:
    if not env_file.exists():
        return {}
    values: dict[str, str] = {}
    for line in env_file.read_text().splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def _positive_int(raw_value: str | None, name: str, default: int) -> int:
    if raw_value is None or raw_value == "":
        return default
    try:
        value = int(raw_value)
    except ValueError as error:
        raise ValueError(f"{name} must be a positive integer.") from error
    if not 1 <= value <= 86_400:
        raise ValueError(f"{name} must be between 1 and 86400 seconds.")
    return value
