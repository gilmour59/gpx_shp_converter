from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import gpxpy
from shapely.geometry import LineString


@dataclass(slots=True)
class GPXFeature:
    source_file: str
    track_name: str
    track_number: int
    segment_number: int
    point_count: int
    geometry: LineString


class GPXParseError(ValueError):
    """Raised when a GPX file cannot be converted into track features."""


def parse_gpx(file_content: bytes, filename: str) -> list[GPXFeature]:
    """Parse GPX track segments into LineString features in WGS 84 coordinates."""
    try:
        text_content = file_content.decode("utf-8-sig")
    except UnicodeDecodeError:
        text_content = file_content.decode("utf-8", errors="replace")

    try:
        gpx = gpxpy.parse(text_content)
    except Exception as exc:
        raise GPXParseError(f"Invalid GPX file: {exc}") from exc

    features: list[GPXFeature] = []

    for track_index, track in enumerate(gpx.tracks, start=1):
        track_name = (track.name or f"Track {track_index}").strip()

        for segment_index, segment in enumerate(track.segments, start=1):
            coordinates: list[tuple[float, float]] = []

            for point in segment.points:
                if not (-90 <= point.latitude <= 90):
                    continue
                if not (-180 <= point.longitude <= 180):
                    continue

                coordinates.append((point.longitude, point.latitude))

            if len(coordinates) < 2:
                continue

            features.append(
                GPXFeature(
                    source_file=Path(filename).name,
                    track_name=track_name,
                    track_number=track_index,
                    segment_number=segment_index,
                    point_count=len(coordinates),
                    geometry=LineString(coordinates),
                )
            )

    return features
