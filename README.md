# GPX → SHP Converter

A user-friendly, local-only GPX to ESRI Shapefile converter.

## Data model

The converter treats the GPX file as the physical georeferenced parcel:

- **1 GPX filename = 1 GEOREF ID = 1 shapefile feature**
- Multiple CSV rows with the same GEOREF ID are valid.
- These repeated rows can represent rotational or multiple cropping records for the same parcel.
- Crop/planting rows do **not** duplicate the geometry.

When CSV attributes are enabled, the output ZIP contains:

- the shapefile with parcel/farmer-level attributes;
- **crop_records.csv**, containing every matching CSV row for the converted GEOREF IDs.

## Current features

- Convert one or many GPX files.
- Fixed output CRS: **EPSG:4326 / WGS 84**.
- Consolidated mode: one shapefile containing one feature per uploaded GPX/GEOREF.
- Individual mode: one shapefile folder per uploaded GPX/GEOREF.
- Optional CSV attribute attachment using **GEOREF ID**.
- Strict validation: if any uploaded GPX filename is missing from GEOREF ID, conversion is blocked.
- Multiple crop rows for one GEOREF ID are preserved in the related crop table.
- Multiple GPX tracks/segments in one file are combined into one multipart geometry.
- Files are processed locally by the application.

## CSV matching

1. The CSV must contain **GEOREF ID**.
2. GPX filenames are matched without the .gpx extension.
3. Example: **R06-79-02-008-000001.gpx** matches **R06-79-02-008-000001**.
4. Every uploaded GPX must have at least one CSV match.
5. Extra CSV rows are allowed.
6. Multiple rows for a matched GEOREF ID are valid and all are exported to **crop_records.csv**.

Parcel-level attributes such as RSBSA ID, parcel ID, farm type, area, ownership, and location are written to the shapefile DBF. Commodity and planting schedule remain in the related crop table so the one-to-many relationship is not lost.

## Tech stack

- Python
- Streamlit
- gpxpy
- pandas
- GeoPandas
- Shapely
- Pyogrio / GDAL
- PyProj
- pytest

## Run locally

1. Create a virtual environment.
2. Install dependencies with: pip install -r requirements.txt
3. Start the app with: streamlit run app.py

## Output

A Shapefile is made up of several files, commonly including .shp, .shx, .dbf, and .prj. These are automatically packaged into ZIP files.

When CSV attributes are used, the ZIP also includes **crop_records.csv**.

## CRS

All outputs use **EPSG:4326 — WGS 84**.
