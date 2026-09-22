from __future__ import annotations

from dataclasses import dataclass

import streamlit as st

from src.converter import OUTPUT_CRS, features_to_gdf
from src.csv_attributes import (
    CSVValidationError,
    build_attribute_lookup,
    read_attribute_csv,
    validate_gpx_files_in_csv,
)
from src.exporter import individual_shapefiles_to_zip, shapefile_to_zip
from src.gpx_parser import GPXParseError, GPXFeature, parse_gpx


@dataclass
class ParsedUpload:
    filename: str
    features: list[GPXFeature]


st.set_page_config(
    page_title="GPX to SHP Converter",
    page_icon="🗺️",
    layout="centered",
)

st.title("GPX → Shapefile Converter")
st.write(
    "Convert one or more GPX files into GIS-ready ESRI Shapefiles. "
    "Everything runs locally on this computer."
)

with st.container(border=True):
    col1, col2 = st.columns(2)
    col1.metric("Output CRS", "EPSG:4326")
    col2.metric("Coordinate System", "WGS 84")
    st.caption("The output CRS is fixed to EPSG:4326 / WGS 84.")

uploaded_files = st.file_uploader(
    "Drop GPX files here or browse",
    type=["gpx"],
    accept_multiple_files=True,
    help="You can upload one or many .gpx files at the same time.",
)

attach_csv = st.checkbox(
    "Attach attributes from CSV",
    help=(
        "When enabled, every uploaded GPX filename must match a value in the "
        "CSV GEOREF ID column. The .gpx extension is ignored when matching."
    ),
)

csv_file = None
if attach_csv:
    csv_file = st.file_uploader(
        "Upload attribute CSV",
        type=["csv"],
        accept_multiple_files=False,
        help=(
            "The CSV must contain a GEOREF ID column. Example: "
            "R06-79-02-008-000001.gpx matches GEOREF ID R06-79-02-008-000001."
        ),
    )

mode = st.radio(
    "Choose output mode",
    options=["Consolidated", "Individual"],
    horizontal=True,
    captions=[
        "Create one shapefile containing features from all valid GPX files.",
        "Create a separate shapefile for every valid GPX file.",
    ],
)

parsed_uploads: list[ParsedUpload] = []
errors: list[str] = []
csv_blocking_errors: list[str] = []
csv_warnings: list[str] = []
attribute_lookup: dict[str, dict[str, str]] | None = None

if uploaded_files:
    for upload in uploaded_files:
        try:
            features = parse_gpx(upload.getvalue(), upload.name)
            if features:
                parsed_uploads.append(ParsedUpload(upload.name, features))
            else:
                errors.append(
                    f"{upload.name}: no valid track segments with at least 2 points."
                )
        except GPXParseError as exc:
            errors.append(f"{upload.name}: {exc}")

    st.subheader("File check")

    for parsed in parsed_uploads:
        point_count = sum(feature.point_count for feature in parsed.features)
        st.success(
            f"{parsed.filename} — {len(parsed.features)} feature(s), "
            f"{point_count:,} GPS point(s)"
        )

    for error in errors:
        st.warning(error)

if attach_csv:
    st.subheader("CSV attribute check")

    if not csv_file:
        csv_blocking_errors.append("Upload a CSV file to continue.")
        st.info("Upload a CSV containing the GEOREF ID column.")
    elif uploaded_files:
        try:
            attribute_df = read_attribute_csv(csv_file.getvalue())

            all_uploaded_names = [upload.name for upload in uploaded_files]
            missing, duplicates = validate_gpx_files_in_csv(
                all_uploaded_names,
                attribute_df,
            )

            if missing:
                csv_blocking_errors.append(
                    "One or more GPX files are missing from the CSV GEOREF ID column."
                )
                st.error(
                    "CSV validation failed. Conversion is blocked because every "
                    "uploaded GPX file must exist in GEOREF ID."
                )
                st.code("\n".join(missing), language=None)
            else:
                attribute_lookup = build_attribute_lookup(attribute_df)
                st.success(
                    f"All {len(all_uploaded_names)} uploaded GPX file(s) were found "
                    "in the CSV GEOREF ID column."
                )

            if duplicates:
                csv_warnings.append(
                    "Some GEOREF IDs occur more than once in the CSV."
                )
                st.warning(
                    "Duplicate GEOREF ID matches were found. Conversion can continue, "
                    "but the first matching CSV row will be used for attributes."
                )
                duplicate_lines = [
                    f"{filename}: {count} CSV rows"
                    for filename, count in duplicates.items()
                ]
                st.code("\n".join(duplicate_lines), language=None)

        except CSVValidationError as exc:
            csv_blocking_errors.append(str(exc))
            st.error(str(exc))

convert_disabled = (
    not parsed_uploads
    or bool(csv_blocking_errors)
    or (attach_csv and attribute_lookup is None)
)

if st.button(
    "Convert files",
    type="primary",
    use_container_width=True,
    disabled=convert_disabled,
):
    all_features = [
        feature
        for parsed in parsed_uploads
        for feature in parsed.features
    ]

    with st.spinner("Creating shapefile output..."):
        if mode == "Consolidated":
            gdf = features_to_gdf(
                all_features,
                attribute_lookup=attribute_lookup,
            )
            output = shapefile_to_zip(gdf, "consolidated_gpx")
            filename = "consolidated_gpx.zip"
            label = "Download consolidated shapefile"
            feature_count = len(gdf)
        else:
            converted = [
                (
                    parsed.filename,
                    features_to_gdf(
                        parsed.features,
                        attribute_lookup=attribute_lookup,
                    ),
                )
                for parsed in parsed_uploads
            ]
            output = individual_shapefiles_to_zip(converted)
            filename = "converted_shapefiles.zip"
            label = "Download all shapefiles"
            feature_count = sum(len(gdf) for _, gdf in converted)

    st.success(
        f"Conversion complete: {len(parsed_uploads)} file(s), "
        f"{feature_count} feature(s), CRS {OUTPUT_CRS}."
    )

    if attach_csv:
        st.caption("CSV attributes were attached by matching GPX filename to GEOREF ID.")

    st.download_button(
        label,
        data=output,
        file_name=filename,
        mime="application/zip",
        use_container_width=True,
    )

with st.expander("How CSV matching works"):
    st.markdown(
        """
- CSV attributes are optional.
- The CSV must contain a column named **GEOREF ID**.
- The uploaded GPX filename is matched using its filename without the **.gpx** extension.
- Example: **R06-79-02-008-000001.gpx** matches **R06-79-02-008-000001**.
- If even one uploaded GPX file is missing from the CSV, conversion is blocked.
- Extra CSV rows are allowed.
- If a GEOREF ID appears more than once, the app warns the user and uses the first matching row.
- CSV attributes are added to the shapefile DBF attributes.
"""
    )

with st.expander("What gets converted?"):
    st.markdown(
        """
- GPX track segments are converted to Shapefile LineString features.
- Each feature keeps its source filename, track name, track number, segment number, and point count.
- In Consolidated mode, features from every GPX file are stored together in one shapefile.
- In Individual mode, every GPX file gets its own shapefile folder inside one ZIP.
- Routes, waypoints, polygons, elevation/time attributes, and map preview are planned for later releases.
"""
    )
