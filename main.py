from fastapi import FastAPI
from . import funct
import json
#from . import database
from fastapi.middleware.cors import CORSMiddleware




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
    data = funct.get_food_data(code_bar)
    if data.status_code != 200:
        return {"message": "Failed to fetch the data"}

    new_data = json.loads(data.text)
    food_data = funct.extract_useful_info(new_data)
    
    # Use background tasks to insert data into the database
    #background_tasks.add_task(database.write_to_db, food_data)
    
    return food_data
