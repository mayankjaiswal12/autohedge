"""
Configuration settings for AutoHedge
"""

import os


class Config:
    """AutoHedge configuration"""
    
    # Ollama settings
    OLLAMA_URL = "http://ollama:11434"
    OLLAMA_MODEL = "qwen2.5:7b"
    
    # Trading settings
    DEFAULT_ALLOCATION = 50000.0
    DEFAULT_STOP_LOSS_PCT = 5.0
    DEFAULT_RISK_LEVEL = 5
    
    # Output settings
    OUTPUT_DIR = "outputs"
    WORKSPACE_DIR = "agent_workspace"
    
    # API settings
    REQUEST_TIMEOUT = 120
    TEMPERATURE = 0.7
    MAX_TOKENS = 1000
    
    @staticmethod
    def get_ollama_url():
        """Get Ollama URL from environment or default"""
        return os.getenv("OLLAMA_URL", Config.OLLAMA_URL)
    
    @staticmethod
    def get_ollama_model():
        """Get Ollama model from environment or default"""
        return os.getenv("OLLAMA_MODEL", Config.OLLAMA_MODEL)
