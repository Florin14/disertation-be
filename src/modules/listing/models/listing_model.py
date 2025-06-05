from datetime import datetime

from sqlalchemy import Column, BigInteger, Integer, DateTime, Float, Text, Enum, ForeignKey, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from constants import ListingSource
from extensions import BaseModel


class ListingModel(BaseModel):
    __tablename__ = "listings"

    # ─────────────────────────────────────────────────────────────
    # Existing PK / timestamps / minimal FKs / unique identifiers
    # ─────────────────────────────────────────────────────────────
    id = Column(BigInteger, primary_key=True, index=True)
    external_id = Column(Text, unique=True, index=True)     # maps to Excel “ID”
    # location_id = Column(Integer, ForeignKey("locations.id"))  # optional FK; kept for relational mapping
    inserted_at = Column(DateTime, default=lambda: datetime.now())

    # ─────────────────────────────────────────────────────────────
    # NEW FIELDS (one per Excel column), with appropriate types
    # ─────────────────────────────────────────────────────────────
    classification = Column(Text)            # Excel: “Clasificare”
    land_classification = Column(Text)       # Excel: “Clasificare teren”

    useful_area_total = Column(Float, default=0)        # Excel: “S. utila totala”
    useful_area = Column(Float, default=0)              # Excel: “S. utila”

    num_kitchens = Column(Integer, default=0)           # Excel: “Nr. bucatarii”
    has_parking_space = Column(Boolean, default=False)            # Excel: “Nr. parcari”

    floor = Column(Integer, default=0)                  # Excel: “Etaj”

    yard_area = Column(Float, default=0)                # Excel: “S. curte”

    # Now split into two fields instead of `location_raw`:
    location_raw = Column(Text, nullable=True)
    city = Column(Text, nullable=True)
    address = Column(Text, nullable=True)
    for_sale = Column(Boolean, default=False)  # Indicates if the listing is for sale or rent

    num_rooms = Column(Integer, default=0)              # Excel: “Nr. camere”

    price = Column(Float, default=0)                    # Excel: “Preț”

    url = Column(Text)                       # Excel: “URL”

    num_bathrooms = Column(Integer, default=0)          # Excel: “Nr. bai”
    has_garage = Column(Boolean, default=False)            # Excel: “Nr. garaje”

    built_area = Column(Float, default=0)               # Excel: “S. construita”
    built_year = Column(Integer, nullable=True)               # Excel: “S. construita”

    land_area = Column(Float, default=0)                # Excel: “S. teren”
    structure = Column(Text)               # Excel: “Structură” (e.g. brick, concrete)
    property_type = Column(Text)               # Excel: “Tip imobil” (e.g. house, apartment)
    condominium = Column(Text)               # Excel: “Comp.” (e.g. condo fee / building)
    has_balconies = Column(Boolean, default=False)          # Excel: “Nr. balcoane”

    has_terrace = Column(Boolean, default=False)                  # Excel: “Terase” (e.g. presence/description)
    comfort = Column(Text)                   # Excel: “Confort”

    # ─────────────────────────────────────────────────────────────
    # RELATIONSHIPS
    # ─────────────────────────────────────────────────────────────
    # location = relationship("LocationModel", backref="listings")
