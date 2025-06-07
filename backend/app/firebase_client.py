import firebase_admin
from firebase_admin import credentials, db
from config import FIREBASE_DB

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': FIREBASE_DB
})

def get_shock_data(shipment_id):
    try:
        ref = db.reference(f"/device_data/SQT-2808/latest_log/events/shock")
        shock_values = ref.get() or []
        return shock_values
    except Exception as e:
        print("Firebase error:", e)
        return []
