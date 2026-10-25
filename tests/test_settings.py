"""Test user preferences and workspace settings API."""

import json


def test_get_default_preferences(client):
    """Test retrieving initial preferences with default values."""
    res = client.get('/api/preferences')
    assert res.status_code == 200

    data = res.get_json()
    assert data['success'] is True
    assert 'preferences' in data
    assert data['preferences']['theme'] in ('dark', 'light')
    assert 'stats' in data
    assert 'total_conversations' in data['stats']


def test_update_theme_preference(client):
    """Test toggling and persisting theme preference."""
    res = client.patch('/api/preferences', json={'theme': 'light'})
    assert res.status_code == 200
    assert res.get_json()['updated']['theme'] == 'light'

    # Verify persistence
    res_get = client.get('/api/preferences')
    assert res_get.get_json()['preferences']['theme'] == 'light'

    # Switch back to dark
    res_dark = client.patch('/api/preferences', json={'theme': 'dark'})
    assert res_dark.status_code == 200
    assert res_dark.get_json()['updated']['theme'] == 'dark'


def test_update_assistant_tone(client):
    """Test updating assistant tone."""
    res = client.patch('/api/preferences', json={'system_tone': 'academic'})
    assert res.status_code == 200
    assert res.get_json()['updated']['system_tone'] == 'academic'


def test_ignore_disallowed_keys(client):
    """Test that unauthorized keys are safely ignored."""
    res = client.patch('/api/preferences', json={'admin_override': 'true', 'theme': 'dark'})
    assert res.status_code == 200
    assert 'admin_override' not in res.get_json()['updated']
