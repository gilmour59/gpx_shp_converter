from __future__ import annotations

import geopandas as gpd

from .csv_attributes import attributes_for_feature
from .gpx_parser import GPXFeature


OUTPUT_CRS = "EPSG:4326"


def features_to_gdf(
    features: list[GPXFeature],
    attribute_lookup: dict[str, dict[str, str]] | None = None,
) -> gpd.GeoDataFrame:
    """Convert parsed GPX features into a GeoDataFrame using WGS 84."""
    if not features:
        raise ValueError("No valid GPX track features were provided.")

    records = []

    for index, feature in enumerate(features, start=1):
        record = {
            "feature_id": index,
            "source": feature.source_file,
            "track_name": feature.track_name,
            "track_no": feature.track_number,
            "segment_no": feature.segment_number,
            "points": feature.point_count,
            "geometry": feature.geometry,
        }

        if attribute_lookup is not None:
            record.update(attributes_for_feature(feature, attribute_lookup))

        records.append(record)

    return gpd.GeoDataFrame(records, geometry="geometry", crs=OUTPUT_CRS)
