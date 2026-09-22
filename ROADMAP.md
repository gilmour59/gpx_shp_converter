# GPX to SHP Converter Roadmap

## Product goal

Build a simple local-only tool that lets non-technical users convert GPX files into ESRI Shapefiles without needing QGIS or command-line GIS knowledge.

The output CRS is fixed to **EPSG:4326 / WGS 84**.

## Phase 1 — MVP

- [x] Local Streamlit interface
- [x] Multiple GPX upload
- [x] GPX track conversion
- [x] One geometry per GPX/GEOREF ID
- [x] Combine multiple track segments into one multipart feature
- [x] EPSG:4326 / WGS 84 output
- [x] Consolidated conversion
- [x] Individual conversion
- [x] Optional CSV attribute import by GEOREF ID
- [x] Block conversion when any GPX filename is missing from CSV
- [x] Support repeated GEOREF rows as one-to-many crop records
- [x] Keep parcel-level attributes in the shapefile
- [x] Export full crop/planting rows to crop_records.csv
- [x] ZIP Shapefile components
- [x] Basic validation and automated tests

## Phase 2 — User experience

- [ ] GPX-to-CSV match summary table
- [ ] Crop-record count per GEOREF in preview
- [ ] File summary table
- [ ] Conversion progress indicator
- [ ] Better duplicate filename handling
- [ ] Clearer partial-success/error summaries
- [ ] Add screenshots and usage examples

## Phase 3 — GIS features

- [ ] Optional closed-track to Polygon conversion
- [ ] GPX routes to LineString
- [ ] GPX waypoints to Point
- [ ] Preserve elevation values
- [ ] Preserve timestamps
- [ ] Track length summary
- [ ] Bounding box metadata
- [ ] Geometry quality checks

## Phase 4 — Preview and quality control

- [ ] Interactive local map preview
- [ ] Show uploaded parcels as map layers
- [ ] Detect duplicate uploaded GPX files
- [ ] Coordinate plausibility warnings
- [ ] Optional Philippines bounds warning
- [ ] Preview parcel and crop attributes before export

## Phase 5 — Distribution

- [ ] Lock tested dependency versions
- [ ] Add Windows launcher
- [ ] Investigate PyInstaller packaging
- [ ] Provide one-click local startup
- [ ] Create release ZIP
