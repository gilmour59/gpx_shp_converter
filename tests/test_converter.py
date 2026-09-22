import io
import zipfile

import pandas as pd

from src.converter import OUTPUT_CRS, features_to_gdf
from src.csv_attributes import (
    build_attribute_lookup,
    read_attribute_csv,
    validate_gpx_files_in_csv,
)
from src.exporter import shapefile_to_zip
from src.gpx_parser import parse_gpx


SAMPLE_GPX = b"""<?xml version="1.0" encoding="UTF-8"?>
<gpx version="1.1" creator="test" xmlns="http://www.topografix.com/GPX/1/1">
  <trk>
    <name>Parcel A</name>
    <trkseg>
      <trkpt lat="10.7000" lon="122.5600" />
      <trkpt lat="10.7005" lon="122.5605" />
      <trkpt lat="10.7010" lon="122.5610" />
    </trkseg>
  </trk>
</gpx>
"""


def test_parser_creates_linestring():
    features = parse_gpx(SAMPLE_GPX, "R06-79-02-008-000001.gpx")

    assert len(features) == 1
    assert features[0].source_file == "R06-79-02-008-000001.gpx"
    assert features[0].track_name == "Parcel A"
    assert features[0].point_count == 3
    assert features[0].geometry.geom_type == "LineString"


def test_converter_uses_wgs84():
    gdf = features_to_gdf(
        parse_gpx(SAMPLE_GPX, "R06-79-02-008-000001.gpx")
    )

    assert gdf.crs.to_string() == OUTPUT_CRS
    assert len(gdf) == 1


def test_csv_validation_requires_every_gpx():
    csv_bytes = (
        b"GEOREF ID,RSBSA ID,COMMODITY\n"
        b"R06-79-02-008-000001,06-79-02-008-000111,Rice/Palay\n"
    )
    df = read_attribute_csv(csv_bytes)

    missing, duplicates = validate_gpx_files_in_csv(
        [
            "R06-79-02-008-000001.gpx",
            "R06-79-02-008-000002.gpx",
        ],
        df,
    )

    assert missing == ["R06-79-02-008-000002.gpx"]
    assert duplicates == {}


def test_csv_attributes_are_added_to_gdf():
    csv_bytes = (
        b"GEOREF ID,RSBSA ID,COMMODITY\n"
        b"R06-79-02-008-000001,06-79-02-008-000111,Rice/Palay\n"
    )
    df = read_attribute_csv(csv_bytes)
    lookup = build_attribute_lookup(df)
    features = parse_gpx(SAMPLE_GPX, "R06-79-02-008-000001.gpx")

    gdf = features_to_gdf(features, attribute_lookup=lookup)

    assert gdf.loc[0, "GEOREF_ID"] == "R06-79-02-008-000001"
    assert gdf.loc[0, "RSBSA_ID"] == "06-79-02-008-000111"
    assert gdf.loc[0, "COMMODITY"] == "Rice/Palay"


def test_shapefile_zip_has_required_components():
    gdf = features_to_gdf(
        parse_gpx(SAMPLE_GPX, "R06-79-02-008-000001.gpx")
    )
    result = shapefile_to_zip(gdf, "parcel_a")

    with zipfile.ZipFile(io.BytesIO(result), "r") as archive:
        names = set(archive.namelist())

    assert "parcel_a.shp" in names
    assert "parcel_a.shx" in names
    assert "parcel_a.dbf" in names
    assert "parcel_a.prj" in names
