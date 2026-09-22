from __future__ import annotations

import io
import re
import tempfile
import zipfile
from pathlib import Path

import geopandas as gpd


def safe_filename(value: str, fallback: str = "converted") -> str:
    """Return a filesystem-safe basename suitable for shapefile output."""
    value = Path(value).stem.strip()
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", value)
    value = value.strip("._-")
    return value or fallback


def shapefile_to_zip(gdf: gpd.GeoDataFrame, shapefile_name: str) -> bytes:
    """Write a GeoDataFrame as an ESRI Shapefile and return all parts as ZIP bytes."""
    name = safe_filename(shapefile_name)

    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir)
        shp_path = output_dir / f"{name}.shp"

        gdf.to_file(
            shp_path,
            driver="ESRI Shapefile",
            engine="pyogrio",
            index=False,
        )

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
            for component in sorted(output_dir.glob(f"{name}.*")):
                archive.write(component, arcname=component.name)

        buffer.seek(0)
        return buffer.getvalue()


def individual_shapefiles_to_zip(
    converted_files: list[tuple[str, gpd.GeoDataFrame]],
) -> bytes:
    """Create one outer ZIP containing one folder per converted GPX file."""
    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as outer_zip:
        for source_name, gdf in converted_files:
            name = safe_filename(source_name)
            inner_zip_bytes = shapefile_to_zip(gdf, name)

            with zipfile.ZipFile(io.BytesIO(inner_zip_bytes), "r") as inner_zip:
                for member in inner_zip.infolist():
                    outer_zip.writestr(
                        f"{name}/{Path(member.filename).name}",
                        inner_zip.read(member.filename),
                    )

    buffer.seek(0)
    return buffer.getvalue()
