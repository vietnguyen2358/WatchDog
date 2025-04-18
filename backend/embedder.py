# embedder.py

import google.generativeai as genai
from chromadb.utils import embedding_functions
import json
import os
from dotenv import load_dotenv
from PIL import Image
import io

# Load environment variables
load_dotenv()

# Gemini API setup
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)

# Models
gemini_vision = genai.GenerativeModel("gemini-2.0-flash-lite")
embed_model = embedding_functions.GoogleGenerativeAiEmbeddingFunction(api_key=GEMINI_API_KEY)

# Prompt to generate structured appearance info
STRUCTURED_JSON_PROMPT = """
Describe this person in structured JSON format with the following keys:
- gender (male, female, other)
- age_group (child, teen, adult, senior)
- ethnicity (if visible/apparent)
- skin_tone (light, medium, dark, etc.)
- hair_style (short, long, curly, straight, bald, etc.)
- hair_color (black, brown, blonde, red, gray, etc.)
- facial_features (beard, mustache, glasses, etc.)
- clothing_top (shirt, hoodie, t-shirt, jacket, etc.)
- clothing_top_color (primary color of top)
- clothing_top_pattern (solid, striped, plaid, floral, etc.)
- clothing_bottom (jeans, pants, skirt, shorts, etc.)
- clothing_bottom_color (primary color of bottom)
- clothing_bottom_pattern (solid, striped, plaid, etc.)
- footwear (sneakers, boots, sandals, etc.)
- footwear_color (primary color of shoes)
- accessories (bag, hat, jewelry, etc.)
- bag_type (backpack, handbag, shoulder bag, etc.)
- bag_color (primary color of bag)
- pose (standing, sitting, walking, etc.)
- location_context (indoor, outdoor, etc.)
- child_context (with_parent, with_guardian, alone, playing, etc.)
- height_estimate (short, average, tall - relative to typical adult height)
- build_type (slim, average, athletic, etc.)

For children, pay special attention to:
1. Age-appropriate clothing and accessories
2. Presence of parents or guardians
3. Activities they are engaged in
4. Their relative size compared to adults
5. Child-specific items (toys, school bags, etc.)

For facial hair, be specific about:
1. Type (beard, mustache, goatee, stubble)
2. Length and style
3. Color (if different from head hair)
4. Grooming state (well-groomed, unkempt, etc.)

Respond with ONLY a valid JSON object, nothing else. Include only the attributes you can confidently identify.
"""


def describe_person(pil_image):
    """Generate a structured JSON description of a person."""
    res = gemini_vision.generate_content([STRUCTURED_JSON_PROMPT, pil_image])
    raw = res.text.strip().replace("```json", "").replace("```", "")
    try:
        return json.loads(raw)
    except:
        print("⚠️ Gemini failed to parse JSON:")
        print(raw)
        return None


def embed_description(json_obj):
    """Convert JSON object to embedding using Google embedding model."""
    text = json.dumps(json_obj)
    return embed_model([text])[0]  # returns vector


def embed_image(image):
    """Convert image to embedding using Google embedding model."""
    if isinstance(image, str):
        # If image is a path, load it
        image = Image.open(image)
    elif isinstance(image, bytes):
        # If image is bytes, convert to PIL Image
        image = Image.open(io.BytesIO(image))
    
    # Convert image to base64 for embedding
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    img_str = buffered.getvalue()
    
    # Get embedding
    return embed_model([img_str])[0]


def embed_text(text):
    """Convert text to embedding using Google embedding model."""
    return embed_model([text])[0]
