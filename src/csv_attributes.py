from __future__ import annotations

import io
from pathlib import Path

import pandas as pd

from .gpx_parser import GPXFeature


GEOREF_COLUMN = "GEOREF ID"

PARCEL_FIELD_ALIASES = {
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
    text = str(value).strip()
    if not text or text.lower() == "nan":
        return ""
    if text.lower().endswith(".gpx"):
        text = text[:-4]
    return text.strip().casefold()


def gpx_georef_id(filename: str) -> str:
    return Path(filename).stem.strip()


def read_attribute_csv(csv_bytes: bytes) -> pd.DataFrame:
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

    Duplicate GEOREF IDs are valid and may represent rotational or multiple
    crop records for the same physical parcel.
    """
    counts = df["_GEOREF_KEY"].value_counts()
    missing: list[str] = []
    multiple_records: dict[str, int] = {}

    for filename in filenames:
        key = _normalize_georef(gpx_georef_id(filename))
        match_count = int(counts.get(key, 0))

        if match_count == 0:
            missing.append(filename)
        elif match_count > 1:
            multiple_records[filename] = match_count

    return missing, multiple_records


def _first_nonempty(values: pd.Series) -> str:
    for value in values.astype(str):
        value = value.strip()
        if value:
            return value
    return ""


def build_parcel_attribute_lookup(
    df: pd.DataFrame,
) -> dict[str, dict[str, str]]:
    """
    Build one parcel-level attribute row per GEOREF ID.

    Multiple crop rows for the same GEOREF ID do not duplicate geometry.
    """
    lookup: dict[str, dict[str, str]] = {}

    for key, group in df.groupby("_GEOREF_KEY", sort=False):
        if not key:
            continue

        attributes: dict[str, str] = {}
        for csv_column, shp_column in PARCEL_FIELD_ALIASES.items():
            if csv_column in group.columns:
                attributes[shp_column] = _first_nonempty(group[csv_column])

        commodities = [
            value.strip()
            for value in group.get("COMMODITY", pd.Series(dtype=str)).astype(str)
            if value.strip()
        ]
        plant_from = [
            value.strip()
            for value in group.get(
                "PLANTING SCHEDULE - FROM",
                pd.Series(dtype=str),
            ).astype(str)
            if value.strip()
        ]
        plant_to = [
            value.strip()
            for value in group.get(
                "PLANTING SCHEDULE - TO",
                pd.Series(dtype=str),
            ).astype(str)
            if value.strip()
        ]

        # Keep crop summaries directly visible in the shapefile while the
        # related CSV preserves the exact one-to-many crop rows.
        attributes["COMMODITY"] = "; ".join(dict.fromkeys(commodities))
        attributes["PLANT_FROM"] = "; ".join(dict.fromkeys(plant_from))
        attributes["PLANT_TO"] = "; ".join(dict.fromkeys(plant_to))
        attributes["CROP_ROWS"] = str(len(group))
        lookup[key] = attributes

    return lookup


def related_crop_records(
    df: pd.DataFrame,
    filenames: list[str],
) -> pd.DataFrame:
    """
    Return every original CSV row related to the uploaded GPX files.

    This preserves one-to-many commodity/planting records for each GEOREF ID.
    """
    wanted_keys = {
        _normalize_georef(gpx_georef_id(filename))
        for filename in filenames
    }
    related = df[df["_GEOREF_KEY"].isin(wanted_keys)].copy()
    return related.drop(columns=["_GEOREF_KEY"], errors="ignore")


def attributes_for_feature(
    feature: GPXFeature,
    lookup: dict[str, dict[str, str]],
) -> dict[str, str]:
    key = _normalize_georef(gpx_georef_id(feature.source_file))
    return lookup.get(key, {})
