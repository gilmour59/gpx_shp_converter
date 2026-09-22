from __future__ import annotations

import io
import re
import tempfile
import zipfile
from pathlib import Path

import geopandas as gpd
import pandas as pd


def safe_filename(value: str, fallback: str = "converted") -> str:
    value = Path(value).stem.strip()
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", value)
    value = value.strip("._-")
    return value or fallback


def _write_shapefile_components(
    gdf: gpd.GeoDataFrame,
    output_dir: Path,
    shapefile_name: str,
) -> list[Path]:
    name = safe_filename(shapefile_name)
    shp_path = output_dir / f"{name}.shp"

    gdf.to_file(
        shp_path,
        driver="ESRI Shapefile",
        engine="pyogrio",
        index=False,
    )

    return sorted(output_dir.glob(f"{name}.*"))


def shapefile_to_zip(
    gdf: gpd.GeoDataFrame,
    shapefile_name: str,
    related_csv: pd.DataFrame | None = None,
    related_csv_name: str = "crop_records.csv",
) -> bytes:
    """Write a shapefile and optionally include related crop records."""
    with tempfile.TemporaryDirectory() as temp_dir:
        output_dir = Path(temp_dir)
        components = _write_shapefile_components(
            gdf,
            output_dir,
            shapefile_name,
        )

        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
            for component in components:
                archive.write(component, arcname=component.name)

            if related_csv is not None:
                archive.writestr(
                    related_csv_name,
                    related_csv.to_csv(index=False),
                )

        buffer.seek(0)
        return buffer.getvalue()


def individual_shapefiles_to_zip(
    converted_files: list[tuple[str, gpd.GeoDataFrame, pd.DataFrame | None]],
) -> bytes:
    """
    Create one outer ZIP containing one folder per GPX file.

    Each folder may include crop_records.csv containing all matched crop rows.
    """
    buffer = io.BytesIO()

    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as outer_zip:
        for source_name, gdf, related_csv in converted_files:
            name = safe_filename(source_name)

            with tempfile.TemporaryDirectory() as temp_dir:
                output_dir = Path(temp_dir)
                components = _write_shapefile_components(gdf, output_dir, name)

                for component in components:
                    outer_zip.write(
                        component,
                        arcname=f"{name}/{component.name}",
                    )

                if related_csv is not None:
                    outer_zip.writestr(
                        f"{name}/crop_records.csv",
                        related_csv.to_csv(index=False),
                    )

    buffer.seek(0)
    return buffer.getvalue()
