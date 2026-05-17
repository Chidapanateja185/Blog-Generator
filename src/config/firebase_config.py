import os
import json
import firebase_admin

from dotenv import load_dotenv
from firebase_admin import credentials

load_dotenv()

if not firebase_admin._apps:

    firebase_json = os.getenv("FIREBASE_JSON")

    if firebase_json:

        cred_dict = json.loads(firebase_json)

        cred = credentials.Certificate(cred_dict)

    else:

        cred = credentials.Certificate(
            "src/config/firebase-adminsdk.json"
        )

    firebase_admin.initialize_app(cred)

print("✅ Firebase initialized")