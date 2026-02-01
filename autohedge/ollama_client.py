"""
Ollama client for AutoHedge
"""

import requests
from typing import List, Dict, Optional
import os


class OllamaClient:
    """Simple Ollama client for AutoHedge"""
    
    def __init__(
        self, 
        base_url: Optional[str] = None,
        model: Optional[str] = None
    ):
        self.base_url = base_url or os.getenv("OLLAMA_URL", "http://ollama:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
        
        print(f"🔗 Connecting to Ollama at: {self.base_url}")
        print(f"📦 Using model: {self.model}")
        
        self._verify_connection()
    
    def _verify_connection(self):
        """Verify Ollama is running and model is available"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            
            models = response.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            
            model_found = False
            for available_model in model_names:
                if self.model in available_model or available_model in self.model:
                    model_found = True
                    break
            
            if not model_found:
                print(f"⚠️  Model '{self.model}' not found.")
                print(f"📋 Available models: {', '.join(model_names)}")
            else:
                print(f"✅ Connected to Ollama - model '{self.model}' is available")
                
        except requests.exceptions.ConnectionError:
            print(f"⚠️  Cannot connect to Ollama at {self.base_url}")
        except Exception as e:
            print(f"⚠️  Ollama connection warning: {e}")
    
    def generate(self, prompt: str, system: Optional[str] = None) -> str:
        """Generate completion using Ollama"""
        url = f"{self.base_url}/api/generate"
        
        full_prompt = prompt
        if system:
            full_prompt = f"{system}\n\n{prompt}"
        
        payload = {
            "model": self.model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 1000
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except requests.exceptions.ConnectionError:
            print(f"❌ Connection error: Cannot reach {self.base_url}")
            return ""
        except requests.exceptions.Timeout:
            print(f"⏱️  Request timeout")
            return ""
        except Exception as e:
            print(f"❌ Ollama error: {e}")
            return ""
    
    def chat(self, messages: List[Dict[str, str]]) -> str:
        """Chat completion using Ollama"""
        url = f"{self.base_url}/api/chat"
        
        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 1000
            }
        }
        
        try:
            response = requests.post(url, json=payload, timeout=120)
            response.raise_for_status()
            result = response.json()
            return result.get("message", {}).get("content", "")
        except Exception as e:
            print(f"❌ Ollama chat error: {e}")
            return ""
