import os
import json
from pathlib import Path
import pandas as pd
import requests
import folium

ACCESS_TOKEN = os.getenv("MAPBOX_TOKEN", "").strip() or "PASTE_TOKEN_HERE"
MAPBOX_USERNAME = "qwinsor"
MAPBOX_STYLE_ID = "cmm3wsyxj001i01scgx0w4dvo"
TILES_URL = f"https://api.mapbox.com/styles/v1/{MAPBOX_USERNAME}/{MAPBOX_STYLE_ID}/tiles/256/{{z}}/{{x}}/{{y}}@2x?access_token={ACCESS_TOKEN}"
GEOCODE_URL = "https://api.mapbox.com/search/geocode/v6/forward"

SCRIPT_DIR = Path(__file__).resolve().parent
CSV_PATH = SCRIPT_DIR / "hometown_locations.csv"
OUTPUT_HTML = SCRIPT_DIR / "chicago_map.html"
CACHE_PATH = SCRIPT_DIR / "geocode_cache.json"

type_to_color = {
    "Food": "darkred",
    "Sports": "gray",
    "Club": "black",
    "Golf": "darkgreen",
    "School": "darkpurple",
    "Landmark": "lightgray",
    "Cultural": "cadetblue",
    "Park": "green",
}

def load_cache():
    if CACHE_PATH.exists():
        try:
            return json.loads(CACHE_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}

def save_cache(cache):
    CACHE_PATH.write_text(json.dumps(cache, indent=2), encoding="utf-8")

def geocode(address, cache):
    a = address.strip()
    if not a:
        return None
    if a in cache:
        return cache[a]
    r = requests.get(GEOCODE_URL, params={"q": a, "access_token": ACCESS_TOKEN, "limit": 1}, timeout=25)
    r.raise_for_status()
    data = r.json()
    feats = data.get("features", [])
    if not feats:
        cache[a] = None
        return None
    lon, lat = feats[0]["geometry"]["coordinates"]
    cache[a] = {"lat": lat, "lon": lon}
    return cache[a]

def popup_html(name, desc, img):
    img = (img or "").strip()
    img_block = ""
    if img and img.lower() != "nan":
        img_block = f'<div style="margin-top:8px;"><img src="{img}" style="width:260px; border-radius:10px; border:1px solid #333;"></div>'
    return f"""
<div style="background:#111; color:#f2f2f2; padding:10px; border-radius:12px; width:290px; border:1px solid #333;">
  <div style="font-size:16px; font-weight:800; margin-bottom:6px;">{name}</div>
  <div style="font-size:13px; line-height:1.35; color:#e6e6e6;">{desc}</div>
  {img_block}
</div>
""".strip()

def main():
    if not ACCESS_TOKEN or "PASTE_TOKEN_HERE" in ACCESS_TOKEN:
        raise ValueError("need a mapbox token (set MAPBOX_TOKEN or paste it in ACCESS_TOKEN)")
    if not CSV_PATH.exists():
        raise FileNotFoundError(f"cant find csv: {CSV_PATH}")

    df = pd.read_csv(CSV_PATH)
    for col in ["Name", "Address", "Type", "Description", "Image_URL"]:
        if col not in df.columns:
            raise ValueError("csv needs columns: Name, Address, Type, Description, Image_URL")

    m = folium.Map(location=[41.8781, -87.6298], zoom_start=11, control_scale=True, tiles=None)

    folium.TileLayer("OpenStreetMap", name="OSM (test)", overlay=False, control=True).add_to(m)

    folium.TileLayer(
        tiles=TILES_URL,
        attr="Mapbox",
        name="Gotham Chicago",
        overlay=False,
        control=True,
        max_zoom=18,
        tile_size=256,
        zoom_offset=0
    ).add_to(m)

    cache = load_cache()
    added = 0
    bounds = []

    for _, row in df.iterrows():
        name = str(row["Name"]).strip()
        address = str(row["Address"]).strip()
        typ = str(row["Type"]).strip()
        desc = str(row["Description"]).strip()
        img = str(row.get("Image_URL", "")).strip()

        c = geocode(address, cache)
        if not c:
            print("geocode failed:", name, "|", address)
            continue

        lat, lon = c["lat"], c["lon"]
        bounds.append([lat, lon])

        folium.Marker(
            location=[lat, lon],
            tooltip=name,
            popup=folium.Popup(popup_html(name, desc, img), max_width=330),
            icon=folium.Icon(color=type_to_color.get(typ, "gray"), icon="info-sign"),
        ).add_to(m)

        added += 1

    save_cache(cache)

    if bounds:
        m.fit_bounds(bounds, padding=(25, 25))

    folium.LayerControl(collapsed=False).add_to(m)

    m.save(str(OUTPUT_HTML))
    print("Added", added, "markers")
    print("Saved:", OUTPUT_HTML)

if __name__ == "__main__":
    main()