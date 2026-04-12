import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    DEBUG = os.getenv("DEBUG", "False") == "True"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    MAX_FIX_ATTEMPTS = int(os.getenv("MAX_FIX_ATTEMPTS", "5"))
    TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", "30"))

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

# Default config
config = DevelopmentConfig()
