from app.services.dialogue import update_dialogue_state


def test_dialogue_state_tracks_topic_transition():
    state = update_dialogue_state(None, "What is this application used for?")
    state = update_dialogue_state(state, "I want to rebalance my portfolio")
    assert state.focus == "rebalancing"
    assert state.transition == "onboarding -> rebalancing"
