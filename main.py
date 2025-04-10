from fastapi import FastAPI, Query
from supabase import create_client, Client
from dotenv import load_dotenv
from fuzzywuzzy import fuzz
import os

# Cargar variables del entorno
load_dotenv()
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Conectar a Supabase
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

app = FastAPI()

def get_all_names_from_table(table_name: str):
    """Obtiene todos los nombres desde una tabla específica de Supabase"""
    response = supabase.table(table_name).select("id, name").execute()
    return response.data

def find_similar_names(input_name: str, table: str, threshold: int = 80):
    """Busca nombres similares en la tabla usando fuzzy matching"""
    records = get_all_names_from_table(table)
    results = []

    for record in records:
        similarity = fuzz.ratio(input_name.lower(), record["name"].lower())
        if similarity >= threshold:
            results.append({
                "name": record["name"],
                "similarity": similarity
            })

    results.sort(key=lambda x: x["similarity"], reverse=True)
    return results[:5]

@app.get("/towns")
def match_town(town: str = Query(..., description="Nombre del pueblo a verificar")):
    suggestions = find_similar_names(town, "towns")
    return {"input": town, "suggestions": suggestions}

@app.get("/cities")
def match_city(city: str = Query(..., description="Nombre de la ciudad a verificar")):
    suggestions = find_similar_names(city, "cities")
    return {"input": city, "suggestions": suggestions}

@app.get("/lastnames")
def match_lastname(lastname: str = Query(..., description="Apellido a verificar")):
    suggestions = find_similar_names(lastname, "lastnames")
    return {"input": lastname, "suggestions": suggestions}
