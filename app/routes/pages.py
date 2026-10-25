"""HTML Template page routes for AskSpace AI."""

from flask import Blueprint, render_template
from app.models.preference import UserPreference
from app.services.ai_provider import get_ai_provider

pages_bp = Blueprint('pages', __name__)


@pages_bp.route('/', methods=['GET'])
def index():
    """Render the primary AskSpace AI Chat Workspace."""
    theme = UserPreference.get('theme', 'dark')
    provider = get_ai_provider()
    return render_template(
        'index.html',
        active_page='chat',
        theme=theme,
        provider_name=provider.provider_name,
        is_demo=provider.is_demo,
        model_name=provider.model_name
    )


@pages_bp.route('/notebook', methods=['GET'])
def notebook_page():
    """Render the personal searchable notebook."""
    theme = UserPreference.get('theme', 'dark')
    provider = get_ai_provider()
    return render_template(
        'notebook.html',
        active_page='notebook',
        theme=theme,
        provider_name=provider.provider_name,
        is_demo=provider.is_demo,
        model_name=provider.model_name
    )


@pages_bp.route('/settings', methods=['GET'])
def settings_page():
    """Render the settings and configuration panel."""
    theme = UserPreference.get('theme', 'dark')
    provider = get_ai_provider()
    return render_template(
        'settings.html',
        active_page='settings',
        theme=theme,
        provider_name=provider.provider_name,
        is_demo=provider.is_demo,
        model_name=provider.model_name
    )
