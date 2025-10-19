from fastapi import FastAPI
from adapters.llm import LLMRouter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
router = LLMRouter()

@app.get("/health")
async def health_check():
    logger.info("Health check")
    return {"status": "ok"}

@app.post("/insights/summary")
async def generate_summary(prompt: str, model: str = "openai"):
    logger.info("Résumé pour: %s, modèle: %s", prompt, model)
    response = await router.query(prompt, model)
    return {"summary": response or "Erreur"}

@app.get("/insights/weak_signals/{keyword}")
async def analyze_weak_signals(keyword: str, platform: str = "x"):
    logger.info("Signaux faibles: %s, plateforme: %s", keyword, platform)
    result = await router.analyze_weak_signals(keyword, platform)
    return result or {"error": "Erreur"}