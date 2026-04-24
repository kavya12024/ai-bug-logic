import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Base configuration"""
    DEBUG = os.getenv("DEBUG", "False") == "True"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    MAX_FIX_ATTEMPTS = int(os.getenv("MAX_FIX_ATTEMPTS", "3"))
    TIMEOUT_SECONDS = int(os.getenv("TIMEOUT_SECONDS", "15"))
    USE_OLLAMA = os.getenv("USE_OLLAMA", "True") == "True"
    OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "codellama:7b")
    GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False

# Default config
config = DevelopmentConfig()
