"""Test AI provider implementations and error handling."""

import pytest
from app.services.ai_provider import (
    DemoAIProvider,
    GeminiAIProvider,
    OpenAIAIProvider,
    AIConfigurationError,
    AIServiceUnavailableError,
    get_ai_provider
)


def test_demo_provider_returns_structured_answer():
    """Test that DemoAIProvider responds with curated content for key topics."""
    provider = DemoAIProvider()
    reply = provider.generate_reply([{'role': 'user', 'content': 'Tell me about the ACID properties'}])

    assert reply['is_demo'] is True
    assert 'Atomicity' in reply['content']
    assert 'Consistency' in reply['content']
    assert 'Isolation' in reply['content']
    assert 'Durability' in reply['content']


def test_demo_provider_additional_curated_topics():
    """Test that DemoAIProvider recognizes Networks, QuickSort, and SOLID topics."""
    provider = DemoAIProvider()

    # Computer Networks
    net_reply = provider.generate_reply([{'role': 'user', 'content': 'Explain the OSI model and TCP handshake'}])
    assert 'Transport' in net_reply['content']
    assert 'Handshake' in net_reply['content']

    # Sorting
    sort_reply = provider.generate_reply([{'role': 'user', 'content': 'Compare quicksort and mergesort time complexity'}])
    assert 'QuickSort' in sort_reply['content']
    assert 'MergeSort' in sort_reply['content']

    # OOP & Design Patterns
    oop_reply = provider.generate_reply([{'role': 'user', 'content': 'What are the SOLID design patterns?'}])
    assert 'Single Responsibility' in oop_reply['content']
    assert 'Open/Closed' in oop_reply['content']

    # Git
    git_reply = provider.generate_reply([{'role': 'user', 'content': 'Difference between git merge and rebase'}])
    assert 'merge' in git_reply['content'].lower()
    assert 'rebase' in git_reply['content'].lower()


def test_gemini_provider_requires_api_key():
    """Test that instantiating GeminiAIProvider without key raises AIConfigurationError."""
    with pytest.raises(AIConfigurationError):
        GeminiAIProvider(api_key="")


def test_openai_provider_requires_api_key():
    """Test that instantiating OpenAIAIProvider without key raises AIConfigurationError."""
    with pytest.raises(AIConfigurationError):
        OpenAIAIProvider(api_key="")


def test_get_ai_provider_fallback_to_demo():
    """Test that get_ai_provider gracefully falls back to DemoAIProvider when keys missing."""
    provider = get_ai_provider('gemini')
    # If GEMINI_API_KEY is not in env, it should fall back to demo
    assert provider.is_demo is True
    assert provider.provider_name == 'demo'
