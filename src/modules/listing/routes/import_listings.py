import re
from pathlib import Path

import pandas as pd
from fastapi import Depends
from sqlalchemy.orm import Session

from extensions import get_db
from project_helpers.responses import ConfirmationResponse
from .router import router
from ..models import ListingModel, ListingAdd


def to_none_if_nan(value):
    """
    Dacă `value` este Pandas NA/NaN sau None, întoarce None,
    altfel returnează valoarea originală.
    """
    if value is None:
        return None
    # pandas.isna acoperă NaN, pd.NA etc.
    if pd.isna(value):
        return None
    return value


def split_location(value):
    """
    - If value is None or NaN → return (None, None).
    - If value contains a comma, split at the first comma:
        city    = text before the comma (stripped)
        address = text after the comma (stripped)
    - If no comma, city = None, address = full string (stripped).
    """
    from pandas import isna
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
    from pandas import isna

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


@router.post("-import")
async def import_listings(data: ListingAdd, db: Session = Depends(get_db)):
    routes_dir = Path(__file__).resolve().parent  # .../routes
    listing_dir = routes_dir.parent  # .../modules/listing
    path_to_file = listing_dir / "data" / "properties9.xlsx"

    df = pd.read_excel(path_to_file)

    for idx, row in df.iterrows():
        # Folosim to_none_if_nan() pentru a pune None acolo unde row[...] este nan
        external_id_val = to_none_if_nan(row.get("ID"))
        if external_id_val is None:
            # Dacă nu există ID, sărim rândul (sau poți alege să generezi un UUID temporar)
            continue

        raw_loc = to_none_if_nan(row.get("Locație"))
        city_val, address_val = split_location(raw_loc)

        # Construim obiectul ListingModel cu toate câmpurile, folosind extract_number()
        listing = ListingModel(
            external_id=str(external_id_val).strip(),

            classification=to_none_if_nan(row.get("Clasificare")),
            land_classification=to_none_if_nan(row.get("Clasificare teren")),

            useful_area_total=extract_number(row.get("S. utila totala")),
            useful_area=extract_number(row.get("S. utila")),

            num_kitchens=extract_number(row.get("Nr. bucatarii"), as_int=True),
            num_parking=extract_number(row.get("Nr. parcari"), as_int=True),

            floor=extract_number(row.get("Etaj"), as_int=True),

            yard_area=extract_number(row.get("S. curte")),
            showcase_area=extract_number(row.get("S. vitrina")),

            location_raw=to_none_if_nan(row.get("Locație")),


            city=city_val,
            address=address_val,

            num_rooms=extract_number(row.get("Nr. camere"), as_int=True),

            price=extract_number(row.get("Preț")),

            street_frontage=extract_number(row.get("Front stradal")),

            url=to_none_if_nan(row.get("URL")),

            num_bathrooms=extract_number(row.get("Nr. bai"), as_int=True),
            num_garages=extract_number(row.get("Nr. garaje"), as_int=True),

            built_area=extract_number(row.get("S. construita")),
            land_area=extract_number(row.get("S. teren")),

            terrace_area=extract_number(row.get("S. terase")),
            balcony_area=extract_number(row.get("S. balcoane")),

            condominium=to_none_if_nan(row.get("Comp.")),
            num_balconies=extract_number(row.get("Nr. balcoane"), as_int=True),

            structural_system=to_none_if_nan(row.get("Structura rezistenta")),
            terraces=to_none_if_nan(row.get("Terase")),
            comfort=to_none_if_nan(row.get("Confort")),

            # Dacă vei face lookup după location_raw pentru location_id,
            # poți adăuga logica aici; momentan lași None:
            location_id=None,
        )

        db.add(listing)

    db.commit()
    db.close()

    return ConfirmationResponse()
