# GPX to SHP Converter Roadmap

## Product goal

Build a simple local-only tool that lets non-technical users convert GPX files into ESRI Shapefiles without needing QGIS or command-line GIS knowledge.

The output CRS is fixed to **EPSG:4326 / WGS 84**.

## Phase 1 — MVP

- [x] Local Streamlit interface
- [x] Multiple GPX upload
- [x] GPX track segment to LineString conversion
- [x] EPSG:4326 / WGS 84 output
- [x] Consolidated conversion
- [x] Individual conversion
- [x] Source filename and GPX track metadata
- [x] ZIP Shapefile components
- [x] Basic validation and friendly errors
- [x] Initial automated tests\n- [x] Optional CSV attribute import by GEOREF ID\n- [x] Block conversion when any GPX filename is missing from CSV

## Phase 2 — User experience\n\n- [ ] Improve duplicate GEOREF ID conflict handling\n- [ ] Add CSV match summary table

- [ ] File summary table instead of one message per file
- [ ] Conversion progress indicator
- [ ] Better duplicate filename handling
- [ ] Clearer per-file warnings and partial-success summary
- [ ] Remember last selected conversion mode during the local session
- [ ] Add a simple help/about section
- [ ] Add drag-and-drop examples and screenshots to README

## Phase 3 — GIS features

- [ ] GPX routes to LineString
- [ ] GPX waypoints to Point
- [ ] Optional closed-track to Polygon conversion
- [ ] Preserve elevation values
- [ ] Preserve timestamps
- [ ] Track length summary
- [ ] Bounding box metadata
- [ ] Geometry quality checks

## Phase 4 — Preview and quality control

- [ ] Interactive local map preview
- [ ] Show uploaded tracks using distinct map layers
- [ ] Detect duplicate files
- [ ] Coordinate plausibility warnings
- [ ] Optional Philippines bounds warning
- [ ] Detect suspiciously short or empty tracks
- [ ] Preview feature attributes before export

## Phase 5 — Distribution

- [ ] Lock tested dependency versions
- [ ] Add Windows launcher
- [ ] Investigate PyInstaller packaging
- [ ] Provide one-click local startup
- [ ] Create release ZIP
- [ ] Add release checklist
