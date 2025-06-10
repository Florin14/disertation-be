import re
from pathlib import Path

import pandas as pd
from pandas import isna

from extensions import SessionLocal
from modules.listing.models.listing_model import ListingModel
from project_helpers.responses import ConfirmationResponse

from project_helpers.responses import ConfirmationResponse
from .router import router
from modules.listing.models.listing_schemas import ListingAdd

# from ...prediction.utils.get_property_location import geocode_address


def check_listing_can_be_added(row):
    if row is None or row.get("Locație", None) is None or extract_number(row.get("S. utila")) is None or extract_number(
            row.get("Nr. camere"), True) is None or (
            extract_number(row.get("Preț")) is None or extract_number(row.get("Preț")) < 100):
        return False
    return True


def validate_nan(value):
    if value is None or isna(value):
        return None


def split_location(value):
    """
    - If value is None or NaN → return (None, None).
    - If value contains a comma, split at the first comma:
        city    = text before the comma (stripped)
        address = text after the comma (stripped)
    - If no comma, city = None, address = full string (stripped).
    """
    if value is None or (isinstance(value, float) and isna(value)):
        return None, None

    if not isinstance(value, str):
        # If somehow it's not str (e.g. numeric), cast to str and proceed:
        value = str(value)

    raw = value.strip()
    if "," in raw:
        # Split on the first comma only:
        city_part, address_part = raw.split(",", 1)
        city_part = city_part.strip()
        address_part = address_part.strip()
        return city_part or None, address_part or None
    else:
        # No comma → entire thing is address; city stays None
        return raw or None, None


def extract_number(value, as_int=False):
    """
    Primește un `value` posibil string ce conține o valoare numerică
    și un sufix (ex: "55.00 mp", "549€"), plus și valori float/int.
    - Dacă `value` e NaN sau None → returnează None.
    - Dacă e deja float/int → direct returnează (eventual cast la int dacă as_int=True).
    - Dacă e string:
        * Caută (prin regex) primul număr (cu virgulă sau punct).
        * Dacă as_int=True: returnează int(parsed).
        * Altfel: returnează float(parsed).
    Ex: extract_number("55.00 mp") → 55.0
        extract_number("549€", as_int=True) → 549
    """

    # 1) Dacă e pandas NaN / None
    if value is None or isna(value):
        return None

    # 2) Dacă e deja numeric
    if isinstance(value, (int, float)):
        if as_int:
            try:
                return int(value)
            except (ValueError, TypeError):
                return None
        return float(value)

    # 3) Când e string (ex: "55.00 mp", "549€")
    if isinstance(value, str):
        # Eliminăm spații inutile
        s = value.strip()

        # Înlocuim virgula cu punct, ca să putem face float("12.345")
        s = s.replace(",", ".")

        # Folosim regex pentru a găsi prima apariție a unui număr (ex: '55.00', '549')
        match = re.search(r"([0-9]+(?:\.[0-9]+)?)", s)
        if match:
            num_str = match.group(1)
            try:
                num = float(num_str)
                if as_int:
                    return int(num)
                return num
            except ValueError:
                return None
    # Dacă nu se potrivește niciun caz de mai sus
    return None



from sqlalchemy.orm import Session
from .router import router
from fastapi import Depends
from extensions import get_db

# db: Session = Depends(get_db)
@router.post("-import")
async def import_listings(data: ListingAdd, db: Session = Depends(get_db)):
# def import_listings():
    # with SessionLocal() as db:

    routes_dir = Path(__file__).resolve().parent  # .../routes
    listing_dir = routes_dir.parent  # .../modules/listing
    # listing_dir = Path(__file__ ).resolve().parent.parent  # .../modules/listing

    path_to_file = listing_dir / "data" / f"properties1_good.xlsx"

    df = pd.read_excel(path_to_file)

    for idx, row in df.iterrows():
        external_id_val = row.get("ID", None)

        if check_listing_can_be_added(row) is False:
            continue

        raw_loc = row.get("Locație", None)
        city_val, address_val = split_location(raw_loc)
        # lat, lon = geocode_address(raw_loc)
        # print(lat, lon, str(external_id_val).strip())

        # if lat is None or lon is None:
        #     # nu putem geocoda → sărim rândul
        #     continue

        external_id = str(external_id_val).strip()

        # Construim obiectul ListingModel cu validări suplimentare
        listing = ListingModel(
            external_id=external_id,
            classification=validate_nan(row.get("Clasificare")),
            land_classification=validate_nan(row.get("Clasificare teren")),
            useful_area_total=extract_number(row.get("S. utila totala")),
            useful_area=extract_number(row.get("S. utila")),
            num_kitchens=extract_number(row.get("Nr. bucatarii"), as_int=True),
            has_parking_space=extract_number(row.get("Nr. parcari"), as_int=True) is not None and extract_number(
                row.get("Nr. parcari"), as_int=True) > 0,
            floor=extract_number(row.get("Etaj"), as_int=True),
            yard_area=extract_number(row.get("S. curte")),
            location_raw=row.get("Locație", None),
            city=city_val,
            address=address_val,
            latitude=None,
            longitude=None,
            num_rooms=extract_number(row.get("Nr. camere"), as_int=True),
            price=extract_number(row.get("Preț")),
            url=row.get("URL", None),
            has_garage=extract_number(row.get("Nr. garaje"), as_int=True) is not None and extract_number(
                row.get("Nr. garaje"), as_int=True) > 0,
            condominium=validate_nan(row.get("Comp.")),
            has_balconies=extract_number(row.get("Nr. balcoane"), as_int=True) is not None and extract_number(
                row.get("Nr. balcoane"), as_int=True) > 0,
            has_terrace=extract_number(row.get("Terase"), as_int=True) is not None and extract_number(
                row.get("Terase"), as_int=True) > 0,
            comfort=validate_nan(row.get("Confort")),
            structure=validate_nan(row.get("Structura")),
            property_type=validate_nan(row.get("Tip imobil")),
            built_year=extract_number(row.get("An constructie"), as_int=True),
            for_sale=extract_number(row.get("Preț")) is not None and extract_number(row.get("Preț")) > 10000,
        )
        # normalizare(valori intre 0 si 1)/standardizare,
        # agregare petnru predictie petnru a lua primele 5 (distante normalizate), daca are sau nu garaj sa nu ajunga sa fie mai important(data embalance)
        # pot sa ma focusez doar pe un model care sa fie antrenat bine - precizie undeva la > 80% este perfect
        # sa nu mentionez de unde am luat datele -> pot sa mentionez ca de pe net !!!obligatoriu nu de pe site ul blitz
        # sa incerc sa restrang la valori intre 0 si 1
        # agregare petnru predictie petnru a lua primele 5 (distante normalizate), daca are sau nu garaj sa nu ajunga sa fie mai important(data embalance)
        # se mai pot adauga informatii legate de distanta pana la centru, prima statie de autobus/troleu, pana la metrou, pana la parc, pana la scoli, pana la spital, etc.

        db.add(listing)

    db.commit()

    db.close()

    return ConfirmationResponse()

