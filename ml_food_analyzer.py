"""
ML-based food analysis using TensorFlow/Keras
Loads a trained model to classify food images and match to acne health database
"""

import os
import json
from pathlib import Path
from typing import Optional, Tuple, List, Dict
import numpy as np
from PIL import Image
import tensorflow as tf
from tensorflow import keras


# Global model cache - loaded once and reused
_model_cache = None
_labels_cache = None


def get_model_path() -> str:
    """Get the model path from environment variable or use default"""
    return os.getenv("VANITYOS_MODEL_PATH", "ml/out/vanityos.keras")


def get_labels_path() -> str:
    """Get the labels path from environment variable or use default"""
    return os.getenv("VANITYOS_LABELS_PATH", "ml/out/labels.json")


def load_model_and_labels() -> Tuple[keras.Model, List[str]]:
    """
    Load the Keras model and labels from disk.
    Caches the results so subsequent calls are fast.

    Returns:
        Tuple of (model, labels_list)

    Raises:
        FileNotFoundError: If model or labels file doesn't exist
    """
    global _model_cache, _labels_cache

    # Return cached versions if available
    if _model_cache is not None and _labels_cache is not None:
        return _model_cache, _labels_cache

    # Load model
    model_path = get_model_path()
    if not Path(model_path).exists():
        raise FileNotFoundError(
            f"Model file not found at {model_path}. "
            f"Set VANITYOS_MODEL_PATH environment variable to specify a different path."
        )

    print(f"Loading model from {model_path}...")
    _model_cache = keras.models.load_model(model_path)
    print("Model loaded successfully!")

    # Load labels
    labels_path = get_labels_path()
    if not Path(labels_path).exists():
        raise FileNotFoundError(
            f"Labels file not found at {labels_path}. "
            f"Expected labels.json in the same directory as the model."
        )

    with open(labels_path, 'r') as f:
        labels_data = json.load(f)
        # Handle both list format and dict format
        if isinstance(labels_data, list):
            _labels_cache = labels_data
        elif isinstance(labels_data, dict):
            # If it's a dict like {"0": "apple", "1": "banana"}, convert to list
            _labels_cache = [labels_data[str(i)] for i in range(len(labels_data))]
        else:
            raise ValueError(f"Unexpected labels format in {labels_path}")

    print(f"Loaded {len(_labels_cache)} labels")

    return _model_cache, _labels_cache


def preprocess_image(image_bytes: bytes) -> np.ndarray:
    """
    Preprocess image bytes for model input.

    Args:
        image_bytes: Raw bytes from uploaded file

    Returns:
        Preprocessed numpy array ready for model prediction

    Steps:
        1. Decode bytes with PIL
        2. Convert to RGB
        3. Resize to 224x224
        4. Normalize to [0, 1]
        5. Add batch dimension
    """
    # Open image from bytes
    image = Image.open(image_bytes)

    # Convert to RGB (handles RGBA, grayscale, etc.)
    image = image.convert('RGB')

    # Resize to 224x224 (standard for many models)
    image = image.resize((224, 224))

    # Convert to numpy array
    img_array = np.array(image)

    # Normalize to [0, 1]
    img_array = img_array.astype(np.float32) / 255.0

    # Add batch dimension: (224, 224, 3) -> (1, 224, 224, 3)
    img_array = np.expand_dims(img_array, axis=0)

    return img_array


def predict_food(image_bytes: bytes, top_k: int = 3) -> List[Tuple[str, float]]:
    """
    Run model prediction on image and return top K predictions.

    Args:
        image_bytes: Raw bytes from uploaded file
        top_k: Number of top predictions to return (default: 3)

    Returns:
        List of (label, confidence_score) tuples, sorted by confidence descending
    """
    # Load model and labels
    model, labels = load_model_and_labels()

    # Preprocess image
    img_array = preprocess_image(image_bytes)

    # Run prediction
    predictions = model.predict(img_array, verbose=0)

    # Get probabilities for the first (and only) image in batch
    probs = predictions[0]

    # Get top K indices
    top_indices = np.argsort(probs)[-top_k:][::-1]

    # Build result list
    results = []
    for idx in top_indices:
        label = labels[idx]
        confidence = float(probs[idx])
        results.append((label, confidence))

    return results


def load_acne_food_database() -> List[Dict]:
    """
    Load the acne food database from JSON file.

    Returns:
        List of food entries with ratings, categories, reasons, alternatives
    """
    db_path = Path("data/acne_food_database.json")

    if not db_path.exists():
        raise FileNotFoundError(
            f"Acne food database not found at {db_path}. "
            f"Please ensure data/acne_food_database.json exists."
        )

    with open(db_path, 'r') as f:
        return json.load(f)


def normalize_food_name(name: str) -> str:
    """
    Normalize a food name for matching.

    Args:
        name: Raw food name from model or database

    Returns:
        Normalized name: lowercase, spaces instead of underscores/hyphens, trimmed
    """
    # Convert to lowercase
    normalized = name.lower()

    # Replace underscores and hyphens with spaces
    normalized = normalized.replace('_', ' ').replace('-', ' ')

    # Remove extra whitespace
    normalized = ' '.join(normalized.split())

    return normalized


def match_food(label: str, database: Optional[List[Dict]] = None) -> Optional[Dict]:
    """
    Match a predicted label to an entry in the acne food database.

    Args:
        label: Predicted label from ML model
        database: Optional pre-loaded database (will load if not provided)

    Returns:
        Matched food entry dict, or None if no match found

    Matching strategy:
        1. Exact match on normalized food name
        2. "Contains" match (label contains food name or vice versa)
    """
    if database is None:
        database = load_acne_food_database()

    normalized_label = normalize_food_name(label)

    # Try exact match first
    for entry in database:
        normalized_food = normalize_food_name(entry['food'])
        if normalized_label == normalized_food:
            return entry

    # Try contains match
    for entry in database:
        normalized_food = normalize_food_name(entry['food'])
        # Check if either contains the other
        if normalized_food in normalized_label or normalized_label in normalized_food:
            return entry

    # No match found
    return None


def analyze_food_image(image_bytes: bytes, top_k: int = 3) -> Tuple[Optional[Dict], List[str]]:
    """
    Complete pipeline: predict food from image and match to acne database.

    Args:
        image_bytes: Raw bytes from uploaded file
        top_k: Number of top predictions to try matching (default: 3)

    Returns:
        Tuple of (matched_entry, detected_labels)
        - matched_entry: Dict with food data if found, None otherwise
        - detected_labels: List of all predicted labels (for error reporting)
    """
    # Load database once
    database = load_acne_food_database()

    # Get top K predictions
    predictions = predict_food(image_bytes, top_k=top_k)

    # Extract just the labels for error reporting
    detected_labels = [label for label, _ in predictions]

    # Try to match each prediction in order
    for label, confidence in predictions:
        matched = match_food(label, database)
        if matched:
            # Add the detected label and confidence to the response
            matched_with_meta = matched.copy()
            matched_with_meta['detected_label'] = label
            matched_with_meta['confidence'] = confidence
            return matched_with_meta, detected_labels

    # No match found
    return None, detected_labels
