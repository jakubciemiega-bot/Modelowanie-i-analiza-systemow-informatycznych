from flask import jsonify, request
import database
from auth import token_required  

def get_vehicles():
    return jsonify(database.load_vehicles())

@token_required(allowed_roles=['Administrator', 'Logistyk']) 
def manage_vehicle(current_user):
    data = request.json
    action = data.get('action')
    vehicle_id = data.get('id')
    vehicles = database.load_vehicles()

    if action == 'add':
        if any(v['id'] == vehicle_id for v in vehicles):
            return jsonify({"success": False, "message": "Pojazd o tym ID już istnieje"}), 400
        
        vehicles.append({
            "id": vehicle_id,
            "typ": data.get('typ'),
            "max_ladownosc": int(data.get('max_ladownosc')),
            "stan": "sprawny",
            "towary": data.get('towary', [])
        })
    
    elif action == 'delete':
        vehicles = [v for v in vehicles if v['id'] != vehicle_id]
        
    elif action == 'change_status':
        for v in vehicles:
            if v['id'] == vehicle_id:
                v['stan'] = data.get('new_status')

    database.save_vehicles(vehicles)
    return jsonify({"success": True, "vehicles": vehicles})