from datetime import datetime

from sqlalchemy import Column, BigInteger, Integer, DateTime, Float, Text, Enum, ForeignKey
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
    location_id = Column(Integer, ForeignKey("locations.id"))  # optional FK; kept for relational mapping
    inserted_at = Column(DateTime, default=lambda: datetime.now())

    # ─────────────────────────────────────────────────────────────
    # NEW FIELDS (one per Excel column), with appropriate types
    # ─────────────────────────────────────────────────────────────
    classification = Column(Text)            # Excel: “Clasificare”
    land_classification = Column(Text)       # Excel: “Clasificare teren”

    useful_area_total = Column(Float)        # Excel: “S. utila totala”
    useful_area = Column(Float)              # Excel: “S. utila”

    num_kitchens = Column(Integer)           # Excel: “Nr. bucatarii”
    num_parking = Column(Integer)            # Excel: “Nr. parcari”

    floor = Column(Integer)                  # Excel: “Etaj”

    yard_area = Column(Float)                # Excel: “S. curte”
    showcase_area = Column(Float)            # Excel: “S. vitrina”

    # Now split into two fields instead of `location_raw`:
    location_raw = Column(Text, nullable=True)
    city = Column(Text, nullable=True)
    address = Column(Text, nullable=True)

    num_rooms = Column(Integer)              # Excel: “Nr. camere”

    price = Column(Float)                    # Excel: “Preț”
    street_frontage = Column(Float)          # Excel: “Front stradal”

    url = Column(Text)                       # Excel: “URL”

    num_bathrooms = Column(Integer)          # Excel: “Nr. bai”
    num_garages = Column(Integer)            # Excel: “Nr. garaje”

    built_area = Column(Float)               # Excel: “S. construita”
    land_area = Column(Float)                # Excel: “S. teren”

    terrace_area = Column(Float)             # Excel: “S. terase”
    balcony_area = Column(Float)             # Excel: “S. balcoane”

    condominium = Column(Text)               # Excel: “Comp.” (e.g. condo fee / building)
    num_balconies = Column(Integer)          # Excel: “Nr. balcoane”

    structural_system = Column(Text)         # Excel: “Structura rezistenta”
    terraces = Column(Text)                  # Excel: “Terase” (e.g. presence/description)
    comfort = Column(Text)                   # Excel: “Confort”

    # ─────────────────────────────────────────────────────────────
    # RELATIONSHIPS
    # ─────────────────────────────────────────────────────────────
    location = relationship("LocationModel", backref="listings")
