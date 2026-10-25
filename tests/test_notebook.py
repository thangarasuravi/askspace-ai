"""Test personal notebook API endpoints."""

import json


def test_save_and_retrieve_notebook_entry(client, sample_conversation):
    """Test saving a note from a conversation and retrieving it."""
    payload = {
        'title': 'Binary Search Time Complexity',
        'content': 'Worst case: O(log n), Best case: O(1)',
        'category': 'Coding',
        'conversation_id': sample_conversation
    }
    res = client.post('/api/notebook', json=payload)
    assert res.status_code == 201

    entry = res.get_json()['data']
    assert entry['title'] == payload['title']
    assert entry['category'] == 'Coding'

    # Retrieve all notes
    res_list = client.get('/api/notebook')
    assert res_list.status_code == 200
    list_data = res_list.get_json()
    assert list_data['count'] >= 1
    assert list_data['data'][0]['id'] == entry['id']


def test_search_notebook_entries(client):
    """Test keyword search in personal notebook."""
    # Seed two notes
    client.post('/api/notebook', json={'title': 'Flask Blueprints Pattern', 'content': 'Modular routes', 'category': 'Coding'})
    client.post('/api/notebook', json={'title': 'Operating Systems Paging', 'content': 'Virtual memory and frames', 'category': 'Study'})

    # Search for "Flask"
    res = client.get('/api/notebook?search=Flask')
    data = res.get_json()
    assert data['count'] == 1
    assert data['data'][0]['title'] == 'Flask Blueprints Pattern'

    # Search for "Virtual" in content
    res_content = client.get('/api/notebook?search=Virtual')
    assert res_content.get_json()['count'] == 1


def test_notebook_validation_empty_fields(client):
    """Test rejection when title or content is empty."""
    res_no_title = client.post('/api/notebook', json={'title': '', 'content': 'Some content'})
    assert res_no_title.status_code == 400

    res_no_content = client.post('/api/notebook', json={'title': 'A Title', 'content': ''})
    assert res_no_content.status_code == 400


def test_delete_notebook_entry(client):
    """Test removing an entry from the personal notebook."""
    res_create = client.post('/api/notebook', json={'title': 'Note to delete', 'content': 'Temporary'})
    note_id = res_create.get_json()['data']['id']

    # Delete
    res_del = client.delete(f'/api/notebook/{note_id}')
    assert res_del.status_code == 200

    # Ensure it is gone
    res_list = client.get('/api/notebook?search=Temporary')
    assert res_list.get_json()['count'] == 0


def test_delete_nonexistent_notebook_entry(client):
    """Test 404 when deleting note that does not exist."""
    res = client.delete('/api/notebook/999999')
    assert res.status_code == 404


def test_export_notebook_compilation(client):
    """Test exporting all notebook entries as a compiled study markdown file."""
    client.post('/api/notebook', json={'title': 'Big-O Cheat Sheet', 'content': 'O(1) < O(log n)', 'category': 'Study'})
    res = client.get('/api/notebook/export')
    assert res.status_code == 200
    assert res.headers.get('Content-Type') == 'text/markdown; charset=utf-8'
    assert b"AskSpace AI" in res.data
    assert b"Big-O Cheat Sheet" in res.data
