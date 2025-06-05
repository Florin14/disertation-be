import asyncio
from typing import List, Literal, Union
import os
import time
from datetime import datetime
import tempfile
import httpx
import pandas as pd
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from starlette.responses import FileResponse

from .router import router
import xlsxwriter

# # ----------------------------------------
# # CONFIGURATION
# # ----------------------------------------
# IDEALISTA_CLIENT_ID = os.getenv("IDEALISTA_CLIENT_ID")
# IDEALISTA_CLIENT_SECRET = os.getenv("IDEALISTA_CLIENT_SECRET")
#
# # Nestoria hosts and sample seed places
# NESTORIA_HOSTS = {
#     "uk": "https://api.nestoria.co.uk/api",
#     "au": "https://api.nestoria.com.au/api",
#     "es": "https://api.nestoria.es/api",
#     "fr": "https://api.nestoria.fr/api",
# }
# seed_places = {
#     "uk": ["London", "Manchester"],
#     "au": ["Sydney", "Melbourne"],
#     "es": ["Madrid", "Barcelona"],
#     "fr": ["Paris", "Lyon"],
# }
# # Idealista seed centers
# seed_centers = {
#     "es": "40.4168,-3.7038",    # Madrid
#     "it": "41.9028,12.4964",    # Rome
#     "pt": "38.7223,-9.1393",    # Lisbon
# }
#
# # ----------------------------------------
# # HELPERS: API FETCH
# # ----------------------------------------
# async def get_idealista_token(client: httpx.AsyncClient, client_id: str, client_secret: str) -> str:
#     url = "https://api.idealista.com/oauth/token"
#     data = {"grant_type": "client_credentials", "scope": "read"}
#     resp = await client.post(url, data=data, auth=(client_id, client_secret))
#     resp.raise_for_status()
#     return resp.json().get("access_token", "")
#
# async def fetch_nestoria_listings(client: httpx.AsyncClient, country: str, place: str,
#                                    operation: Literal["sale","rent"] = "sale",
#                                    page: int = 1, page_size: int = 50) -> List[dict]:
#     params = {
#         "encoding": "json",
#         "pretty": "1",
#         "action": "search_listings",
#         "country": country,
#         "listing_type": "buy" if operation == "sale" else "rent",
#         "page": page,
#         "number_of_results": page_size,
#         "place_name": place,
#     }
#     resp = await client.get(NESTORIA_HOSTS[country], params=params)
#     resp.raise_for_status()
#     data = resp.json().get("response", {})
#     listings = data.get("listings") or []
#     # log if unexpected format
#     if not isinstance(listings, list):
#         raise HTTPException(502, f"Unexpected Nestoria response format for {country}/{place}: {listings}")
#     return listings
#
# async def fetch_idealista_listings(client: httpx.AsyncClient, token: str, country: str, center: str,
#                                     operation: Literal["sale","rent"] = "sale",
#                                     page: int = 1, page_size: int = 50,
#                                     distance: int = 2000) -> List[dict]:
#     url = f"https://api.idealista.com/3.5/{country}/search"
#     headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
#     params = {
#         "operation": operation,
#         "propertyType": "homes",
#         "center": center,
#         "distance": distance,
#         "maxItems": page_size,
#         "numPage": page - 1,
#     }
#     resp = await client.get(url, headers=headers, params=params)
#     resp.raise_for_status()
#     data = resp.json()
#     listings = data.get("elementList") or []
#     if not isinstance(listings, list):
#         raise HTTPException(502, f"Unexpected Idealista response format for {country}: {listings}")
#     return listings

# ----------------------------------------
# ENDPOINT /search
# ----------------------------------------
# @router.get("-search", summary="Fetch real estate data and save Excel locally")
# async def search_all():
#     """
#     Fetch listings from Nestoria and Idealista, aggregate into an Excel file with separate sheets per country, and save it in the package directory.
#     """
#     # Build output filepath next to this module
#     async with httpx.AsyncClient(timeout=10.0) as client:
#         # Create Excel file path
#         package_dir = os.path.dirname(__file__)
#         now = datetime.now().strftime("%Y%m%d_%H%M%S")
#         filename = f"realestate_{now}.xlsx"
#         filepath = os.path.join(package_dir, filename)
#         writer = pd.ExcelWriter(filepath, engine="xlsxwriter")
#
#         # 1) Nestoria data
#         for cc, places in seed_places.items():
#             all_listings = []
#             for place in places:
#                 page = 1
#                 while True:
#                     listings = await fetch_nestoria_listings(client, cc, place, operation="sale", page=page)
#                     print(f"[Nestoria {cc}] fetched {len(listings)} listings for {place} page {page}")
#                     if not listings:
#                         break
#                     all_listings.extend(listings)
#                     page += 1
#                     await asyncio.sleep(1)
#             if all_listings:
#                 pd.DataFrame(all_listings).to_excel(writer, sheet_name=f"nestoria_{cc}", index=False)

        # 2) Idealista data
        # if not IDEALISTA_CLIENT_ID or not IDEALISTA_CLIENT_SECRET:
        #     raise HTTPException(500, "Missing IDEALISTA_CLIENT_ID or IDEALISTA_CLIENT_SECRET env variables")
        # token = await get_idealista_token(client, IDEALISTA_CLIENT_ID, IDEALISTA_CLIENT_SECRET)
        # for cc, center in seed_centers.items():
        #     all_listings = []
        #     page = 1
        #     while True:
        #         listings = await fetch_idealista_listings(client, token, cc, center, operation="sale", page=page)
        #         print(f"[Idealista {cc}] fetched {len(listings)} listings page {page}")
        #         if not listings:
        #             break
        #         all_listings.extend(listings)
        #         page += 1
        #         await asyncio.sleep(1)
        #     if all_listings:
        #         pd.DataFrame(all_listings).to_excel(writer, sheet_name=f"idealista_{cc}", index=False)

        # Save workbook
    #     writer.close()
    # return {"status": "saved", "file": filename}


