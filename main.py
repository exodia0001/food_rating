from fastapi import FastAPI
import requests

import json
#from . import database
from fastapi.middleware.cors import CORSMiddleware



url="https://world.openfoodfacts.org/api/v3/product/6111259343108.json"

def get_food_data(code_bar:str):
    url="https://world.openfoodfacts.org/api/v3/product/"+f"{code_bar}.json"
    r=requests.get(url)
    return r

def extract_useful_info(product_data):
    product = product_data.get("product", {})
    
    # Extract basic product info
    code = product.get("code", "N/A")
    categories = product.get("categories", "N/A")
    ingredients = product.get("ingredients", [])
    ecoscore_grade = product.get("ecoscore_grade", "N/A")
    ecoscore_score = product.get("ecoscore_score", "N/A")
    country = ", ".join(product.get("countries_tags", [])) or "N/A"
    allergens = product.get("allergens", "N/A")
    images = {
        "front": product.get("image_front_url", "N/A"),
        "ingredients": product.get("image_ingredients_url", "N/A"),
        "nutrition": product.get("image_nutrition_url", "N/A")
    }
    
    # Extract nutritional information
    nutriments = product.get("nutriments", {})
    
    nutritional_info = {
        'energy': {
            'value': nutriments.get('energy', 0),
            'unit': 'kcal' if 'energy-kcal' in nutriments else '',
            'energy_kcal_value': nutriments.get('energy-kcal', 0),
            'energy_kcal_unit': 'kcal'
        },
        'fat': {
            'value': nutriments.get('fat', 0),
            'unit': 'g'
        },
        'saturated_fat': {
            'value': nutriments.get('saturated-fat', 0),
            'unit': 'g'
        },
        'carbohydrates': {
            'value': nutriments.get('carbohydrates', 0),
            'unit': 'g'
        },
        'sugars': {
            'value': nutriments.get('sugars', 0),
            'unit': 'g'
        },
        'fiber': {
            'value': nutriments.get('fiber', 0),
            'unit': 'g'
        },
        'proteins': {
            'value': nutriments.get('proteins', 0),
            'unit': 'g'
        },
        'salt': {
            'value': nutriments.get('salt', 0),
            'unit': 'g'
        },
        'sodium': {
            'value': nutriments.get('sodium', 0),
            'unit': 'g'
        }
    }
    
    # Organize the extracted information into a dictionary
    extracted_info = {
        "code": code,
        "categories": categories,
        "ecoscore_grade": ecoscore_grade,
        "ecoscore_score": ecoscore_score,
        "countries": country,
        "allergens": allergens,
        "images": images,
        "ingredients": [
            {
                "text": ingredient.get("text", "Unknown"),
                "percent_estimate": ingredient.get("percent_estimate", "N/A")
            }
            for ingredient in ingredients
        ],
        "nutritional_info": nutritional_info  # Include nutritional info here
    }
    
    # Include warnings or additional information if available
    if product.get("missing_data_warning", 0):
        extracted_info["warning"] = "Some key data is missing or incomplete for this product."
    
    data_quality_tags = product.get("data_quality_tags", [])
    if data_quality_tags:
        extracted_info["data_quality_tags"] = data_quality_tags
    
    grades = product.get("grades", {})
    if grades:
        extracted_info["grades"] = grades
    
    scores = product.get("scores", {})
    if scores:
        extracted_info["scores"] = scores
    
    return extracted_info



app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/food/{code_bar}")
def get_food(code_bar: str):
    data = get_food_data(code_bar)
    if data.status_code != 200:
        return {"message": "Failed to fetch the data"}

    new_data = json.loads(data.text)
    food_data = extract_useful_info(new_data)
    
    # Use background tasks to insert data into the database
    #background_tasks.add_task(database.write_to_db, food_data)
    
    return food_data
