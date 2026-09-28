# Silmaril

**Silmaril** is a satellite tracking and orbital visualization project focused on calculating and displaying the positions of objects in Earth orbit.

The project is being built from the ground up to explore orbital mechanics, satellite data, backend development, and interactive 3D visualization.

> *A small Tolkien reference to light, observation, and the heavens.*

## Status

🚧 **Early Development**

Currently working on retrieving real satellite orbital data from **CelesTrak**, parsing **OMM JSON**, and using **SGP4** to calculate satellite positions.

## Helpful Links and Info
CelesTrak "A New Way to Obtain GP Data (aka TLEs)" documentation: https://celestrak.org/NORAD/documentation/gp-data-formats.php

All GP queries on CelesTrak will take the form:

https://celestrak.org/NORAD/elements/gp.php?{QUERY}=VALUE[&FORMAT=VALUE]
where {QUERY} is:

- CATNR: Catalog Number (1 to 9 digits). Allows return of data for a single catalog number.
- INTDES: International Designator (yyyy-nnn). Allows return of data for all objects associated with a particular launch.
- GROUP: Groups of satellites provided on the CelesTrak Current Data page.
- NAME: Satellite Name. Allows searching for satellites by parts of their name.
- SPECIAL: Special data sets for:
The GEO Protected Zone (SPECIAL=GPZ),
GPZ Plus (SPECIAL=GPZ-PLUS),
Potential Decays (SPECIAL=DECAYING).

{QUERY} must be uppercase.

ISS: https://celestrak.org/NORAD/elements/gp.php?CATNR=25544&FORMAT=JSON

OMM stands for Orbit Mean-Elements Message
Epoch: Data/Time where Data is considered accurate
Inclination: How tilted the orbit is relative to Earth, where 0 degrees is inline with the equator
Eccentricity: How stretched the orbit is. Low eccentricity means nearly circular. High means more elongated
Mean Motion: How quickly the satellite goes around Earth, expressed as revolutions per day.


                    RAAN
                     ↓
              Which direction
              is the orbit facing?

                     /
                    /
                   /   ← orbital plane
                  /
                 /

Inclination → How tilted?

Eccentricity → How stretched?

Argument of Perigee → Where is
                       the closest
                       point?

Mean Anomaly → Where is the
               satellite right now
               within the orbit?

Mean Motion → How quickly is it
              going around?

Epoch → When are these values
        considered accurate?

BSTAR → How is atmospheric drag
        affecting the model?
        
## Goals

* Retrieve and process satellite orbital data
* Calculate satellite positions and velocities
* Convert orbital coordinates to latitude, longitude, and altitude
* Store satellite data in a database
* Provide a REST API
* Build an interactive satellite map
* Visualize satellites and orbits on a 3D Earth
* Calculate satellite passes and visibility

## Technology

**Backend:** Python, FastAPI, SGP4, SQLite, Pydantic

**Frontend:** React, TypeScript, Three.js

**Development:** Git, Docker, Pytest, GitHub Actions

## Data

Initial orbital data will come from **CelesTrak**, using OMM JSON as the primary format.

## Project Structure

```text
silmaril/
├── backend/
├── frontend/
├── tests/
├── scripts/
├── docs/
├── requirements.txt
└── README.md
```

The project will be developed incrementally, starting with satellite data and orbital calculations before expanding into the web application and 3D visualization.
