# Silmaril

**Silmaril** is a satellite tracking and orbital visualization project focused on calculating and displaying the positions of objects in Earth orbit.

The project is being built from the ground up to explore orbital mechanics, satellite data, backend development, and interactive 3D visualization.

> *A small Tolkien reference to light, observation, and the heavens.*

## Status

🚧 **Early Development**

Retrieving real satellite orbital data from **CelesTrak**, parsing **OMM JSON**, and using **SGP4** to calculate satellite positions. 

## Goals

* Retrieve and process satellite orbital data ✓
* Calculate satellite positions and velocities ✓
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
├── data/
├── tests/
├── scripts/
├── docs/
├── requirements.txt
└── README.md
```

The project will be developed incrementally, starting with satellite data and orbital calculations before expanding into the web application and 3D visualization.

## Helpful Links and Info
CelesTrak: https://celestrak.org

Shout out to T.S. Kelso and his amazing work here!

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

RAAN : Right Ascension of the Ascending Node. It tells us which direction the satellite's orbital plane is pointing around Earth.

Mean Anomaly: a mathematical angle that increases at a steady, uniform rate over time to track an object's position along an elliptical orbit




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

SGP4 is an orbit propagation model. It takes the orbital parameters contained in a TLE/OMM record and propagates them forward or backward from the record's epoch to calculate the satellite's position and velocity. SGP4 gives us a position in an Earth-centered inertial coordinate system and a velocity that we have to convert.

## Coordinate Conversions

Silmaril converts SGP4's **TEME** (True Equator, Mean Equinox) coordinates into **ECEF** (Earth-Centered, Earth-Fixed), then into geodetic latitude, longitude, and altitude.

```text
TEME → ECEF → Latitude / Longitude / Altitude
```

### TEME → ECEF

SGP4 provides the satellite position as:

$$
(x_{TEME}, y_{TEME}, z_{TEME})
$$

Calculate Julian centuries since J2000.0:

$$
T = \frac{JD - 2451545.0}{36525}
$$

Calculate Greenwich Mean Sidereal Time:

$$
\theta = 280.46061837 + 360.98564736629(JD - 2451545.0) + 0.000387933T^2-
\frac{T^3}{38710000}
$$

Normalize $\theta$ to $0^\circ$–$360^\circ$ and convert to radians.

Then rotate TEME into ECEF:

$$
x_{ECEF} = x_{TEME}\cos(\theta) + y_{TEME}\sin(\theta)
$$

$$
y_{ECEF} = -x_{TEME}\sin(\theta) + y_{TEME}\cos(\theta)
$$

$$
z_{ECEF} = z_{TEME}
$$

### ECEF → Geodetic

Silmaril uses the **WGS84** ellipsoid:

$$
a = 6378.137\text{ km}
$$

$$
f = \frac{1}{298.257223563}
$$

$$
e^2 = f(2-f)
$$

Longitude:

$$
\lambda = atan2(y,x)
$$

Distance from Earth's rotational axis:

$$
p = \sqrt{x^2+y^2}
$$

The latitude and altitude are then solved iteratively using:

$$
N = \frac{a}{\sqrt{1-e^2\sin^2(\phi)}}
$$

$$
h = \frac{p}{\cos(\phi)} - N
$$

until the latitude converges.

### Reference Models

* **WGS72** — SGP4 propagation
* **WGS84** — geodetic latitude, longitude, and altitude

        

