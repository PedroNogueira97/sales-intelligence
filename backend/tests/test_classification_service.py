import pytest

from app.core.enums import Qualification, RecommendedAction
from app.services.classification_service import classify_priority, decide_recommended_action


@pytest.mark.parametrize(
    ("score", "expected"),
    [
        (0, "baixa"),
        (1, "baixa"),
        (49, "baixa"),
        (50, "media"),
        (79, "media"),
        (80, "alta"),
        (100, "alta"),
    ],
)
def test_classify_priority_boundaries(score, expected):
    assert classify_priority(score) == expected


@pytest.mark.parametrize("confidence", [0.0, 0.3, 0.59])
def test_decide_recommended_action_low_confidence_always_asks_for_more_information(confidence):
    action = decide_recommended_action(score=95, qualification=Qualification.QUALIFIED, confidence=confidence)

    assert action == RecommendedAction.ASK_MORE_INFORMATION


@pytest.mark.parametrize("score", [80, 90, 100])
def test_decide_recommended_action_high_score_schedules_demo(score):
    action = decide_recommended_action(score=score, qualification=Qualification.QUALIFIED, confidence=0.9)

    assert action == RecommendedAction.SCHEDULE_DEMO


@pytest.mark.parametrize("score", [50, 65, 79])
def test_decide_recommended_action_medium_score_contacts_salesperson(score):
    action = decide_recommended_action(score=score, qualification=Qualification.MAYBE, confidence=0.9)

    assert action == RecommendedAction.CONTACT_SALESPERSON


def test_decide_recommended_action_low_score_unqualified_discards():
    action = decide_recommended_action(score=10, qualification=Qualification.UNQUALIFIED, confidence=0.9)

    assert action == RecommendedAction.DISCARD


def test_decide_recommended_action_low_score_not_unqualified_nurtures():
    action = decide_recommended_action(score=30, qualification=Qualification.MAYBE, confidence=0.9)

    assert action == RecommendedAction.NURTURING


def test_decide_recommended_action_confidence_takes_priority_over_score_band():
    low_confidence = decide_recommended_action(score=10, qualification=Qualification.UNQUALIFIED, confidence=0.2)

    assert low_confidence == RecommendedAction.ASK_MORE_INFORMATION
