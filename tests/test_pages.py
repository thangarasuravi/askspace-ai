"""Test HTML page routes and security headers."""


def test_index_page(client):
    """Test that the homepage renders successfully with security headers."""
    response = client.get('/')
    assert response.status_code == 200
    assert b"AskSpace" in response.data
    assert b"What would you like to explore?" in response.data
    assert response.headers.get('X-Content-Type-Options') == 'nosniff'
    assert response.headers.get('X-Frame-Options') == 'DENY'


def test_notebook_page(client):
    """Test that notebook view renders correctly."""
    response = client.get('/notebook')
    assert response.status_code == 200
    assert b"Personal Notebook" in response.data
    assert b"notebookSearchInput" in response.data


def test_settings_page(client):
    """Test that settings view renders correctly."""
    response = client.get('/settings')
    assert response.status_code == 200
    assert b"Workspace Settings" in response.data
    assert b"AI Provider & Engine Status" in response.data
