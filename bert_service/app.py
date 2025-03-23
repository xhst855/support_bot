from fastapi import FastAPI, Request
from model import load_model, predict
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s: %(message)s',
)
logger = logging.getLogger(__name__)

app = FastAPI()

logger.info("Loading BERT model...")
model, tokenizer = load_model()
logger.info("Model loaded successfully.")

@app.post("/predict")
async def classify(request: Request):
    try:
        data = await request.json()
        text = data.get("text", "")

        logger.info(f"Received text: {text}")

        category = predict(text, model, tokenizer)

        logger.info(f"Predicted category: {category}")
        return {"category": category}
    except Exception as e:
        logger.exception(f"Error during prediction: {e}")
        return {"error": "Prediction failed"}
