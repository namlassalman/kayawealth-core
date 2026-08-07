from enum import Enum

from pydantic import BaseModel


class JobStatus(str, Enum):
    PENDING = "pending"
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class SimulationTask(BaseModel):
    portfolio_name: str
    status: JobStatus
    expected_return: float = 0.0
    processed_async: bool = False
