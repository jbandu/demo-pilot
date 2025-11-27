import pytest
from unittest.mock import Mock, patch
from agents.question_handler import QuestionHandler
from anthropic import Anthropic


@pytest.fixture
def question_handler():
    """Create QuestionHandler instance"""
    mock_anthropic = Mock(spec=Anthropic)
    # Mock the nested messages.create structure
    mock_anthropic.messages = Mock()
    mock_anthropic.messages.create = Mock()
    return QuestionHandler(mock_anthropic)


@pytest.fixture
def demo_context():
    """Sample demo context"""
    return {
        "demo_type": "insign",
        "customer_context": {"name": "Test User", "company": "Test Corp"},
        "demo_script": [
            {"name": "Login"},
            {"name": "Dashboard"},
            {"name": "Sign Document"},
        ],
    }


@pytest.mark.asyncio
async def test_handle_question_success(
    question_handler, demo_context, mock_anthropic_response
):
    """Test successful question handling"""
    question_handler.anthropic.messages.create = Mock(
        return_value=Mock(
            content=[Mock(text=mock_anthropic_response["content"][0]["text"])]
        )
    )

    result = await question_handler.handle_question(
        question="How do I sign a document?", demo_context=demo_context, current_step=1
    )

    assert "answer" in result
    assert "action" in result
    assert "intent" in result
    assert result["action"] in [
        "continue",
        "jump_to_feature",
        "deep_dive",
        "schedule_human",
    ]


@pytest.mark.asyncio
async def test_handle_question_with_feature_jump(question_handler, demo_context):
    """Test question that requests feature jump"""
    question_handler.anthropic.messages.create = Mock(
        return_value=Mock(
            content=[
                Mock(
                    text='{"answer": "Let me show you!", "action": "jump_to_feature", "feature": "Sign Document", "intent": "feature_request", "sentiment": "positive", "priority": "normal"}'
                )
            ]
        )
    )

    result = await question_handler.handle_question(
        question="Can you show me how to sign?",
        demo_context=demo_context,
        current_step=0,
    )

    assert result["action"] == "jump_to_feature"
    assert result["feature"] == "Sign Document"


def test_extract_available_features(question_handler):
    """Test extracting features from demo script"""
    demo_script = [{"name": "Feature A"}, {"name": "Feature B"}, {"name": "Feature C"}]

    features = question_handler._extract_available_features(demo_script)

    assert len(features) == 3
    assert "Feature A" in features
    assert "Feature B" in features
    assert "Feature C" in features
