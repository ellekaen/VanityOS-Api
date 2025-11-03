"""
Food to comedogenic ingredient mapper
Maps common food items to their skincare carrier equivalents and comedogenic properties
"""
import re
from pathlib import Path


# Food to carrier mapping dictionary
FOOD_TO_CARRIER = {
    "pumpkin seed": "Pumpkin Seed Oil",
    "pumpkin seeds": "Pumpkin Seed Oil",
    "avocado": "Avocado Oil",
    "avocado oil": "Avocado Oil",
    "coconut": "Coconut Oil",
    "coconut oil": "Coconut Oil",
    "olive": "Olive Oil",
    "olive oil": "Olive Oil",
    "argan": "Argan Oil",
    "argan oil": "Argan Oil",
    "jojoba": "Jojoba Oil",
    "jojoba oil": "Jojoba Oil",
    "almond": "Almond Oil",
    "almond oil": "Almond Oil",
    "grapeseed": "Grapeseed Oil",
    "grapeseed oil": "Grapeseed Oil",
    "sunflower": "Sunflower Oil",
    "sunflower oil": "Sunflower Oil",
    "shea butter": "Shea Butter",
    "cocoa butter": "Cocoa Butter",
    "cocoa": "Cocoa Butter",
    "sesame": "Sesame Oil",
    "sesame oil": "Sesame Oil",
    "rosehip": "Rosehip Seed Oil",
    "rosehip seed": "Rosehip Seed Oil",
    "rosehip oil": "Rosehip Seed Oil",
    "castor": "Castor Oil",
    "castor oil": "Castor Oil",
}


# Comedogenic data - grade 0-5, with notes
COMEDOGENIC_DB = {
    "Pumpkin Seed Oil": {
        "is_comedogenic": False,
        "grade": "0",
        "notes": "Non-comedogenic, excellent for acne-prone skin"
    },
    "Avocado Oil": {
        "is_comedogenic": True,
        "grade": "2-3",
        "notes": "Moderately comedogenic, use with caution on oily/acne-prone skin"
    },
    "Coconut Oil": {
        "is_comedogenic": True,
        "grade": "4",
        "notes": "Highly comedogenic, avoid on acne-prone skin"
    },
    "Olive Oil": {
        "is_comedogenic": True,
        "grade": "2",
        "notes": "Moderately comedogenic, may clog pores"
    },
    "Argan Oil": {
        "is_comedogenic": False,
        "grade": "0",
        "notes": "Non-comedogenic, suitable for all skin types"
    },
    "Jojoba Oil": {
        "is_comedogenic": False,
        "grade": "0",
        "notes": "Non-comedogenic, mimics skin's natural sebum"
    },
    "Almond Oil": {
        "is_comedogenic": False,
        "grade": "1-2",
        "notes": "Low to moderately comedogenic"
    },
    "Grapeseed Oil": {
        "is_comedogenic": False,
        "grade": "1",
        "notes": "Low comedogenic potential, suitable for most skin types"
    },
    "Sunflower Oil": {
        "is_comedogenic": False,
        "grade": "0-1",
        "notes": "Non to low comedogenic, good for sensitive skin"
    },
    "Shea Butter": {
        "is_comedogenic": False,
        "grade": "0",
        "notes": "Non-comedogenic, excellent moisturizer"
    },
    "Cocoa Butter": {
        "is_comedogenic": True,
        "grade": "4",
        "notes": "Highly comedogenic, heavy and pore-clogging"
    },
    "Sesame Oil": {
        "is_comedogenic": False,
        "grade": "1-2",
        "notes": "Low to moderately comedogenic"
    },
    "Rosehip Seed Oil": {
        "is_comedogenic": False,
        "grade": "0",
        "notes": "Non-comedogenic, excellent for acne-prone and aging skin"
    },
    "Castor Oil": {
        "is_comedogenic": False,
        "grade": "0",
        "notes": "Non-comedogenic, viscous oil"
    },
}


def get_ingredient_info(food_name: str) -> dict:
    """
    Map a food name to its carrier oil equivalent and return comedogenic information.
    
    Args:
        food_name: The name of the food ingredient
        
    Returns:
        Dictionary with comedogenic information, or None if not found
    """
    # Normalize the input
    food_lower = food_name.lower().strip()
    
    # Look up the carrier equivalent
    carrier = FOOD_TO_CARRIER.get(food_lower)
    
    # If not found, try partial matching
    if not carrier:
        for food_key, carrier_value in FOOD_TO_CARRIER.items():
            if food_key in food_lower or food_lower in food_key:
                carrier = carrier_value
                break
    
    # If still not found, return None
    if not carrier:
        return None
    
    # Return the comedogenic information
    return COMEDOGENIC_DB.get(carrier)