import requests
import time
import random
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup

# =========== CONFIGURARE ===========

START_SITEMAP = 'https://www.imobiliare.ro/sitemap-listings-index-ro.xml'  # sitemap național
PROXIES = {}  # dacă ai proxy, pune aici
RATE_LIMIT = 1  # secunde între cereri

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) '
    'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 '
    '(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36',
    # ...+ alte variante
]

# ====================================

def get_listing_urls(sitemap_url):
    """Parcurge recursiv sitemap-urile și returnează toate URL-urile de anunț."""
    r = requests.get(sitemap_url, proxies=PROXIES, timeout=10)
    r.raise_for_status()
    root = ET.fromstring(r.content)
    urls = [loc.text for loc in root.findall('.//{*}loc')]
    listings = []
    for u in urls[1:5]:
        if u.endswith('.xml'):
            listings += get_listing_urls(u)
        else:
            listings.append(u)
    return listings

def parse_listing(url):
    """Parsează o pagină de anunț și extrage cât mai multe câmpuri posibile."""
    headers = {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'ro-RO,ro;q=0.9',
        'Referer': 'https://www.imobiliare.ro/'
    }
    r = requests.get(url, headers=headers, proxies=PROXIES, timeout=10)
    if r.status_code == 403:
        # poți integra cloudscraper aici pentru bypass Cloudflare
        return None
    r.raise_for_status()

    soup = BeautifulSoup(r.text, 'html.parser')
    data = {'url': url}

    # --- 1. Titlu ---
    h1 = soup.find('h1')
    data['title'] = h1.get_text(strip=True) if h1 else None

    # --- 2. Preț ---
    price_tag = (
        soup.select_one('[data-testid="listing-price"]') or
        soup.select_one('.pret') or
        soup.find(text=lambda t: '€' in t or 'lei' in t)
    )
    data['price'] = price_tag.get_text(strip=True) if getattr(price_tag, 'get_text', None) else None

    # --- 3. Breadcrumbs (pentru city + cartier) ---
    crumbs = [li.get_text(strip=True) for li in soup.select('ul.breadcrumb-list li')]
    data['county'] = crumbs[0] if len(crumbs) > 0 else None
    data['city']   = crumbs[1] if len(crumbs) > 1 else None
    data['neighborhood'] = crumbs[2] if len(crumbs) > 2 else None

    # --- 4. Adresă / stradă ---
    addr = (
        soup.select_one('[data-testid="listing-address"]') or
        soup.select_one('.adresa') or
        soup.find('address')
    )
    data['address'] = addr.get_text(strip=True) if addr else None

    # --- 5. Alte caracteristici din listă (suprafață, camere, etaj, an construcție etc.) ---
    # multe site-uri pun aceste date într-un tabel sau listă de rânduri
    data['features'] = {}
    for row in soup.select('ul[itemprop="features"] li, .listing-params li'):
        # încearcă să extragi: <span class="label">Suprafață</span><span class="value">35 m²</span>
        label = row.select_one('.label, .param-label')
        value = row.select_one('.value, .param-value')
        if label and value:
            key = label.get_text(strip=True)
            val = value.get_text(strip=True)
            data['features'][key] = val

    # --- 6. Descriere ---
    desc = soup.select_one('[data-testid="listing-description"]') or soup.select_one('.description')
    data['description'] = desc.get_text(strip=True) if desc else None

    # --- 7. Agent / Persoană de contact ---
    agent = soup.select_one('.agent-name, .contact-person')
    data['agent'] = agent.get_text(strip=True) if agent else None

    return data if data.get('title') and data.get('price') else None

@router.get("-search", summary="Fetch real estate data and save Excel locally")
async def search_all():
    index_sitemap = 'https://www.imobiliare.ro/sitemap-listings-index-ro.xml'
    all_urls = get_listing_urls(index_sitemap)
    rezultate = []
    for url in all_urls[1:5]:
        data = parse_listing(url)
        if data:
            rezultate.append(data)
        time.sleep(1)

    # ——— Salvează rezultatele în Excel ———
    df = pd.DataFrame(rezultate)
    # directorul curent al acestui fișier .py
    package_dir = os.path.dirname(__file__)
    now = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"realestate_{now}.xlsx"
    file_path = os.path.join(package_dir, filename)
    df.to_excel(file_path, index=False)

    # ——— Returnează fișierul pentru descărcare ———
    return FileResponse(
        path=str(file_path),
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename="scraped_data.xlsx"
    )