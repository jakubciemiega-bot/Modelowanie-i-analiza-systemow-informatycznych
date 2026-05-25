from flask import Flask
from flask_cors import CORS
import auth
import warehouse
import vehicles
import transports

app = Flask(__name__)
CORS(app)


@app.route('/api/login', methods=['POST'])
def login():
    """Logowanie i pobieranie roli użytkownika"""
    return auth.login()

@app.route('/api/admin/users', methods=['GET'])
def list_users():
    """Pobieranie listy wszystkich użytkowników (tylko dla Admina)"""
    return auth.get_all_users()

@app.route('/api/admin/users/manage', methods=['POST'])
def manage_users():
    """Tworzenie/usuwanie kierowców i edycja uprawnień"""
    return auth.manage_user()

@app.route('/api/warehouse', methods=['GET'])
def get_inventory():
    """Pobieranie stanu magazynowego (dostępne dla wszystkich)"""
    return warehouse.get_status()

@app.route('/api/warehouse/add', methods=['POST'])
def add_to_inventory():
    """Dodawanie towaru (tylko dla Logistyka i Admina)"""
    return warehouse.add_item()

@app.route('/api/warehouse/delete', methods=['POST'])
def delete_from_inventory():
    """Usuwanie towaru z magazynu (tylko dla Logistyka i Admina)"""
    return warehouse.delete_item()

@app.route('/api/vehicles', methods=['GET'])
def list_vehicles():
    """Pobieranie listy pojazdów floty"""
    return vehicles.get_vehicles()

@app.route('/api/vehicles/manage', methods=['POST'])
def manage_fleet():
    """Dodawanie nowych pojazdów i zmiana ich statusu"""
    return vehicles.manage_vehicle()

@app.route('/api/transports/create', methods=['POST'])
def create_new_transport():
    """Tworzenie nowego transportu (tylko dla Logistyka i Admina)"""
    return transports.create_transport()

@app.route('/api/user/complete_trip', methods=['POST'])
def finish_trip():
    """Zakańczanie trasy (tylko dla Kierowców)"""
    return auth.complete_trip()

@app.route('/api/user/me', methods=['GET'])
def get_me():
    """Weryfikacja tokenu i przywracanie sesji po odświeżeniu"""
    return auth.get_current_user_profile()

if __name__ == '__main__':
    app.run(debug=True, port=5000, use_reloader=False)