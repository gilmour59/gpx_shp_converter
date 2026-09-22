# TODO

## Current MVP

- [x] Initialize Python project
- [x] Add dependencies
- [x] Add GPX parser
- [x] Create one feature per GPX/GEOREF ID
- [x] Combine internal GPX segments into one geometry
- [x] Set CRS to EPSG:4326
- [x] Export ESRI Shapefile
- [x] Consolidated mode
- [x] Individual mode
- [x] Streamlit interface
- [x] Multiple GPX upload
- [x] Optional CSV attribute attachment
- [x] GPX filename to GEOREF ID matching
- [x] Fail entire conversion if any GPX file is missing from CSV
- [x] Treat repeated GEOREF rows as valid crop records
- [x] Keep one geometry while preserving all crop rows
- [x] Export crop_records.csv with the shapefile
- [x] Automated tests for one-to-many crop records

## Next

- [ ] Test with real GPX files and the provided field CSV
- [ ] Confirm shapefile and crop_records.csv workflow in QGIS
- [ ] Add a structured GPX-to-GEOREF match table
- [ ] Add crop-record count and commodity summary in the UI
- [ ] Add map preview
- [ ] Add optional closed-track polygon output
- [ ] Add elevation and timestamp handling
- [ ] Add CI workflow for pytest
- [ ] Pin dependency versions after compatibility testing
- [ ] Package for easy Windows/local use
