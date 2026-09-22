from __future__ import annotations

import io
from pathlib import Path

import pandas as pd

from .gpx_parser import GPXFeature


GEOREF_COLUMN = "GEOREF ID"

# ESRI Shapefile DBF field names are limited. These aliases keep the
# important CSV attributes readable and unique in the exported shapefile.
FIELD_ALIASES = {
    "GEOREF ID": "GEOREF_ID",
    "RSBSA ID": "RSBSA_ID",
    "FIRST NAME": "FIRST_NAME",
    "MIDDLE NAME": "MID_NAME",
    "LASTNAME": "LASTNAME",
    "EXTENSION NAME": "EXT_NAME",
    "DATE OF BIRTH": "DOB",
    "RESIDENCE": "RESIDENCE",
    "FCA": "FCA",
    "RSBSA PARCEL ID": "PARCEL_ID",
    "PARCEL NAME": "PRCL_NAME",
    "FARM TYPE": "FARM_TYPE",
    "COMMODITY": "COMMODITY",
    "PLANTING SCHEDULE - FROM": "PLANT_FROM",
    "PLANTING SCHEDULE - TO": "PLANT_TO",
    "DECLARED AREA (Ha)": "DECL_AREA",
    "VERIFIED AREA (Ha)": "VERIF_AREA",
    "TYPE OF OWNERSHIP": "OWN_TYPE",
    "LAND OWNER": "LAND_OWNER",
    "ARB": "ARB",
    "ANCESTRAL DOMAIN": "ANCEST_DOM",
    "REGION": "REGION",
    "PROVINCE": "PROVINCE",
    "MUNICIPALITY": "MUNICIPAL",
    "BARANGAY": "BARANGAY",
    "TRACK DATE": "TRACK_DATE",
    "DATE/TIME UPLOADED": "UPLOADED",
    "UPLOADER": "UPLOADER",
}


class CSVValidationError(ValueError):
    """Raised when the attribute CSV is unusable for GPX matching."""


def _normalize_georef(value: object) -> str:
    """Normalize GEOREF values and GPX filenames to comparable IDs."""
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return ""
    if text.lower().endswith(".gpx"):
        text = text[:-4]
    return text.strip().casefold()


def gpx_georef_id(filename: str) -> str:
    """Return the GPX filename basename used to match GEOREF ID."""
    return Path(filename).stem.strip()


def read_attribute_csv(csv_bytes: bytes) -> pd.DataFrame:
    """Read a CSV while preserving identifiers as strings."""
    try:
        df = pd.read_csv(io.BytesIO(csv_bytes), dtype=str, keep_default_na=False)
    except Exception as exc:
        raise CSVValidationError(f"Could not read CSV: {exc}") from exc

    df.columns = [str(column).strip() for column in df.columns]

    if GEOREF_COLUMN not in df.columns:
        raise CSVValidationError(
            f'CSV is missing the required "{GEOREF_COLUMN}" column.'
        )

    df["_GEOREF_KEY"] = df[GEOREF_COLUMN].map(_normalize_georef)

    if not df["_GEOREF_KEY"].any():
        raise CSVValidationError(
            f'The "{GEOREF_COLUMN}" column does not contain usable values.'
        )

    return df


def validate_gpx_files_in_csv(
    filenames: list[str],
    df: pd.DataFrame,
) -> tuple[list[str], dict[str, int]]:
    """
    Validate that every GPX filename exists in GEOREF ID.

    Returns:
        missing filenames,
        duplicate match counts keyed by original GPX filename.
    """
    counts = df["_GEOREF_KEY"].value_counts()
    missing: list[str] = []
    duplicates: dict[str, int] = {}

    for filename in filenames:
        key = _normalize_georef(gpx_georef_id(filename))
        match_count = int(counts.get(key, 0))

        if match_count == 0:
            missing.append(filename)
        elif match_count > 1:
            duplicates[filename] = match_count

    return missing, duplicates


def build_attribute_lookup(df: pd.DataFrame) -> dict[str, dict[str, str]]:
    """
    Build one attribute row per GEOREF ID.

    Duplicate GEOREF IDs use the first CSV row to avoid multiplying geometry.
    The UI reports duplicate matches to the user before conversion.
    """
    lookup: dict[str, dict[str, str]] = {}

    for _, row in df.iterrows():
        key = row["_GEOREF_KEY"]
        if not key or key in lookup:
            continue

        attributes: dict[str, str] = {}

        for csv_column, shp_column in FIELD_ALIASES.items():
            if csv_column in df.columns:
                attributes[shp_column] = str(row[csv_column]).strip()

        # Preserve additional, previously unknown columns with safe aliases.
        used_names = set(attributes)
        for column in df.columns:
            if column == "_GEOREF_KEY" or column in FIELD_ALIASES:
                continue

            base = "".join(ch if ch.isalnum() else "_" for ch in column.upper())
            base = base.strip("_") or "FIELD"
            base = base[:10]

            candidate = base
            suffix = 1
            while candidate in used_names:
                suffix_text = str(suffix)
                candidate = f"{base[:10-len(suffix_text)]}{suffix_text}"
                suffix += 1

            used_names.add(candidate)
            attributes[candidate] = str(row[column]).strip()

        lookup[key] = attributes

    return lookup


def attributes_for_feature(
    feature: GPXFeature,
    lookup: dict[str, dict[str, str]],
) -> dict[str, str]:
    """Return CSV attributes for a GPX feature based on source filename."""
    key = _normalize_georef(gpx_georef_id(feature.source_file))
    return lookup.get(key, {})
