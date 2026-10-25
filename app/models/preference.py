from datetime import datetime
from app.extensions import db


class UserPreference(db.Model):
    """Key-value user preference settings."""
    __tablename__ = 'user_preferences'

    id = db.Column(db.Integer, primary_key=True)
    preference_key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    preference_value = db.Column(db.Text, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    @classmethod
    def get(cls, key: str, default: str = None) -> str:
        """Fetch preference value by key with fallback default."""
        pref = cls.query.filter_by(preference_key=key).first()
        return pref.preference_value if pref else default

    @classmethod
    def set(cls, key: str, value: str):
        """Set or update preference key-value pair."""
        pref = cls.query.filter_by(preference_key=key).first()
        if pref:
            pref.preference_value = str(value)
        else:
            pref = cls(preference_key=key, preference_value=str(value))
            db.session.add(pref)
        db.session.commit()
        return pref

    def to_dict(self):
        """Serialize preference to dictionary."""
        return {
            'key': self.preference_key,
            'value': self.preference_value,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
