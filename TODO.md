# TODO

## Current MVP

- [x] Initialize Python project
- [x] Add dependencies
- [x] Add GPX parser
- [x] Convert track segments to LineString
- [x] Create GeoDataFrame
- [x] Set CRS to EPSG:4326
- [x] Export ESRI Shapefile
- [x] Consolidated mode
- [x] Individual mode
- [x] Preserve source filename
- [x] Preserve track name
- [x] Preserve track and segment numbers
- [x] ZIP shapefile components
- [x] Streamlit interface
- [x] Multiple GPX upload
- [x] Basic file validation
- [x] Basic automated tests\n- [x] Optional CSV attribute attachment\n- [x] GPX filename to GEOREF ID matching\n- [x] Fail entire conversion if any GPX file is missing from CSV

## Next\n\n- [ ] Decide stricter policy for duplicate GEOREF IDs with conflicting attributes\n- [ ] Show a GPX-to-CSV match table before conversion

- [ ] Test with real GPX files from actual field devices/apps
- [ ] Confirm shapefiles open correctly in QGIS
- [ ] Add a structured file inspection table
- [ ] Add progress reporting during conversion
- [ ] Add map preview
- [ ] Add routes and waypoints
- [ ] Add optional closed-track polygon output
- [ ] Add elevation and timestamp handling
- [ ] Add CI workflow for pytest
- [ ] Pin dependency versions after successful compatibility testing
- [ ] Package for easy Windows/local use
