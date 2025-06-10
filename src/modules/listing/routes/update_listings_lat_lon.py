# from fastapi import Depends
# from sqlalchemy import or_
# from sqlalchemy.orm import Session
# import re
# from extensions import get_db, SessionLocal
# from modules.listing.models.listing_model import ListingModel
# from modules.listing.models.listing_schemas import ListingUpdate
# from project_helpers.responses import ConfirmationResponse
# # from .router import router
# from modules.prediction.utils.get_property_location import geocode_address
#
# db = SessionLocal()
# # @router.post("-update", response_model=ConfirmationResponse)
# # async def update_listings(data: ListingUpdate, db: Session = Depends(get_db)):
# listingQuery = db.query(ListingModel).filter(or_(ListingModel.latitude == 0, ListingModel.longitude == 0, ListingModel.latitude.is_(None), ListingModel.longitude.is_(None), ListingModel.id < 245175))
# for listing in listingQuery.all():
#     # lat, lon = geocode_address(listing.location_raw)
#
#     lat, lon = geocode_address(listing.location_raw)
#     location = listing.location_raw
#     if lat is None or lon is None:
#         if ('Est' or 'Vest' or 'Sud' or 'Nord') in listing.location_raw:
#             location = location.replace(",", "")
#         if "Exterior" in location:
#             location = location.replace("Exterior", "")
#
#         lat, lon = geocode_address(location)
#
#     if lat is None or lon is None:
#         if ('Est' or 'Vest' or 'Sud' or 'Nord') in location:
#             location = location.split(" ")[1] + " " + location.split(" ")[0]
#
#             lat, lon = geocode_address(location)
#
#     if lat is None or lon is None:
#         if ("Central" or "Ultracentral") in location:
#             location = "Centru" + " " + location.split(",")[0]
#             lat, lon = geocode_address(location)
#
#     if lat is None or lon is None:
#         if "/" in location:
#             street = location.split("/")[1]
#             city = location.split("/")[0].split(",")[0]
#             location = city + " " + street
#         lat, lon = geocode_address(location)
#
#     if lat is None or lon is None:
#         location = listing.city
#         lat, lon = geocode_address(location)
#
#     listing.latitude = lat or 0
#     listing.longitude = lon or 0
#     # print(lat, lon, str(listing.external_id).strip())
#     print(str(listing.external_id).strip(), listing.location_raw, location, lat, lon,)
#
# db.commit()
#
# db.close()
# print("Updated succesfully")
#     # return ConfirmationResponse()
