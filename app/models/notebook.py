from datetime import datetime
from app.extensions import db


class NotebookEntry(db.Model):
    """Saved answer or note curated by the user."""
    __tablename__ = 'notebook_entries'

    id = db.Column(db.Integer, primary_key=True)
    message_id = db.Column(
        db.Integer,
        db.ForeignKey('messages.id', ondelete='SET NULL'),
        nullable=True,
        index=True
    )
    conversation_id = db.Column(
        db.Integer,
        db.ForeignKey('conversations.id', ondelete='SET NULL'),
        nullable=True,
        index=True
    )
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False, default='General')
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Serialize notebook entry to dictionary."""
        return {
            'id': self.id,
            'message_id': self.message_id,
            'conversation_id': self.conversation_id,
            'title': self.title,
            'content': self.content,
            'category': self.category,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }
