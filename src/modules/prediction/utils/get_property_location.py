from geopy.geocoders import Nominatim
from geopy.extra.rate_limiter import RateLimiter
import time
import pandas as pd

geolocator = Nominatim(user_agent="MyPropertyApp")
# Pentru a nu depăși rata de cereri:
geocode = RateLimiter(geolocator.geocode, min_delay_seconds=1)

def geocode_address(raw_loc):
    # Formăm șirul complet, de ex. “<address>, <city>, România”
    addr = f"{raw_loc}, România"
    try:
        location = geocode(addr)
        if location:
            return pd.Series([location.latitude, location.longitude])
    except Exception as e:
        return pd.Series([None, None])
    # Dacă nu găsește nimic:
    return pd.Series([None, None])

print(geocode_address("Alba Iulia Vest"))

