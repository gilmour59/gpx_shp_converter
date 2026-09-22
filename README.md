# GPX → SHP Converter

A user-friendly, local-only GPX to ESRI Shapefile converter.

## Current features

- Convert one or many GPX files.
- Fixed output CRS: **EPSG:4326 / WGS 84**.
- Consolidated mode: create one shapefile containing features from all GPX files.
- Individual mode: create one shapefile for every GPX file.
- GPX track segments are exported as LineString geometries.
- Source filename, track name, track number, segment number, and point count are preserved.
- Shapefile components are packaged automatically into ZIP files.
- Files are processed locally by the application.

## Tech stack

- Python
- Streamlit
- gpxpy
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
