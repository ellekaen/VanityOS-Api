# VanityOS Skincare API

A FastAPI-based skincare ingredient analysis API that helps determine whether food ingredients are comedogenic (pore-clogging) for skin.

## Features

- **Food Ingredient Analysis**: Analyze if a food ingredient is comedogenic for skin
- **Image Detection**: Upload images to detect if they contain food items
- **Comedogenic Database**: Comprehensive database of carrier oils and their comedogenic properties
- **API Key Authentication**: Secure access with API key authentication

## Installation

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/VanityOS-Api.git
cd VanityOS-Api
```

2. Create a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set your API key (for local testing):
```bash
export API_KEY="vanityos_secret_key_123"
```

Or update the `API_KEY` in `main.py` directly.

5. Run the server:
```bash
uvicorn main:app --reload
```

The API will be available at `http://127.0.0.1:8000`

## API Endpoints

### Root
- **GET** `/` - API information

### Health Check
- **GET** `/health` - Health status

### Analyze Food
- **GET** `/analyze_food?food=<food_name>` - Analyze if a food ingredient is comedogenic
- **Headers**: `x-api-key: <your_api_key>`
- **Response**: Food analysis with comedogenic grade and notes

**Example:**
```bash
curl -G "http://127.0.0.1:8000/analyze_food" \
  --data-urlencode "food=Pumpkin Seeds" \
  -H "x-api-key: vanityos_scanner_M1c43ll3kuzemczak0417"
```

### Analyze Image
- **POST** `/analyze_image` - Upload an image to detect if it contains food
- **Headers**: `x-api-key: <your_api_key>`
- **Body**: Image file (multipart/form-data)
- **Response**: Detected food label or rejection message

### Interactive Documentation
- **GET** `/docs` - Swagger UI documentation

## Comedogenic Scale

The API uses a 0-5 comedogenic scale:

- **0**: Non-comedogenic - Will not clog pores
- **1-2**: Low comedogenic - Rarely clogs pores
- **3**: Moderately comedogenic - May clog pores
- **4**: High comedogenic - Will clog pores
- **5**: Very high - Almost certain to clog pores

## Supported Ingredients

The API includes data for common carrier oils and food ingredients that can be applied to skin:

- Pumpkin Seed Oil (Grade 0)
- Avocado Oil (Grade 2-3)
- Coconut Oil (Grade 4)
- Olive Oil (Grade 2)
- Argan Oil (Grade 0)
- Jojoba Oil (Grade 0)
- Almond Oil (Grade 1-2)
- Grapeseed Oil (Grade 1)
- Sunflower Oil (Grade 0-1)
- Shea Butter (Grade 0)
- Cocoa Butter (Grade 4)
- Sesame Oil (Grade 1-2)
- Rosehip Seed Oil (Grade 0)
- Castor Oil (Grade 0)

See `carriers.md` for detailed information about each ingredient.

## Dependencies

- FastAPI - Modern web framework
- Uvicorn - ASGI server
- PyTorch - Machine learning framework
- Transformers - Hugging Face model library
- Pillow - Image processing
- NumPy - Numerical computing

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

