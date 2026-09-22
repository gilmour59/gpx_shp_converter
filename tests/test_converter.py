import io
import zipfile

from src.converter import OUTPUT_CRS, features_to_gdf
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
    features = parse_gpx(SAMPLE_GPX, "parcel_a.gpx")

    assert len(features) == 1
    assert features[0].source_file == "parcel_a.gpx"
    assert features[0].track_name == "Parcel A"
    assert features[0].point_count == 3
    assert features[0].geometry.geom_type == "LineString"


def test_converter_uses_wgs84():
    gdf = features_to_gdf(parse_gpx(SAMPLE_GPX, "parcel_a.gpx"))

    assert gdf.crs.to_string() == OUTPUT_CRS
    assert len(gdf) == 1


def test_shapefile_zip_has_required_components():
    gdf = features_to_gdf(parse_gpx(SAMPLE_GPX, "parcel_a.gpx"))
    result = shapefile_to_zip(gdf, "parcel_a")

    with zipfile.ZipFile(io.BytesIO(result), "r") as archive:
        names = set(archive.namelist())

    assert "parcel_a.shp" in names
    assert "parcel_a.shx" in names
    assert "parcel_a.dbf" in names
    assert "parcel_a.prj" in names
