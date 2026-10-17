# Author: Carson Morris
# Silmaril - Created at: September 28, 2026
# Description: Define data models for satellite orbital elements and metadata.
"""Parse CelesTrak OMM JSON into structured orbital and metadata models."""

from datetime import datetime
from pydantic import BaseModel, Field

class OrbitalElements(BaseModel):
    """Validated orbital-element fields returned by CelesTrak's GP endpoint."""

    epoch: datetime = Field(
        alias="EPOCH",
        title="Epoch",
        description="Date and time at which the orbital data is considered accurate.",
    )
    mean_motion: float = Field(
        alias="MEAN_MOTION",
        title="Mean motion",
        description="How quickly the satellite orbits, expressed in revolutions per day.",
    )
    mean_motion_dot: float = Field(
        alias="MEAN_MOTION_DOT",
        title="Mean motion derivative",
        description="How mean motion changes over time, in revolutions per day squared.",
    )
    mean_motion_ddot: float = Field(
        alias="MEAN_MOTION_DDOT",
        title="Mean motion second derivative",
        description="How the mean motion derivative changes, in revolutions per day cubed.",
    )
    eccentricity: float = Field(
        alias="ECCENTRICITY",
        title="Eccentricity",
        description="How stretched the orbit is; low eccentricity means nearly circular.",
    )
    inclination: float = Field(
        alias="INCLINATION",
        title="Inclination",
        description="How tilted the orbit is relative to Earth; zero degrees is in line with the equator.",
    )
    ra_of_asc_node: float = Field(
        alias="RA_OF_ASC_NODE",
        title="RAAN",
        description="Right Ascension of the Ascending Node; the orientation of the orbital plane around Earth.",
    )
    arg_of_pericenter: float = Field(
        alias="ARG_OF_PERICENTER",
        title="Argument of perigee",
        description="The orientation of the orbit's closest point to Earth.",
    )
    mean_anomaly: float = Field(
        alias="MEAN_ANOMALY",
        title="Mean anomaly",
        description="A steadily increasing mathematical angle used to track position along an elliptical orbit.",
    )
    bstar: float = Field(
        alias="BSTAR",
        title="BSTAR",
        description="A parameter used to model atmospheric drag.",
    )
    rev_at_epoch: int = Field(
        alias="REV_AT_EPOCH",
        title="Revolutions at epoch",
        description="The satellite's orbit revolution count at the epoch.",
    )

class OrbitalMetadata(BaseModel):
    """Validated identity and catalog metadata returned with a GP record."""

    object_name: str = Field(
        alias="OBJECT_NAME",
        title="Object name",
        description="Satellite name from the source catalog.",
    )
    object_id: str = Field(
        alias="OBJECT_ID",
        title="International designator",
        description="Identifier assigned to the satellite's launch.",
    )
    norad_cat_id: int = Field(
        alias="NORAD_CAT_ID",
        title="NORAD catalog number",
        description="Unique catalog number assigned to the object.",
    )
    ephemeris_type: int = Field(
        alias="EPHEMERIS_TYPE",
        title="Ephemeris type",
        description="Orbit data representation type.",
    )
    classification_type: str = Field(
        alias="CLASSIFICATION_TYPE",
        title="Classification",
        description="Catalog classification code for the object.",
    )
    element_set_no: int = Field(
        alias="ELEMENT_SET_NO",
        title="Element set number",
        description="Sequence number for this orbital element set.",
    )
    