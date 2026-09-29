# Author: Carson Morris
# Silmaril - Created: September 28, 2026
# Representation of a satellite's orbital data

from datetime import datetime
from pydantic import BaseModel, Field

# Take the JSON data returned from CelesTrak and parse it into a structured format
class OrbitalElements(BaseModel):
    object_name: str = Field(alias="OBJECT_NAME") # Name of the satellite
    norad_cat_id: int = Field(alias="NORAD_CAT_ID") # NORAD catalog number
    epoch: datetime = Field(alias="EPOCH") # Will tell us where the satellite is in its orbit
    mean_motion: float = Field(alias="MEAN_MOTION") 
    eccentricity: float = Field(alias="ECCENTRICITY")
    inclination: float = Field(alias="INCLINATION")
    ra_of_asc_node: float = Field(alias="RA_OF_ASC_NODE")
    arg_of_pericenter: float = Field(alias="ARG_OF_PERICENTER")
    mean_anomaly: float = Field(alias="MEAN_ANOMALY")
    bstar: float = Field(alias="BSTAR")