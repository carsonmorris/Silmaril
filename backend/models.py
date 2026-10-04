# Author: Carson Morris
# Silmaril - Created: September 28, 2026
# Representation of a satellite's orbital data

from datetime import datetime
from pydantic import BaseModel, Field

# Take the JSON data returned from CelesTrak and parse it into a structured format

#Orbital Data - Describing orbit
class OrbitalElements(BaseModel):
    epoch: datetime = Field(
        alias="EPOCH",
        title="Epoch",
        description="Reference date and time for these orbital elements.",
    )
    mean_motion: float = Field(
        alias="MEAN_MOTION",
        title="Mean motion",
        description="Average orbital revolutions per day.",
    )
    mean_motion_dot: float = Field(
        alias="MEAN_MOTION_DOT",
        title="Mean motion derivative",
        description="First derivative of mean motion, in revolutions per day squared.",
    )
    mean_motion_ddot: float = Field(
        alias="MEAN_MOTION_DDOT",
        title="Mean motion second derivative",
        description="Second derivative of mean motion, in revolutions per day cubed.",
    )
    eccentricity: float = Field(
        alias="ECCENTRICITY",
        title="Eccentricity",
        description="Unitless measure of how elliptical the orbit is.",
    )
    inclination: float = Field(
        alias="INCLINATION",
        title="Inclination",
        description="Orbital plane tilt relative to the equator, in degrees.",
    )
    ra_of_asc_node: float = Field(
        alias="RA_OF_ASC_NODE",
        title="Ascending node (RAAN)",
        description="Direction of the orbital plane, in degrees.",
    )
    arg_of_pericenter: float = Field(
        alias="ARG_OF_PERICENTER",
        title="Argument of pericenter",
        description="Orientation of the orbit's closest point, in degrees.",
    )
    mean_anomaly: float = Field(
        alias="MEAN_ANOMALY",
        title="Mean anomaly",
        description="Satellite position along its orbit at the epoch, in degrees.",
    )
    bstar: float = Field(
        alias="BSTAR",
        title="B* drag term",
        description="Atmospheric drag term used by the SGP4 model.",
    )
    rev_at_epoch: int = Field(
        alias="REV_AT_EPOCH",
        title="Revolutions at epoch",
        description="Orbit revolution count at the reference epoch.",
    )

#Orbital Metadata - Describing the satellite itself
class OrbitalMetadata(BaseModel):
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
    