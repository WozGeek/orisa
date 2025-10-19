from fastapi import FastAPI
from pydantic import BaseModel
from adapters.llm import LLMRouter
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()
router = LLMRouter()

class SummaryRequest(BaseModel):
    prompt: str
    model: str = "openai"

@app.get("/health")
async def health_check():
    logger.info("Health check")
    return {"status": "ok"}

@app.post("/insights/summary")
async def generate_summary(request: SummaryRequest):
    logger.info("Résumé pour: %s, modèle: %s", request.prompt, request.model)
    response = await router.query(request.prompt, request.model)
    return {"summary": response or "Erreur"}

@app.get("/insights/weak_signals/{keyword}")
async def analyze_weak_signals(keyword: str, platform: str = "x"):
    logger.info("Signaux faibles: %s, plateforme: %s", keyword, platform)
    result = await router.analyze_weak_signals(keyword, platform)
    return result or {"error": "Erreur"}