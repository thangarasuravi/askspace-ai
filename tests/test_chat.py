"""Test chat API, message persistence, title generation, and demo mode."""

import json
from app.models.conversation import Conversation
from app.models.message import Message


def test_chat_creates_new_conversation_and_autotitles(client):
    """Sending a message without conversation_id creates a conversation and titles it."""
    payload = {
        'message': 'Explain how the binary search algorithm works in detail',
        'category': 'Coding'
    }
    res = client.post('/api/chat', json=payload)
    assert res.status_code == 201

    data = res.get_json()
    assert data['success'] is True
    assert data['data']['conversation_id'] is not None
    assert 'binary search' in data['data']['conversation_title'].lower()
    assert data['data']['user_message']['content'] == payload['message']
    assert 'Binary Search' in data['data']['assistant_message']['content']
    assert data['data']['meta']['is_demo'] is True


def test_chat_in_existing_conversation(client, sample_conversation):
    """Sending a message with existing conversation_id appends to history."""
    payload = {
        'conversation_id': sample_conversation,
        'message': 'What is the space complexity?'
    }
    res = client.post('/api/chat', json=payload)
    assert res.status_code == 200

    data = res.get_json()
    assert data['data']['conversation_id'] == sample_conversation

    # Check that messages persisted
    res_conv = client.get(f'/api/conversations/{sample_conversation}')
    messages = res_conv.get_json()['data']['messages']
    assert len(messages) == 4  # 2 original + 1 user + 1 assistant


def test_chat_empty_message_validation(client):
    """Test rejection of empty message string."""
    res = client.post('/api/chat', json={'message': '   '})
    assert res.status_code == 400
    assert 'required' in res.get_json()['error']


def test_chat_missing_json(client):
    """Test rejection when payload is not JSON."""
    res = client.post('/api/chat', data="plain text message", content_type='text/plain')
    assert res.status_code == 400
    assert 'must be valid JSON' in res.get_json()['error']


def test_chat_message_length_limit(client):
    """Test rejection of message exceeding 8,000 characters."""
    oversized = "a" * 8001
    res = client.post('/api/chat', json={'message': oversized})
    assert res.status_code == 400
    assert 'limit' in res.get_json()['error']


def test_chat_nonexistent_conversation_id(client):
    """Test 404 when user provides non-existent conversation ID."""
    res = client.post('/api/chat', json={'conversation_id': 999999, 'message': 'Hello?'})
    assert res.status_code == 404


def test_chat_demo_mode_unsupported_query(client):
    """Test demo mode response for an unmapped question provides honest disclosure."""
    payload = {'message': 'Tell me a story about a dragon in space'}
    res = client.post('/api/chat', json=payload)
    assert res.status_code == 201

    data = res.get_json()
    assistant_text = data['data']['assistant_message']['content']
    assert "Demo Mode" in assistant_text
    assert "running in **Demo Mode**" in assistant_text
    assert "GEMINI_API_KEY" in assistant_text


def test_service_status_endpoint(client):
    """Test /api/status metadata."""
    res = client.get('/api/status')
    assert res.status_code == 200
    data = res.get_json()['data']
    assert data['app_name'] == 'AskSpace AI'
    assert data['is_demo'] is True
    assert 'Study' in data['categories']
