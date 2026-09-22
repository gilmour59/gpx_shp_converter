from __future__ import annotations

from dataclasses import dataclass

import streamlit as st

from src.converter import OUTPUT_CRS, features_to_gdf
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

if uploaded_files:
    for upload in uploaded_files:
        try:
            features = parse_gpx(upload.getvalue(), upload.name)
            if features:
                parsed_uploads.append(ParsedUpload(upload.name, features))
            else:
                errors.append(f"{upload.name}: no valid track segments with at least 2 points.")
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

convert_disabled = not parsed_uploads

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
            gdf = features_to_gdf(all_features)
            output = shapefile_to_zip(gdf, "consolidated_gpx")
            filename = "consolidated_gpx.zip"
            label = "Download consolidated shapefile"
            feature_count = len(gdf)
        else:
            converted = [
                (parsed.filename, features_to_gdf(parsed.features))
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

    st.download_button(
        label,
        data=output,
        file_name=filename,
        mime="application/zip",
        use_container_width=True,
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
