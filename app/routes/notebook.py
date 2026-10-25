"""Notebook API endpoints for saving and managing curated notes."""

from datetime import datetime
from flask import Blueprint, request, jsonify
from app.extensions import db
from app.models.notebook import NotebookEntry
from app.models.message import Message
from app.models.conversation import Conversation

notebook_bp = Blueprint('notebook', __name__)
VALID_CATEGORIES = {'All', 'Study', 'Coding', 'Career', 'General'}


@notebook_bp.route('/notebook', methods=['GET'])
def list_notes():
    """Retrieve all notebook entries with optional search filter."""
    search_query = request.args.get('search', '').strip()
    category = request.args.get('category', '').strip().capitalize()

    query = NotebookEntry.query

    if category and category != 'All' and category in VALID_CATEGORIES:
        query = query.filter_by(category=category)

    if search_query:
        query = query.filter(
            (NotebookEntry.title.ilike(f"%{search_query}%")) |
            (NotebookEntry.content.ilike(f"%{search_query}%"))
        )

    entries = query.order_by(NotebookEntry.created_at.desc()).all()

    return jsonify({
        'success': True,
        'count': len(entries),
        'data': [e.to_dict() for e in entries]
    }), 200


@notebook_bp.route('/notebook', methods=['POST'])
def save_note():
    """Save an answer or snippet to the personal notebook."""
    if not request.is_json:
        return jsonify({'success': False, 'error': 'Request payload must be valid JSON.'}), 400

    payload = request.get_json() or {}
    title = (payload.get('title') or '').strip()
    content = (payload.get('content') or '').strip()
    category = (payload.get('category') or 'General').strip().capitalize()
    message_id = payload.get('message_id')
    conversation_id = payload.get('conversation_id')

    if not title:
        return jsonify({'success': False, 'error': 'Title is required.'}), 400

    if not content:
        return jsonify({'success': False, 'error': 'Content is required.'}), 400

    if len(title) > 200:
        title = title[:197] + '...'

    if category not in VALID_CATEGORIES or category == 'All':
        category = 'General'

    # Sanitize message_id and conversation_id
    if message_id is not None:
        try:
            message_id = int(message_id)
        except (ValueError, TypeError):
            message_id = None

    if conversation_id is not None:
        try:
            conversation_id = int(conversation_id)
        except (ValueError, TypeError):
            conversation_id = None

    entry = NotebookEntry(
        title=title,
        content=content,
        category=category,
        message_id=message_id,
        conversation_id=conversation_id
    )
    db.session.add(entry)
    db.session.commit()

    return jsonify({
        'success': True,
        'data': entry.to_dict()
    }), 201


@notebook_bp.route('/notebook/<int:entry_id>', methods=['DELETE'])
def delete_note(entry_id: int):
    """Delete a note from the notebook."""
    entry = db.session.get(NotebookEntry, entry_id)
    if not entry:
        return jsonify({
            'success': False,
            'error': f'Notebook entry with ID {entry_id} not found.'
        }), 404

    db.session.delete(entry)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'Note {entry_id} deleted successfully.'
    }), 200


@notebook_bp.route('/notebook/export', methods=['GET'])
def export_notebook_markdown():
    """Export all notebook entries as a compiled Markdown study guide booklet."""
    from flask import Response
    category = request.args.get('category', '').strip().capitalize()
    query = NotebookEntry.query
    if category and category != 'All' and category in VALID_CATEGORIES:
        query = query.filter_by(category=category)

    entries = query.order_by(NotebookEntry.created_at.desc()).all()

    lines = [
        "# AskSpace AI — Personal Technical Notebook",
        f"**Compiled on:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC",
        f"**Total Entries:** {len(entries)}\n",
        "---\n"
    ]

    for idx, note in enumerate(entries, start=1):
        lines.append(f"## {idx}. {note.title}")
        lines.append(f"**Category:** `{note.category}` | **Saved:** {note.created_at.strftime('%Y-%m-%d')}\n")
        lines.append(f"{note.content}\n")
        lines.append("---\n")

    md_content = "\n".join(lines)
    return Response(
        md_content,
        mimetype="text/markdown",
        headers={"Content-Disposition": "attachment; filename=AskSpace_Study_Notebook.md"}
    )
