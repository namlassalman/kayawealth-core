from app.services.conversation import client_guidance_response


def test_client_guidance_explains_platform_purpose_without_advisor_template():
    response = client_guidance_response("what is this platform for?")
    assert response is not None
    assert "financial GPS" in response
    assert "Executive Advisory Report" not in response


def test_client_guidance_turns_wealth_goal_into_useful_questions():
    response = client_guidance_response("my planning objective is to get rich")
    assert response is not None
    assert "not a guaranteed outcome" in response
    assert "timeframe" in response
