from google.oauth2 import id_token
from google.auth.transport import requests
import os

GOOGLE_CLIENT_ID = "83021076383-148aa0gv78b8o1h4egqi0kq0s81tclm0.apps.googleusercontent.com"


def verify_google_token(token: str) -> dict | None:
    """
    Verifică ID token-ul emis de Google și returnează payload-ul
    cu informațiile user-ului (email, name, sub etc.),
    sau None dacă token-ul nu e valid.
    """
    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            audience=GOOGLE_CLIENT_ID
        )
        # Validăm issuer-ul
        if idinfo.get("iss") not in ("accounts.google.com", "https://accounts.google.com"):
            return None
        return idinfo
    except ValueError:
        return None