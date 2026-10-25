"""Test conversations API endpoints."""

import json
from app.models.conversation import Conversation


def test_create_conversation(client):
    """Test manual conversation creation."""
    payload = {'title': 'Database Transactions', 'category': 'Study'}
    res = client.post('/api/conversations', json=payload)
    assert res.status_code == 201

    data = res.get_json()
    assert data['success'] is True
    assert data['data']['title'] == 'Database Transactions'
    assert data['data']['category'] == 'Study'


def test_list_conversations_with_filter(client, sample_conversation):
    """Test listing and filtering conversations by category."""
    # List all
    res = client.get('/api/conversations')
    assert res.status_code == 200
    data = res.get_json()
    assert data['count'] >= 1

    # Filter matching category
    res_match = client.get('/api/conversations?category=Coding')
    data_match = res_match.get_json()
    assert data_match['count'] >= 1
    assert data_match['data'][0]['category'] == 'Coding'

    # Filter non-matching category
    res_none = client.get('/api/conversations?category=Career')
    data_none = res_none.get_json()
    assert data_none['count'] == 0


def test_get_conversation_messages(client, sample_conversation):
    """Test retrieving conversation details and message list."""
    res = client.get(f'/api/conversations/{sample_conversation}')
    assert res.status_code == 200

    data = res.get_json()
    assert data['success'] is True
    assert data['data']['id'] == sample_conversation
    assert len(data['data']['messages']) == 2
    assert data['data']['messages'][0]['role'] == 'user'
    assert data['data']['messages'][1]['role'] == 'assistant'


def test_get_invalid_conversation(client):
    """Test 404 response for non-existent conversation ID."""
    res = client.get('/api/conversations/999999')
    assert res.status_code == 404
    assert res.get_json()['success'] is False


def test_update_conversation(client, sample_conversation):
    """Test renaming conversation title and updating category."""
    update_payload = {'title': 'Updated Algorithms Guide', 'category': 'Study'}
    res = client.patch(f'/api/conversations/{sample_conversation}', json=update_payload)
    assert res.status_code == 200

    data = res.get_json()
    assert data['success'] is True
    assert data['data']['title'] == 'Updated Algorithms Guide'
    assert data['data']['category'] == 'Study'


def test_update_conversation_validation(client, sample_conversation):
    """Test rejection of empty title during rename."""
    res = client.patch(f'/api/conversations/{sample_conversation}', json={'title': '   '})
    assert res.status_code == 400
    assert 'cannot be empty' in res.get_json()['error']


def test_delete_conversation(client, sample_conversation):
    """Test deleting conversation and cascade removal."""
    res = client.delete(f'/api/conversations/{sample_conversation}')
    assert res.status_code == 200
    assert res.get_json()['success'] is True

    # Verify conversation is gone
    res_check = client.get(f'/api/conversations/{sample_conversation}')
    assert res_check.status_code == 404


def test_export_conversation(client, sample_conversation):
    """Test exporting conversation as markdown file."""
    res = client.get(f'/api/conversations/{sample_conversation}/export')
    assert res.status_code == 200
    assert res.headers.get('Content-Type') == 'text/markdown; charset=utf-8'
    assert b"Algorithms Deep Dive" in res.data
    assert b"Explain binary search" in res.data
