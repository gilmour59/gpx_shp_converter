import io
import zipfile

from src.converter import OUTPUT_CRS, features_to_gdf
from src.csv_attributes import (
    build_parcel_attribute_lookup,
    read_attribute_csv,
    related_crop_records,
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
    <trkseg>
      <trkpt lat="10.7020" lon="122.5620" />
      <trkpt lat="10.7025" lon="122.5625" />
    </trkseg>
  </trk>
</gpx>
"""


def test_converter_creates_one_feature_per_gpx():
    features = parse_gpx(SAMPLE_GPX, "R06-79-02-008-000001.gpx")
    gdf = features_to_gdf(features)

    assert len(features) == 2
    assert len(gdf) == 1
    assert gdf.loc[0, "segments"] == 2
    assert gdf.crs.to_string() == OUTPUT_CRS


def test_csv_validation_requires_every_gpx():
    csv_bytes = (
        b"GEOREF ID,RSBSA ID,COMMODITY\n"
        b"R06-79-02-008-000001,06-79-02-008-000111,Rice/Palay\n"
    )
    df = read_attribute_csv(csv_bytes)

    missing, multiple_records = validate_gpx_files_in_csv(
        [
            "R06-79-02-008-000001.gpx",
            "R06-79-02-008-000002.gpx",
        ],
        df,
    )

    assert missing == ["R06-79-02-008-000002.gpx"]
    assert multiple_records == {}


def test_duplicate_georef_crop_rows_are_valid():
    csv_bytes = (
        b"GEOREF ID,RSBSA ID,RSBSA PARCEL ID,COMMODITY,PLANTING SCHEDULE - FROM\n"
        b"R06-79-02-008-000001,RSBSA-1,PARCEL-1,Rice/Palay,June\n"
        b"R06-79-02-008-000001,RSBSA-1,PARCEL-1,Corn,January\n"
    )
    df = read_attribute_csv(csv_bytes)

    missing, multiple_records = validate_gpx_files_in_csv(
        ["R06-79-02-008-000001.gpx"],
        df,
    )

    assert missing == []
    assert multiple_records == {"R06-79-02-008-000001.gpx": 2}


def test_shapefile_uses_parcel_attributes_and_related_table_keeps_crops():
    csv_bytes = (
        b"GEOREF ID,RSBSA ID,RSBSA PARCEL ID,COMMODITY,PLANTING SCHEDULE - FROM\n"
        b"R06-79-02-008-000001,RSBSA-1,PARCEL-1,Rice/Palay,June\n"
        b"R06-79-02-008-000001,RSBSA-1,PARCEL-1,Corn,January\n"
    )
    df = read_attribute_csv(csv_bytes)
    lookup = build_parcel_attribute_lookup(df)
    features = parse_gpx(SAMPLE_GPX, "R06-79-02-008-000001.gpx")

    gdf = features_to_gdf(features, attribute_lookup=lookup)
    related = related_crop_records(df, ["R06-79-02-008-000001.gpx"])

    assert len(gdf) == 1
    assert gdf.loc[0, "GEOREF_ID"] == "R06-79-02-008-000001"
    assert gdf.loc[0, "RSBSA_ID"] == "RSBSA-1"
    assert gdf.loc[0, "PARCEL_ID"] == "PARCEL-1"
    assert gdf.loc[0, "CROP_ROWS"] == "2"
    assert "COMMODITY" not in gdf.columns
    assert len(related) == 2
    assert set(related["COMMODITY"]) == {"Rice/Palay", "Corn"}


def test_output_zip_contains_related_crop_records():
    csv_bytes = (
        b"GEOREF ID,RSBSA ID,COMMODITY\n"
        b"R06-79-02-008-000001,RSBSA-1,Rice/Palay\n"
        b"R06-79-02-008-000001,RSBSA-1,Corn\n"
    )
    df = read_attribute_csv(csv_bytes)
    gdf = features_to_gdf(
        parse_gpx(SAMPLE_GPX, "R06-79-02-008-000001.gpx"),
        attribute_lookup=build_parcel_attribute_lookup(df),
    )
    related = related_crop_records(df, ["R06-79-02-008-000001.gpx"])

    result = shapefile_to_zip(
        gdf,
        "parcel_a",
        related_csv=related,
    )

    with zipfile.ZipFile(io.BytesIO(result), "r") as archive:
        names = set(archive.namelist())
        crop_csv = archive.read("crop_records.csv").decode("utf-8")

    assert "parcel_a.shp" in names
    assert "parcel_a.shx" in names
    assert "parcel_a.dbf" in names
    assert "parcel_a.prj" in names
    assert "crop_records.csv" in names
    assert "Rice/Palay" in crop_csv
    assert "Corn" in crop_csv
