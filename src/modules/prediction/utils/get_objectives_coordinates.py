import osmnx as ox
import pandas as pd
from shapely.geometry import Point

# 4.4.1. Obținem poligonul București (cum am arătat mai sus)
place_name = "Cluj-Napoca, Romania"
city = ox.geocode_to_gdf(place_name).iloc[0]
city_polygon = city.geometry

# 4.4.2. Definim dicționarul cu tag-uri pentru fiecare tip de POI
poi_tags = {
    "metro": {"railway": "station", "station": "subway"},
    "bus_stop": {"highway": "bus_stop"},
    "park": {"leisure": "park"},
    "school": {"amenity": "school"},
    "hospital": {"amenity": "hospital"},
    # poți adăuga și “library”: {"amenity": "library"} sau altele
}

# 4.4.3. Vom construi o listă de DataFrame-uri parțiale, apoi le concatenăm
poi_frames = []

for poi_type, tags in poi_tags.items():
    # Cerem OSM nodurile (geometrii punct) + poligoane (vom extrage centroids)
    gdf = ox.features_from_polygon(city_polygon, tags)
    # .features_from_polygon aduce noduri și poligoane (dar multe categorii sunt poligoane)

    # 4.4.4. Extragem doar geometria punct și pentru poligoane luăm centrul
    records = []
    for idx, row in gdf.iterrows():
        geom = row.geometry
        # Dacă e poligon sau multilinel, obținem centroid:
        if geom.geom_type in ["Polygon", "MultiPolygon", "LineString", "MultiLineString"]:
            pt = geom.centroid
        elif geom.geom_type == "Point":
            pt = geom
        else:
            # Dacă e alt tip (de ex. `Relation`), trecem peste
            continue

        name = row.get("name", f"{poi_type}_unknown")
        records.append({
            "type": poi_type,
            "name": name,
            "latitude": pt.y,
            "longitude": pt.x
        })

    df_poi = pd.DataFrame(records)
    print(f" - {poi_type}: {len(df_poi)} obiective găsite.")
    poi_frames.append(df_poi)

# 4.4.5. Concatenăm totul într-un singur DataFrame
poi_df = pd.concat(poi_frames, ignore_index=True)

# 4.4.6. Dacă vrei să adaugi manual “center” (centrul orașului)
centroid = city_polygon.centroid
center_row = {
    "type": "center",
    "name": "City Center (centroid)",
    "latitude": centroid.y,
    "longitude": centroid.x
}
poi_df = pd.concat([poi_df, pd.DataFrame([center_row])], ignore_index=True)

# 4.4.7. Salvăm într-un CSV (opțional)
poi_df.to_csv("poi_bucharest.csv", index=False)

print(f"Total POI-uri (toate categoriile + center): {len(poi_df)}")
