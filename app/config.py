import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env if present
basedir = Path(__file__).resolve().parent.parent
load_dotenv(basedir / '.env')


class Config:
    """Base application configuration."""
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-askspace-ai-portfolio-2026')
    
    # Instance directory for database storage (use /tmp on Vercel/serverless)
    is_serverless = os.environ.get('VERCEL') == '1' or os.environ.get('AWS_LAMBDA_FUNCTION_NAME') is not None
    INSTANCE_PATH = Path('/tmp') if is_serverless else (basedir / 'instance')
    
    # SQLite default database path
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        f"sqlite:///{INSTANCE_PATH / 'askspace.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Security: limit request body to 2MB
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024
    
    # AI Provider configuration ('demo', 'gemini', 'openai')
    AI_PROVIDER = os.environ.get('AI_PROVIDER', 'demo').lower()
    
    GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY', '')
    GEMINI_MODEL = os.environ.get('GEMINI_MODEL', 'gemini-3.5-flash')
    
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY', '')
    OPENAI_MODEL = os.environ.get('OPENAI_MODEL', 'gpt-4o-mini')
    
    # Message constraints
    MAX_MESSAGE_LENGTH = 8000
    MAX_CONVERSATION_TITLE_LENGTH = 120


class TestConfig(Config):
    """Configuration for automated test suite."""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    AI_PROVIDER = 'demo'
    WTF_CSRF_ENABLED = False
