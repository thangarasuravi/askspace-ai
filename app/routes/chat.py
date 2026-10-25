"""Chat API endpoints."""

from flask import Blueprint, request, jsonify
from app.services.chat_service import ChatService
from app.services.ai_provider import get_ai_provider

chat_bp = Blueprint('chat', __name__)


@chat_bp.route('/chat', methods=['POST'])
def send_chat_message():
    """Process incoming chat message and return assistant response."""
    if not request.is_json:
        return jsonify({
            'success': False,
            'error': 'Request payload must be valid JSON.'
        }), 400

    payload = request.get_json() or {}
    message_content = payload.get('message')
    conversation_id = payload.get('conversation_id')
    category = payload.get('category')

    if not message_content or not isinstance(message_content, str) or not message_content.strip():
        return jsonify({
            'success': False,
            'error': 'The "message" field is required and cannot be empty.'
        }), 400

    if len(message_content) > 8000:
        return jsonify({
            'success': False,
            'error': 'Message length exceeds the 8,000 character limit.'
        }), 400

    # Parse conversation_id if passed as string
    if conversation_id is not None:
        try:
            conversation_id = int(conversation_id)
        except (ValueError, TypeError):
            return jsonify({
                'success': False,
                'error': 'conversation_id must be a valid integer.'
            }), 400

    try:
        result = ChatService.process_chat_message(
            message_content=message_content,
            conversation_id=conversation_id,
            category=category
        )
        status_code = 201 if result.get('is_new') else 200
        return jsonify({
            'success': True,
            'data': result
        }), status_code
    except ValueError as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404 if 'not found' in str(e).lower() else 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to process chat message: {str(e)}'
        }), 500


@chat_bp.route('/status', methods=['GET'])
def get_service_status():
    """Return backend AI provider status and application metadata."""
    provider = get_ai_provider()
    return jsonify({
        'success': True,
        'data': {
            'app_name': 'AskSpace AI',
            'version': '1.0.0',
            'provider': provider.provider_name,
            'model': provider.model_name,
            'is_demo': provider.is_demo,
            'categories': ['Study', 'Coding', 'Career', 'General'],
            'max_message_length': 8000,
            'notice': 'AI-generated content can be inaccurate. Verify important academic or code details.'
        }
    }), 200
