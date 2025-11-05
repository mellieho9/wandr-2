"""
Configuration Settings
Loads environment variables and provides application configuration.
"""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application configuration loaded from environment variables"""
    
    # Notion OAuth Configuration
    NOTION_CLIENT_ID = os.getenv('NOTION_CLIENT_ID')
    NOTION_CLIENT_SECRET = os.getenv('NOTION_CLIENT_SECRET')
    NOTION_REDIRECT_URI = os.getenv('NOTION_REDIRECT_URI')
    
    # OpenAI Whisper API
    WHISPER_API_KEY = os.getenv('WHISPER_API_KEY')
    
    # Google Gemini API
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    
    # Google Cloud Vision API
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
    
    # PostgreSQL Database
    DATABASE_URL = os.getenv('DATABASE_URL')
    
    # Grafana Cloud Logging
    GRAFANA_CLOUD_API_KEY = os.getenv('GRAFANA_CLOUD_API_KEY')
    GRAFANA_CLOUD_URL = os.getenv('GRAFANA_CLOUD_URL')
    
    # Flask Configuration
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    FLASK_SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key-change-in-production')
    
    # Logging
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Redis Configuration (Google Cloud Memorystore for Production)
    # Leave empty for local development (will use in-memory storage)
    REDIS_HOST = os.getenv('REDIS_HOST')
    REDIS_PORT = int(os.getenv('REDIS_PORT', '6379'))
    
    # Processing Configuration
    POLLING_INTERVAL_SECONDS = int(os.getenv('POLLING_INTERVAL_SECONDS', '60'))
    MAX_CONCURRENT_PROCESSING = int(os.getenv('MAX_CONCURRENT_PROCESSING', '5'))
    
    def validate(self):
        """
        Validates that all required configuration is present.
        Raises ValueError if required settings are missing.
        """
        required_settings = [
            'NOTION_CLIENT_ID',
            'NOTION_CLIENT_SECRET',
            'NOTION_REDIRECT_URI',
            'WHISPER_API_KEY',
            'GEMINI_API_KEY',
            'DATABASE_URL'
        ]
        
        missing = []
        for setting in required_settings:
            if not getattr(self, setting):
                missing.append(setting)
        
        if missing:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing)}"
            )
    
    def __repr__(self):
        """String representation (hides sensitive values)"""
        return f"<Settings env={self.FLASK_ENV} log_level={self.LOG_LEVEL}>"
