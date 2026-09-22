from __future__ import annotations

from collections import defaultdict

import geopandas as gpd
from shapely.ops import unary_union

from .csv_attributes import attributes_for_feature
from .gpx_parser import GPXFeature


OUTPUT_CRS = "EPSG:4326"


def features_to_gdf(
    features: list[GPXFeature],
    attribute_lookup: dict[str, dict[str, str]] | None = None,
) -> gpd.GeoDataFrame:
    """
    Convert parsed GPX features into one shapefile feature per source GPX file.

    Multiple tracks or track segments inside one GPX are combined into one
    LineString/MultiLineString geometry.
    """
    if not features:
        raise ValueError("No valid GPX track features were provided.")

    grouped: dict[str, list[GPXFeature]] = defaultdict(list)
    for feature in features:
        grouped[feature.source_file].append(feature)

    records = []

    for index, (source_file, group) in enumerate(grouped.items(), start=1):
        geometry = unary_union([feature.geometry for feature in group])

        record = {
            "feature_id": index,
            "source": source_file,
            "tracks": len({feature.track_number for feature in group}),
            "segments": len(group),
            "points": sum(feature.point_count for feature in group),
            "geometry": geometry,
        }

        if attribute_lookup is not None:
            record.update(attributes_for_feature(group[0], attribute_lookup))

        records.append(record)

    return gpd.GeoDataFrame(records, geometry="geometry", crs=OUTPUT_CRS)
