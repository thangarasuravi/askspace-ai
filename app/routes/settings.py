"""Preferences and settings API endpoints."""

from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.preference import UserPreference
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.notebook import NotebookEntry

settings_bp = Blueprint('settings', __name__)
ALLOWED_PREFERENCE_KEYS = {
    'theme',
    'system_tone',
    'preferred_category',
    'stream_responses',
    'code_font_ligatures'
}


@settings_bp.route('/preferences', methods=['GET'])
def get_preferences():
    """Retrieve all user preferences with sensible defaults."""
    all_prefs = UserPreference.query.all()
    prefs_map = {p.preference_key: p.preference_value for p in all_prefs}

    # Populate defaults
    defaults = {
        'theme': 'dark',
        'system_tone': 'balanced',
        'preferred_category': 'General',
        'stream_responses': 'false',
        'code_font_ligatures': 'true'
    }
    for k, v in defaults.items():
        if k not in prefs_map:
            prefs_map[k] = v

    # Add workspace stats
    stats = {
        'total_conversations': Conversation.query.count(),
        'total_messages': Message.query.count(),
        'total_notebook_entries': NotebookEntry.query.count()
    }

    return jsonify({
        'success': True,
        'preferences': prefs_map,
        'stats': stats
    }), 200


@settings_bp.route('/preferences', methods=['PATCH'])
def update_preferences():
    """Update one or more user preferences."""
    if not request.is_json:
        return jsonify({'success': False, 'error': 'JSON payload required.'}), 400

    payload = request.get_json() or {}
    updated = {}

    for key, value in payload.items():
        if key in ALLOWED_PREFERENCE_KEYS:
            val_str = str(value).strip().lower()
            if key == 'theme' and val_str not in ('dark', 'light'):
                continue
            if key == 'system_tone' and val_str not in ('balanced', 'concise', 'academic'):
                continue

            UserPreference.set(key, val_str)
            updated[key] = val_str

    return jsonify({
        'success': True,
        'updated': updated
    }), 200
