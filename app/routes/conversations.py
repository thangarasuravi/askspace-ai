"""Conversations API endpoints."""

from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.conversation import Conversation
from app.models.message import Message

conversations_bp = Blueprint('conversations', __name__)
VALID_CATEGORIES = {'All', 'Study', 'Coding', 'Career', 'General'}


@conversations_bp.route('/conversations', methods=['GET'])
def list_conversations():
    """List all conversations with optional category filter and keyword search."""
    category = request.args.get('category', '').strip().capitalize()
    search_query = request.args.get('search', '').strip()

    query = Conversation.query

    if category and category != 'All' and category in VALID_CATEGORIES:
        query = query.filter_by(category=category)

    if search_query:
        # Case-insensitive title search
        query = query.filter(Conversation.title.ilike(f"%{search_query}%"))

    conversations = query.order_by(Conversation.updated_at.desc()).all()

    return jsonify({
        'success': True,
        'count': len(conversations),
        'data': [c.to_dict(include_messages=False) for c in conversations]
    }), 200


@conversations_bp.route('/conversations', methods=['POST'])
def create_conversation():
    """Create a new blank conversation container."""
    payload = request.get_json(silent=True) or {}
    title = (payload.get('title') or 'New Chat').strip()
    category = (payload.get('category') or 'General').strip().capitalize()

    if category not in VALID_CATEGORIES or category == 'All':
        category = 'General'

    if len(title) > 120:
        title = title[:117] + '...'

    conversation = Conversation(title=title, category=category)
    db.session.add(conversation)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': conversation.to_dict(include_messages=True)
    }), 201


@conversations_bp.route('/conversations/<int:conv_id>', methods=['GET'])
def get_conversation(conv_id: int):
    """Retrieve full conversation details and its messages in chronological order."""
    conversation = db.session.get(Conversation, conv_id)
    if not conversation:
        return jsonify({
            'success': False,
            'error': f'Conversation with ID {conv_id} not found.'
        }), 404

    return jsonify({
        'success': True,
        'data': conversation.to_dict(include_messages=True)
    }), 200


@conversations_bp.route('/conversations/<int:conv_id>', methods=['PATCH'])
def update_conversation(conv_id: int):
    """Update title or category of an existing conversation."""
    conversation = db.session.get(Conversation, conv_id)
    if not conversation:
        return jsonify({
            'success': False,
            'error': f'Conversation with ID {conv_id} not found.'
        }), 404

    if not request.is_json:
        return jsonify({'success': False, 'error': 'JSON payload required.'}), 400

    payload = request.get_json() or {}

    if 'title' in payload:
        new_title = str(payload['title']).strip()
        if not new_title:
            return jsonify({'success': False, 'error': 'Title cannot be empty.'}), 400
        if len(new_title) > 120:
            return jsonify({'success': False, 'error': 'Title cannot exceed 120 characters.'}), 400
        conversation.title = new_title

    if 'category' in payload:
        new_category = str(payload['category']).strip().capitalize()
        if new_category in VALID_CATEGORIES and new_category != 'All':
            conversation.category = new_category

    db.session.commit()

    return jsonify({
        'success': True,
        'data': conversation.to_dict(include_messages=False)
    }), 200


@conversations_bp.route('/conversations/<int:conv_id>', methods=['DELETE'])
def delete_conversation(conv_id: int):
    """Delete a conversation and all its associated messages."""
    conversation = db.session.get(Conversation, conv_id)
    if not conversation:
        return jsonify({
            'success': False,
            'error': f'Conversation with ID {conv_id} not found.'
        }), 404

    db.session.delete(conversation)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Conversation {conv_id} deleted successfully.'
    }), 200


@conversations_bp.route('/conversations/<int:conv_id>/export', methods=['GET'])
def export_conversation_markdown(conv_id: int):
    """Export an entire conversation as a formatted Markdown study guide."""
    from flask import Response
    conversation = db.session.get(Conversation, conv_id)
    if not conversation:
        return jsonify({'success': False, 'error': f'Conversation {conv_id} not found.'}), 404

    lines = [
        f"# {conversation.title}",
        f"**Category:** {conversation.category} | **Exported from AskSpace AI**\n",
        "---\n"
    ]

    for msg in conversation.messages:
        role_label = "👤 You" if msg.role == 'user' else "🤖 AskSpace AI"
        timestamp = msg.created_at.strftime("%Y-%m-%d %H:%M:%S") if msg.created_at else ""
        lines.append(f"### {role_label} *({timestamp})*:\n")
        lines.append(f"{msg.content}\n")
        lines.append("---\n")

    md_content = "\n".join(lines)
    clean_filename = "".join(c for c in conversation.title if c.isalnum() or c in (' ', '_', '-')).strip().replace(' ', '_')[:30] or f"chat_{conv_id}"

    return Response(
        md_content,
        mimetype="text/markdown",
        headers={"Content-Disposition": f"attachment; filename=AskSpace_{clean_filename}.md"}
    )
