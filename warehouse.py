from flask import jsonify, request
import database
import time
from auth import token_required

def get_status():
    return jsonify(database.load_warehouse())

@token_required(allowed_roles=['Administrator', 'Logistyk'])
def add_item(current_user): 
    try:
        warehouse_data = database.load_warehouse()
        data = request.json
        
        nazwa = data.get('nazwa', '').strip()
        ilosc = data.get('ilosc')
        rodzaj = data.get('rodzaj')
        
        # Walidacja danych wejściowych
        if not nazwa or not str(ilosc).isdigit() or rodzaj not in ['sypki', 'ciekły', 'pakowany']:
            return jsonify({"success": False, "message": "Niepoprawne dane"}), 400

        ilosc_int = int(ilosc)
        if ilosc_int <= 0:
            return jsonify({"success": False, "message": "Ilość musi być większa od 0"}), 400

        existing_item = None
        for item in warehouse_data:
            if item['nazwa'].lower() == nazwa.lower() and item['rodzaj'] == rodzaj:
                existing_item = item
                break

        if existing_item:
            existing_item['ilosc'] += ilosc_int
            message = f"Zwiększono ilość towaru '{existing_item['nazwa']}' o {ilosc_int}."
        else:
            new_item = {
                "id": int(time.time()),
                "nazwa": nazwa,  # Zachowaj oryginalną wielkość liter wpisaną przez użytkownika
                "ilosc": ilosc_int,
                "rodzaj": rodzaj
            }
            warehouse_data.append(new_item)
            message = "Dodano nowy towar do magazynu."
        
        # Zapis do bazy danych (pliku JSON)
        database.save_warehouse(warehouse_data)
        return jsonify({"success": True, "message": message, "inventory": warehouse_data})
        
    except Exception as e:
        return jsonify({"success": False, "message": f"Błąd serwera: {str(e)}"}), 500
    
@token_required(allowed_roles=['Administrator', 'Logistyk'])
def delete_item(current_user):
    try:
        warehouse_data = database.load_warehouse()
        data = request.json
        item_id = data.get('id')

        if not item_id:
            return jsonify({"success": False, "message": "Brak ID towaru"}), 400

        # Odfiltrowanie (usunięcie) elementu o podanym ID
        updated_warehouse = [item for item in warehouse_data if item['id'] != int(item_id)]
        
        if len(updated_warehouse) == len(warehouse_data):
            return jsonify({"success": False, "message": "Nie znaleziono towaru o podanym ID"}), 404

        database.save_warehouse(updated_warehouse)
        return jsonify({"success": True, "message": "Towar został usunięty z magazynu."})
    except Exception as e:
        return jsonify({"success": False, "message": f"Błąd serwera: {str(e)}"}), 500