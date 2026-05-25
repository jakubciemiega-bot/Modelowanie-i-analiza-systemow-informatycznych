import json
import os

DB_FILE = 'warehouse_db.json'
USERS_FILE = 'users_db.json'
VEHICLES_FILE = 'vehicles_db.json'

def load_warehouse():
    if not os.path.exists(DB_FILE):
        initial_data = [
            {"id": 1, "nazwa": "Paliwo", "ilosc": 5000, "rodzaj": "ciekły"},
            {"id": 2, "nazwa": "Żwir", "ilosc": 200, "rodzaj": "sypki"}
        ]
        save_warehouse(initial_data)
        return initial_data
    with open(DB_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_warehouse(data):
    with open(DB_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
        
def load_users():
    if not os.path.exists(USERS_FILE):
        initial_users = {
            "admin": {"password": "123", "role": "Administrator", "uprawnienia": ["wszystko"]}
        }
        save_users(initial_users)
        return initial_users
    with open(USERS_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_users(data):
    with open(USERS_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
        
def load_vehicles():
    if not os.path.exists(VEHICLES_FILE):
        initial_vehicles = [
            {"id": "KR12345", "typ": "cysterna", "max_ladownosc": 20000, "stan": "sprawny", "towary": ["ciekły"]},
            {"id": "KR67890", "typ": "ciężarówka", "max_ladownosc": 15000, "stan": "sprawny", "towary": ["pakowany", "sypki"]}
        ]
        save_vehicles(initial_vehicles)
        return initial_vehicles
    with open(VEHICLES_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def save_vehicles(data):
    with open(VEHICLES_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)