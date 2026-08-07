import pytest
from pydantic import ValidationError

from app.models import JobStatus, SimulationTask


def test_simulation_task_uses_strict_status_enum():
    task = SimulationTask(portfolio_name="Retirement", status=JobStatus.PENDING)
    assert task.status is JobStatus.PENDING
    with pytest.raises(ValidationError):
        SimulationTask(portfolio_name="Retirement", status="unknown")
