from datetime import datetime
from app.extensions import db


class Conversation(db.Model):
    """Conversation entity grouping chat messages."""
    __tablename__ = 'conversations'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False, default='New Chat')
    category = db.Column(db.String(50), nullable=False, default='General')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    messages = db.relationship(
        'Message',
        backref='conversation',
        cascade='all, delete-orphan',
        order_by='Message.created_at.asc()'
    )
    notebook_entries = db.relationship(
        'NotebookEntry',
        backref='conversation',
        cascade='all, delete-orphan'
    )

    def to_dict(self, include_messages=False):
        """Serialize conversation model to dictionary."""
        data = {
            'id': self.id,
            'title': self.title,
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            'message_count': len(self.messages) if self.messages else 0,
        }
        if include_messages:
            data['messages'] = [m.to_dict() for m in self.messages]
        else:
            # Provide preview snippet from last message
            last_msg = self.messages[-1] if self.messages else None
            data['last_message_preview'] = (
                (last_msg.content[:80] + '...') if last_msg and len(last_msg.content) > 80
                else (last_msg.content if last_msg else '')
            )
        return data
