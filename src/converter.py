from __future__ import annotations

import geopandas as gpd

from .gpx_parser import GPXFeature


OUTPUT_CRS = "EPSG:4326"


def features_to_gdf(features: list[GPXFeature]) -> gpd.GeoDataFrame:
    """Convert parsed GPX features into a GeoDataFrame using WGS 84."""
    if not features:
        raise ValueError("No valid GPX track features were provided.")

    records = [
        {
            "feature_id": index,
            "source": feature.source_file,
            "track_name": feature.track_name,
            "track_no": feature.track_number,
            "segment_no": feature.segment_number,
            "points": feature.point_count,
            "geometry": feature.geometry,
        }
        for index, feature in enumerate(features, start=1)
    ]

    return gpd.GeoDataFrame(records, geometry="geometry", crs=OUTPUT_CRS)
