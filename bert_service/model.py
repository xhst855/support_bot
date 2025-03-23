from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch


def load_model():
    model_name = "cointegrated/rubert-tiny2-cedr-emotion-detection"  # Пример, заменим позже!
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    model.eval()  # Важно: ставим в режим инференса
    return model, tokenizer


def predict(text, model, tokenizer):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
    with torch.no_grad():
        outputs = model(**inputs)
    prediction = torch.argmax(outputs.logits, dim=1).item()

    # Здесь можно сопоставить label к читаемой категории
    if prediction == 0:
        return "AML"
    elif prediction == 1:
        return "Finance"
    else:
        return "Question"
