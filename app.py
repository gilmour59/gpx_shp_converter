from __future__ import annotations

from dataclasses import dataclass

import streamlit as st

from src.converter import OUTPUT_CRS, features_to_gdf
from src.csv_attributes import (
    CSVValidationError,
    build_parcel_attribute_lookup,
    read_attribute_csv,
    related_crop_records,
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
    "Attach parcel attributes from CSV",
    help=(
        "Every uploaded GPX filename must match a value in the CSV GEOREF ID "
        "column. Multiple CSV rows for one GEOREF ID are allowed."
    ),
)

csv_file = None
if attach_csv:
    csv_file = st.file_uploader(
        "Upload attribute CSV",
        type=["csv"],
        accept_multiple_files=False,
        help=(
            "The CSV must contain GEOREF ID. Multiple rows for the same GEOREF "
            "may represent rotational or multiple cropping."
        ),
    )

mode = st.radio(
    "Choose output mode",
    options=["Consolidated", "Individual"],
    horizontal=True,
    captions=[
        "Create one shapefile containing one feature per uploaded GPX/GEOREF.",
        "Create a separate shapefile for every uploaded GPX/GEOREF.",
    ],
)

parsed_uploads: list[ParsedUpload] = []
errors: list[str] = []
csv_blocking_errors: list[str] = []
attribute_lookup: dict[str, dict[str, str]] | None = None
attribute_df = None

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
            f"{parsed.filename} — {len(parsed.features)} track segment(s), "
            f"{point_count:,} GPS point(s) → 1 shapefile feature"
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
            missing, multiple_records = validate_gpx_files_in_csv(
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
                attribute_lookup = build_parcel_attribute_lookup(attribute_df)
                st.success(
                    f"All {len(all_uploaded_names)} uploaded GPX file(s) were found "
                    "in the CSV GEOREF ID column."
                )

            if multiple_records:
                st.info(
                    "Some GEOREF IDs have multiple CSV rows. These are treated as "
                    "one parcel geometry with multiple crop/planting records. "
                    "All rows will be preserved in crop_records.csv."
                )
                lines = [
                    f"{filename}: {count} crop/attribute rows"
                    for filename, count in multiple_records.items()
                ]
                st.code("\n".join(lines), language=None)

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
            related = (
                related_crop_records(
                    attribute_df,
                    [parsed.filename for parsed in parsed_uploads],
                )
                if attach_csv and attribute_df is not None
                else None
            )
            output = shapefile_to_zip(
                gdf,
                "consolidated_gpx",
                related_csv=related,
            )
            filename = "consolidated_gpx.zip"
            label = "Download consolidated shapefile"
            feature_count = len(gdf)
        else:
            converted = []
            for parsed in parsed_uploads:
                related = (
                    related_crop_records(attribute_df, [parsed.filename])
                    if attach_csv and attribute_df is not None
                    else None
                )
                converted.append(
                    (
                        parsed.filename,
                        features_to_gdf(
                            parsed.features,
                            attribute_lookup=attribute_lookup,
                        ),
                        related,
                    )
                )

            output = individual_shapefiles_to_zip(converted)
            filename = "converted_shapefiles.zip"
            label = "Download all shapefiles"
            feature_count = sum(len(gdf) for _, gdf, _ in converted)

    st.success(
        f"Conversion complete: {len(parsed_uploads)} GPX file(s), "
        f"{feature_count} shapefile feature(s), CRS {OUTPUT_CRS}."
    )

    if attach_csv:
        st.caption(
            "Parcel-level attributes are stored in the shapefile. "
            "All matched crop/planting rows are preserved in crop_records.csv."
        )

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
- Multiple CSV rows for one GEOREF ID are valid.
- One GPX/GEOREF produces one geometry.
- Parcel/farmer attributes are stored in the shapefile DBF.
- All matching crop, commodity, and planting rows are preserved in **crop_records.csv**.
"""
    )

with st.expander("What gets converted?"):
    st.markdown(
        """
- Each uploaded GPX becomes one shapefile feature.
- If a GPX contains several tracks or segments, they are combined into one multipart line geometry.
- In Consolidated mode, all uploaded GPX/GEOREF features are stored in one shapefile.
- In Individual mode, every GPX gets its own shapefile folder inside one ZIP.
- Routes, waypoints, polygons, elevation/time attributes, and map preview are planned for later releases.
"""
    )
