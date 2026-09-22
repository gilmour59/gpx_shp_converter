# GPX → SHP Converter

A user-friendly, local-only GPX to ESRI Shapefile converter.

## Current features

- Convert one or many GPX files.
- Fixed output CRS: **EPSG:4326 / WGS 84**.
- Consolidated mode: create one shapefile containing features from all GPX files.
- Individual mode: create one shapefile for every GPX file.
- Optional CSV attribute attachment using **GEOREF ID**.
- Strict CSV validation: if any uploaded GPX filename is missing from GEOREF ID, conversion is blocked.
- GPX track segments are exported as LineString geometries.
- Source filename, track name, track number, segment number, and point count are preserved.
- Shapefile components are packaged automatically into ZIP files.
- Files are processed locally by the application.

## CSV attribute matching

When **Attach attributes from CSV** is enabled:

1. The CSV must contain a column named **GEOREF ID**.
2. Each uploaded GPX filename is matched to GEOREF ID using the filename without the .gpx extension.
3. Example: **R06-79-02-008-000001.gpx** matches **R06-79-02-008-000001**.
4. Every uploaded GPX must have a CSV match. If one or more are missing, the entire conversion is blocked.
5. Extra rows in the CSV are allowed.
6. Duplicate GEOREF IDs are reported as warnings. The first matching CSV row is currently used to avoid multiplying geometry.
7. Matched CSV columns are written into the Shapefile DBF attributes.

The app uses short DBF-safe aliases for long field names because the Shapefile format limits attribute field names.

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

The app will open in your browser on the local machine.

## Output

A Shapefile is made up of several files, commonly including .shp, .shx, .dbf, and .prj. The application packages these components into ZIP files automatically.

## Conversion behavior

### Consolidated

All valid GPX track segments become separate features in one shapefile. They are not merged into one giant line, so their source files remain identifiable.

### Individual

Each GPX file becomes its own shapefile folder inside one downloadable ZIP archive.

## CRS

All current outputs use **EPSG:4326 — WGS 84**.

GPX coordinates are interpreted as longitude/latitude coordinates. Geometry coordinates are created in the correct GIS order: longitude, latitude.

## Development

Run tests with: pytest

See ROADMAP.md for planned features and TODO.md for the current task list.
