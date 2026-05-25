from flask import jsonify, request
import database
from auth import token_required

@token_required(allowed_roles=['Administrator', 'Logistyk'])
def create_transport(current_user):
    data = request.json
    warehouse = database.load_warehouse()
    users = database.load_users()
    vehicles = database.load_vehicles()
    
    towar_nazwa = data.get('towar_nazwa')
    ilosc_potrzebna = int(data.get('ilosc'))
    wybrany_kierowca_id = data.get('kierowca_id')
    wybrany_pojazd_id = data.get('pojazd_id')  # Pobieranie ID pojazdu z frontendu

    # Weryfikacja towaru
    towar_w_magazynie = next((item for item in warehouse if item['nazwa'] == towar_nazwa), None)
    if not towar_w_magazynie or towar_w_magazynie['ilosc'] < ilosc_potrzebna:
        return jsonify({"success": False, "message": "Brak towaru w magazynie"}), 400

    # Weryfikacja wybranego pojazdu
    pojazd = next((v for v in vehicles if v['id'] == wybrany_pojazd_id), None)
    
    if not pojazd:
        return jsonify({"success": False, "message": "Wybrany pojazd nie istnieje"}), 404
    
    if pojazd['stan'] != 'sprawny':
        return jsonify({"success": False, "message": f"Pojazd {wybrany_pojazd_id} nie jest dostępny (Status: {pojazd['stan']})"}), 400
    
    if towar_w_magazynie['rodzaj'] not in pojazd['towary']:
        return jsonify({"success": False, "message": f"Pojazd {wybrany_pojazd_id} nie może przewozić towaru typu: {towar_w_magazynie['rodzaj']}"}), 400

    if int(pojazd['max_ladownosc']) < ilosc_potrzebna:
        return jsonify({"success": False, "message": "Ładunek przekracza maksymalną ładowność pojazdu"}), 400

    # Weryfikacja kierowcy 
    if wybrany_kierowca_id not in users:
        return jsonify({"success": False, "message": "Wybrany kierowca nie istnieje"}), 404
    
    kierowca_data = users[wybrany_kierowca_id]
    wymagane_upr = "ADR" if towar_w_magazynie['rodzaj'] == "ciekły" else "C"

    if kierowca_data['status'] != 'wolny':
        return jsonify({"success": False, "message": f"Kierowca {wybrany_kierowca_id} jest zajęty"}), 400
    
    if wymagane_upr not in kierowca_data.get('uprawnienia', []):
        return jsonify({"success": False, "message": f"Kierowca nie ma uprawnień {wymagane_upr}"}), 400

    # Aktualizacja stanów
    towar_w_magazynie['ilosc'] -= ilosc_potrzebna
    pojazd['stan'] = 'w trasie'  # Zmiana stan konkretnego wybranego pojazdu
    users[wybrany_kierowca_id]['status'] = 'w trasie'
    users[wybrany_kierowca_id]['current_vehicle'] = pojazd['id']
    
    database.save_warehouse(warehouse)
    database.save_vehicles(vehicles)
    database.save_users(users)
    
    return jsonify({"success": True, "message": f"Transport rozpoczęty: {wybrany_kierowca_id} pojazdem {wybrany_pojazd_id}"})