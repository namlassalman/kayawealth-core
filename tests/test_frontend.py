from streamlit.testing.v1 import AppTest


def test_frontend_renders_without_a_backend_call(monkeypatch, tmp_path):
    monkeypatch.setenv("AURAWEALTH_SESSION_FILE", str(tmp_path / "history.json"))
    app_test = AppTest.from_file("app/frontend.py")
    app_test.run(timeout=15)
    assert not app_test.exception
    assert len(app_test.chat_input) == 1
    assert any("financial GPS" in markdown.value for markdown in app_test.markdown)
