# Author: Carson Morris
# Silmaril - Created: September 28, 2026
# Representation of a satellite's orbital data

from datetime import datetime
from pydantic import BaseModel, Field

# Take the JSON data returned from CelesTrak and parse it into a structured format

#Orbital Data - Describing orbit
class OrbitalElements(BaseModel):
    epoch: datetime = Field(alias="EPOCH") # Time at which these orbital elements are referenced
    mean_motion: float = Field(alias="MEAN_MOTION")
    mean_motion_dot: float = Field(alias="MEAN_MOTION_DOT")
    mean_motion_ddot: float = Field(alias="MEAN_MOTION_DDOT")
    eccentricity: float = Field(alias="ECCENTRICITY")
    inclination: float = Field(alias="INCLINATION")
    ra_of_asc_node: float = Field(alias="RA_OF_ASC_NODE")
    arg_of_pericenter: float = Field(alias="ARG_OF_PERICENTER")
    mean_anomaly: float = Field(alias="MEAN_ANOMALY") # Where the satellite is in its orbit at the epoch
    bstar: float = Field(alias="BSTAR")
    rev_at_epoch: int = Field(alias="REV_AT_EPOCH")

#Orbital Metadata - Describing the satellite itself
class OrbitalMetadata(BaseModel):
    object_name: str = Field(alias="OBJECT_NAME") # Name of the satellite
    object_id: str = Field(alias="OBJECT_ID")
    norad_cat_id: int = Field(alias="NORAD_CAT_ID") # NORAD catalog number
    ephemeris_type: int = Field(alias="EPHEMERIS_TYPE")
    classification_type: str = Field(alias="CLASSIFICATION_TYPE")
    element_set_no: int = Field(alias="ELEMENT_SET_NO")
    