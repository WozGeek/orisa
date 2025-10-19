
import openai
import os
import json
import asyncio
from dotenv import load_dotenv
from typing import Optional, Dict
import logging
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
XAI_API_KEY = os.getenv("XAI_API_KEY")
X_API_KEY = os.getenv("X_API_KEY")

class XAIClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.x.ai/v1"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def create(self, model: str, messages: list, max_tokens: int, temperature: float) -> Dict:
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "stream": False
        }
        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers=self.headers,
                json=payload
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error("Erreur xAI API: %s", str(e))
            raise

class LLMRouter:
    def __init__(self):
        self.openai = openai.Client(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
        self.xai = XAIClient(api_key=XAI_API_KEY) if XAI_API_KEY else None
        os.makedirs("cache", exist_ok=True)
        logger.info("LLMRouter: OpenAI %s, xAI %s", 
                    "disponible" if self.openai else "non configuré", 
                    "disponible" if self.xai else "non configuré")

    async def query(self, prompt: str, model: str = "openai") -> Optional[str]:
        try:
            if model == "openai" and self.openai:
                logger.info("Appel OpenAI: %s", prompt)
                response = self.openai.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                    temperature=0.7
                )
                return response.choices[0].message.content
            elif model == "xai" and self.xai:
                logger.info("Appel xAI: %s", prompt)
                response = self.xai.create(
                    model="grok-4-latest",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=500,
                    temperature=0.7
                )
                return response["choices"][0]["message"]["content"]
            logger.warning("Modèle %s non configuré", model)
            return None
        except Exception as e:
            logger.error("Erreur LLM %s: %s", model, str(e))
            return None

    async def analyze_weak_signals(self, keyword: str, platform: str = "x") -> Optional[Dict]:
        try:
            cache_file = f"cache/{keyword.replace(' ', '_')}.json"
            if os.path.exists(cache_file):
                with open(cache_file, 'r') as f:
                    logger.info("Cache hit: %s", keyword)
                    return json.load(f)
            if platform == "x":
                logger.info("Scraping X: %s", keyword)
                prompt = f"Recherche sur X les mentions de '{keyword}' et résume les tendances en 50 mots."
                summary = await self.query(prompt, model="xai")
                result = {"keyword": keyword, "summary": summary, "count": None}
                with open(cache_file, 'w') as f:
                    json.dump(result, f)
                return result
            logger.warning("Plateforme %s non supportée", platform)
            return None
        except Exception as e:
            logger.error("Erreur signaux faibles %s: %s", platform, str(e))
            return None

async def main():
    router = LLMRouter()
    prompt = "Résume en 50 mots : Les ventes à Lagos ont augmenté de 20% en 2025."
    response = await router.query(prompt, model="xai")
    print("Résumé (xAI):", response)
    weak_signals = await router.analyze_weak_signals("solaire Kenya", platform="x")
    print("Signaux faibles:", weak_signals)

if __name__ == "__main__":
    asyncio.run(main())
