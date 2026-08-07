from app.services import worker


def test_worker_completes_simulation_without_blocking_test(monkeypatch):
    monkeypatch.setattr(worker.time, "sleep", lambda _: None)
    state_store = {}
    worker.execute_distributed_simulation("job_1", {"initial_capital": 1000.0, "horizon_years": 1}, state_store)
    assert state_store["job_1"]["status"] == "completed"
    assert state_store["job_1"]["result"] == 1080.0
