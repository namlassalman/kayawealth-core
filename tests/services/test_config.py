import pytest

from app.services.config import load_settings


def test_settings_apply_profile_defaults_and_explicit_overrides(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("AURAWEALTH_ENV=TEST\nREDIS_URL=redis://test-host:6379/2\n")

    settings = load_settings(env_file, {"CACHE_TTL_SECONDS": "90"})

    assert settings.environment == "TEST"
    assert settings.redis_url == "redis://test-host:6379/2"
    assert settings.cache_ttl_seconds == 90
    assert settings.queue_job_ttl_seconds == 3_600


def test_settings_reject_invalid_profile_or_ttl(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("AURAWEALTH_ENV=SANDBOX\n")
    with pytest.raises(ValueError, match="AURAWEALTH_ENV"):
        load_settings(env_file, {})

    env_file.write_text("AURAWEALTH_ENV=DEV\nCACHE_TTL_SECONDS=0\n")
    with pytest.raises(ValueError, match="CACHE_TTL_SECONDS"):
        load_settings(env_file, {})
