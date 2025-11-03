from fastapi import FastAPI, HTTPException, Header, UploadFile, File
from pydantic import BaseModel
from typing import Optional
import re
from pathlib import Path
from food_mapper import get_ingredient_info
from PIL import Image
import torch
from transformers import AutoProcessor, AutoModelForImageClassification

app = FastAPI(title="VanityOS Skincare API", version="1.0.0")

# API key for authentication
API_KEY = "vanityos_scanner_M1c43ll3kuzemczak0417"

# Load food detection model lazily (on first use)
processor_foodcheck = None
model_foodcheck = None

def load_food_model():
    global processor_foodcheck, model_foodcheck
    if processor_foodcheck is None:
        processor_foodcheck = AutoProcessor.from_pretrained("google/vit-base-patch16-224")
        model_foodcheck = AutoModelForImageClassification.from_pretrained("google/vit-base-patch16-224")


class FoodAnalysis(BaseModel):
    food: str
    is_comedogenic: Optional[bool] = None
    comedogenic_grade: Optional[str] = None
    comedogenic_notes: Optional[str] = None


@app.get("/")
async def root():
    return {
        "message": "VanityOS Skincare API - Healthy Ingredients Hub",
        "endpoints": {
            "/analyze_food": "Analyze if a food ingredient is comedogenic for skin",
            "/analyze_image": "Analyze an uploaded image to detect food",
            "/docs": "Interactive API documentation"
        }
    }


@app.get("/analyze_food", response_model=FoodAnalysis)
async def analyze_food(
    food: str,
    x_api_key: Optional[str] = Header(None, alias="x-api-key")
):
    """
    Analyze a food ingredient for comedogenic properties.
    
    Args:
        food: The name of the food/ingredient to analyze (e.g., "Pumpkin Seeds", "Avocado Oil")
        x_api_key: API key for authentication (in header as 'x-api-key')
    
    Returns:
        FoodAnalysis object with comedogenic information
    """
    # Verify API key
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    
    # Get ingredient information
    info = get_ingredient_info(food)
    
    if info:
        return FoodAnalysis(
            food=food,
            is_comedogenic=info["is_comedogenic"],
            comedogenic_grade=info.get("grade"),
            comedogenic_notes=info.get("notes")
        )
    else:
        # Return unknown if ingredient not found
        return FoodAnalysis(
            food=food,
            is_comedogenic=None,
            comedogenic_grade=None,
            comedogenic_notes="Ingredient not found in database"
        )


@app.post("/analyze_image")
async def analyze_image(file: UploadFile = File(...), x_api_key: str = Header(None)):
    """
    Analyze an uploaded image to detect if it contains food.
    
    Args:
        file: The image file to analyze
        x_api_key: API key for authentication (in header as 'x-api-key')
    
    Returns:
        Dictionary with detected food label if valid food is found
    """
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

    try:
        image = Image.open(file.file)
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid or unreadable image file")

    # Load model if not already loaded
    load_food_model()

    # Step 1: Classify the image (cheap first pass)
    inputs = processor_foodcheck(images=image, return_tensors="pt")
    outputs = model_foodcheck(**inputs)
    probs = torch.nn.functional.softmax(outputs.logits, dim=1)
    pred_id = torch.argmax(probs, dim=1).item()
    label = model_foodcheck.config.id2label[pred_id].lower()

    # Step 2: Simple filter - reject if not likely a food item
    food_keywords = [
        "food", "dish", "meal", "pasta", "salad", "soup", "fruit", "bread",
        "cake", "burger", "pizza", "noodles", "egg", "rice", "fish", "vegetable",
        "seafood", "drink", "coffee", "tea"
    ]

    if not any(keyword in label for keyword in food_keywords):
        raise HTTPException(status_code=400, detail=f"Image not recognized as food (detected: {label}). Please upload a clear food photo.")

    # Step 3: Proceed with your main analysis if food
    return {"food_detected": label, "message": "Valid food photo detected ✅"}


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy"}

