from sqlalchemy import Column, Integer, String, Float, Date, BigInteger, ForeignKey
from sqlalchemy.orm import relationship

from extensions import BaseModel


class PriceHistoryModel(BaseModel):
    __tablename__ = "price_history"

    id = Column(BigInteger, primary_key=True, index=True)
    listing_id = Column(BigInteger, ForeignKey("listings.id", ondelete="CASCADE"))
    price_eur = Column(Float)
    collected_on = Column(Date, index=True)

    listing = relationship("ListingModel", backref="prices")