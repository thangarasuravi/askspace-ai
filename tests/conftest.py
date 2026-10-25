"""Pytest fixtures for AskSpace AI testing suite."""

import os
import sys
from pathlib import Path

# Ensure project root is in sys.path
project_root = Path(__file__).resolve().parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Isolate test environment to offline Demo mode
os.environ['AI_PROVIDER'] = 'demo'
os.environ['GEMINI_API_KEY'] = ''
os.environ['OPENAI_API_KEY'] = ''

import pytest
from app import create_app
from app.config import TestConfig
from app.extensions import db
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.notebook import NotebookEntry
from app.models.preference import UserPreference


@pytest.fixture
def app():
    """Create and configure a clean Flask app instance for testing."""
    test_app = create_app(TestConfig)
    
    with test_app.app_context():
        db.create_all()
        yield test_app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Test client for issuing requests."""
    return app.test_client()


@pytest.fixture
def sample_conversation(app):
    """Seed a sample conversation with messages for testing."""
    with app.app_context():
        conv = Conversation(title="Algorithms Deep Dive", category="Coding")
        db.session.add(conv)
        db.session.commit()

        msg1 = Message(conversation_id=conv.id, role="user", content="Explain binary search")
        msg2 = Message(conversation_id=conv.id, role="assistant", content="Binary search runs in O(log n) time.")
        db.session.add_all([msg1, msg2])
        db.session.commit()

        return conv.id
