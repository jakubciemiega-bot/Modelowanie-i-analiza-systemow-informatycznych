from flask import jsonify, request
import database
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
import datetime
from functools import wraps
import re

SECRET_KEY = "SUPER_TAJNY_KLUCZ_SERWERA" 

def generate_jwt(username, role):
    payload = {
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=8), # ważność tokenu
        'iat': datetime.datetime.utcnow(),
        'sub': username,
        'role': role
    }
    return jwt.encode(payload, SECRET_KEY, algorithm='HS256')

def token_required(allowed_roles=None):
    def decorator(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            token = None
            if 'Authorization' in request.headers:
                auth_header = request.headers['Authorization']
                if auth_header.startswith("Bearer "):
                    token = auth_header.split(" ")[1]

            if not token:
                return jsonify({"success": False, "message": "Brak tokenu autoryzacyjnego"}), 401

            try:
                data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
                current_user = {
                    "username": data['sub'],
                    "role": data['role']
                }
            except jwt.ExpiredSignatureError:
                return jsonify({"success": False, "message": "Token wygasł"}), 401
            except jwt.InvalidTokenError:
                return jsonify({"success": False, "message": "Niepoprawny token"}), 401

            # Weryfikacja ról (RBAC)
            if allowed_roles and current_user['role'] not in allowed_roles:
                return jsonify({"success": False, "message": "Brak wymaganych uprawnień"}), 403

            # Przekazanie dane użytkownika do funkcji docelowej
            return f(current_user, *args, **kwargs)
        return decorated
    return decorator

def login():
    data = request.json
    users = database.load_users()
    username = data.get('username')
    password = data.get('password')
    
    user = users.get(username)
    
    if user:
        is_valid = False
        if user['password'] == password:
            is_valid = True
            user['password'] = generate_password_hash(password)
            database.save_users(users)
        elif check_password_hash(user['password'], password):
            is_valid = True

        if is_valid:
            token = generate_jwt(username, user['role']) # Generowanie tokenu JWT
            return jsonify({
                "success": True, 
                "token": token, 
                "username": username,
                "role": user['role'], 
                "uprawnienia": user.get('uprawnienia', []),
                "status": user.get('status', 'wolny')
            }), 200
            
    return jsonify({"success": False, "message": "Błędne dane logowania"}), 401

@token_required(allowed_roles=['Administrator', 'Logistyk'])
def get_all_users(current_user):
    return jsonify(database.load_users())

@token_required(allowed_roles=['Administrator'])
def manage_user(current_user):
    data = request.json
    action = data.get('action')
    username = data.get('username', '').strip()
    password = data.get('password')
    role = data.get('role')
    uprawnienia = data.get('uprawnienia', [])

    users = database.load_users()

    if action == 'add':
        if not username or not password or not role:
            return jsonify({"success": False, "message": "Wszystkie pola są wymagane"}), 400
        
        if username in users:
            return jsonify({"success": False, "message": "Użytkownik o tej nazwie już istnieje"}), 400

        password_regex = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&#])[A-Za-z\d@$!%*?&#]{8,}$"
        
        if not re.match(password_regex, password):
            return jsonify({
                "success": False, 
                "message": "Hasło nie spełnia wymagań: min. 8 znaków, mała i wielka litera, cyfra oraz znak specjalny (@$!%*?&#)."
            }), 400

        # Jeśli hasło jest poprawne, utwórz użytkownika
        users[username] = {
            "password": password,
            "role": role,
            "uprawnienia": uprawnienia,
            "status": "wolny",
            "current_vehicle": None
        }
    
    elif action == 'delete':
        if username == 'admin': 
            return jsonify({"success": False, "message": "Nie usuwaj konta głównego"}), 400
        users.pop(username, None)

    database.save_users(users)
    return jsonify({"success": True, "users": users})

@token_required(allowed_roles=['Kierowca'])
def complete_trip(current_user):
    # Tożsamość pobierana z tokenu JWT, a nie z żądania użytkownika
    username = current_user['username'] 
    
    users = database.load_users()
    vehicles = database.load_vehicles()

    if username not in users:
        return jsonify({"success": False, "message": "Użytkownik nie istnieje"}), 404

    user_info = users[username]
    
    if user_info.get('status') != 'w trasie':
        return jsonify({"success": False, "message": "Nie jesteś obecnie w trasie"}), 400

    # Zwolnienie pojazdu
    vehicle_id = user_info.get('current_vehicle')
    if vehicle_id:
        for v in vehicles:
            if v['id'] == vehicle_id:
                v['stan'] = 'sprawny'
                break
    
    # Aktualizacja statusu kierowcy
    user_info['status'] = 'wolny'
    user_info['current_vehicle'] = None

    database.save_users(users)
    database.save_vehicles(vehicles)

    return jsonify({
        "success": True, 
        "message": "Trasa zakończona. Pojazd i kierowca są wolni.",
        "new_status": "wolny"
    })

@token_required(allowed_roles=['Administrator', 'Logistyk', 'Kierowca'])
def get_current_user_profile(current_user):
    """Zwraca profil użytkownika po tokenie (potrzebne przy odświeżaniu strony)."""
    users = database.load_users()
    username = current_user['username']
    
    if username not in users:
        return jsonify({"success": False, "message": "Użytkownik nie istnieje"}), 404
        
    user_info = users[username]
    return jsonify({
        "success": True,
        "user": {
            "username": username,
            "role": user_info['role'],
            "status": user_info.get('status', 'wolny'),
            "uprawnienia": user_info.get('uprawnienia', []),
            "current_vehicle": user_info.get('current_vehicle') or 'Brak'
        }
    })