# GPX → SHP Converter

A user-friendly, local-only GPX to ESRI Shapefile converter.

## For end users

You do **not** need Python installed if you use a packaged release.

### Windows

1. Open the latest GitHub Release.
2. Download the file named similar to:
   `GPX_SHP_Converter_Windows_vX.X.X.zip`
3. Extract the ZIP to a normal folder.
4. Double-click:
   `Run_GPX_SHP_Converter.bat`

You can also launch `GPX_SHP_Converter.exe` directly.

The converter automatically chooses an available local port and opens the correct address in your browser. It usually starts at port 8501, but if that port is already in use it will try the next available port.

### macOS

1. Open the latest GitHub Release.
2. Download the file named similar to:
   `GPX_SHP_Converter_macOS_vX.X.X.zip`
3. Extract the ZIP.
4. Double-click:
   `Run_GPX_SHP_Converter.command`

If macOS blocks the launcher because the app is unsigned:

1. Right-click `Run_GPX_SHP_Converter.command`.
2. Choose **Open**.
3. Confirm **Open** when prompted.

The converter automatically chooses an available local port and opens the correct address in your browser. It usually starts at port 8501, but if that port is already in use it will try the next available port.

> Windows and macOS use separate release packages. Do not use the Windows ZIP on a Mac or the macOS ZIP on Windows.

## Basic workflow

1. Upload one or more GPX files.
2. Choose:
   - **Consolidated** — one shapefile containing all uploaded GPX/GEOREF features.
   - **Individual** — one shapefile per uploaded GPX file.
3. Optional: enable **Attach parcel attributes from CSV**.
4. If CSV mode is enabled:
   - the CSV must contain `GEOREF ID`;
   - every uploaded GPX filename must exist in `GEOREF ID`;
   - the `.gpx` extension is ignored when matching;
   - if even one GPX is missing from the CSV, conversion is blocked.
5. Click **Convert files**.
6. Download the generated ZIP.

## Data model

The converter treats the GPX file as the physical georeferenced parcel:

- **1 GPX filename = 1 GEOREF ID = 1 shapefile feature**
- Multiple CSV rows with the same GEOREF ID are valid.
- These repeated rows may represent rotational or multiple cropping records for the same parcel.
- Crop/planting rows do **not** duplicate the geometry.

When CSV attributes are enabled, the output ZIP contains:

- the shapefile with parcel/farmer-level attributes;
- summary crop fields in the shapefile:
  - `COMMODITY`
  - `PLANT_FROM`
  - `PLANT_TO`
  - `CROP_ROWS`
- `crop_records.csv`, containing every matching CSV row for the converted GEOREF IDs.

Example:

```text
GEOREF ID: ABC001
COMMODITY: Rice/Palay; Corn
PLANT_FROM: June; January
PLANT_TO: December; April
CROP_ROWS: 2
```

The exact source rows are still preserved in `crop_records.csv`.

## Current features

- Convert one or many GPX files.
- Fixed output CRS: **EPSG:4326 / WGS 84**.
- Consolidated mode.
- Individual mode.
- Optional CSV attribute attachment using **GEOREF ID**.
- Strict validation when CSV mode is enabled.
- One geometry per GPX / GEOREF ID.
- Multiple GPX tracks/segments in one file are combined into one multipart geometry.
- Commodity and planting summaries are visible directly in the shapefile.
- Full crop/planting records are preserved in `crop_records.csv`.
- Local-only processing.

## CSV matching

Example:

```text
R06-79-02-008-000001.gpx
```

matches:

```text
GEOREF ID = R06-79-02-008-000001
```

Rules:

1. The CSV must contain **GEOREF ID**.
2. GPX filenames are matched without the `.gpx` extension.
3. Every uploaded GPX must have at least one CSV match.
4. Extra CSV rows are allowed.
5. Multiple rows for the same matched GEOREF ID are valid and preserved as crop records.

## Output CRS

All shapefiles use:

**EPSG:4326 — WGS 84**

## Running from source

Developers can still run the project with Python:

```bash
python -m venv .venv
pip install -r requirements.txt
streamlit run app.py
```

## Building desktop releases

The repository includes automated GitHub Actions packaging for:

- Windows
- macOS

Changing `RELEASE_VERSION` triggers both builds and creates a GitHub Release with separate downloadable ZIP files.

See `WINDOWS_DISTRIBUTION.md` for additional Windows packaging notes.


## Local port behavior

The packaged app does not require a fixed port.

It checks ports from **8501 through 8599** and uses the first available one. This avoids conflicts with other Streamlit apps already running on the computer.

Examples:

- If 8501 is free → the app opens on port 8501.
- If 8501 is already in use → it may open on 8502.
- If 8501 and 8502 are both in use → it may open on 8503.

The browser is opened automatically using the selected port.
