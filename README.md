<div align="center">

# ✦ Silmaril

**A satellite-tracking and orbital visualization project inspired by the lights above Earth.**

[![Python](https://img.shields.io/badge/Python-SGP4%20tracker-7ce8e5?style=flat-square&labelColor=0b1925)](https://www.python.org/)
[![Orbit model](https://img.shields.io/badge/Orbit-SGP4-f2d38a?style=flat-square&labelColor=0b1925)](https://celestrak.org/)
[![Map](https://img.shields.io/badge/Map-Leaflet%20%2B%20Folium-79e8e5?style=flat-square&labelColor=0b1925)](https://python-visualization.github.io/folium/)

*A small Tolkein reference: A Silmaril is a jewel of starlight, reimagined as a window into the moving lights above us.*

</div>

---

## About Silmaril

Silmaril retrieves orbital data, propagates satellite positions with **SGP4**, and displays a selected object's live location on an interactive map. The project explores orbital mechanics, satellite data, backend development, and interactive visualization.

The map uses Esri's dark-gray basemap and reference labels and includes a calculated 24-hour orbital trail, viewable over 1, 6, or 24 hours. Trail positions are calculated from orbital data rather than loaded from historical tracking records. A REST API, 3D Earth visualization, and satellite pass predictions are possible directions for future development.

Position calculations have been verified against [AstroViewer's ISS tracker](https://www.astroviewer.net/iss/en/).

## Technology

| Layer | Stack |
| --- | --- |
| Backend | Python standard-library HTTP server, SGP4, SQLite, Pydantic, requests |
| Map interface | Folium-generated HTML, JavaScript, Leaflet |
| Development | Git, Pytest |

## Orbital data


The app reads its satellite catalog and cached orbital data from a pre-populated local SQLite database (`data/satellites.db`). Missing orbital records are retrieved from CelesTrak, and cached orbital data older than three hours is refreshed when that satellite is selected.

The landing page reports the number of non-decayed Earth-orbiting objects with confirmed CelesTrak GP orbital data in the local database. SATCAT's element-availability flag alone does not guarantee that a GP record is currently available from CelesTrak, so Silmaril only counts objects for which valid orbital data has been retrieved.

Users can switch between a curated collection of notable satellites and the full cached catalog, which is displayed in pages of 50 objects. Satellites can be searched by name or NORAD catalog number and selected directly from the list for tracking.

When a satellite is selected, Silmaril uses its cached orbital data when available and refreshes stale data from CelesTrak as needed. The satellite's position is then propagated to the current time and displayed on the map.

The notable collection includes the ISS, Hubble Space Telescope, Tiangong, several NOAA weather satellites, Terra, Aqua, Landsat 9, Sentinel-2A, GOES-16, and Suomi NPP. Objects such as the James Webb Space Telescope are excluded because JWST isn't actually an Earth-orbiting satellite in the way the objects Silmaril currently propagates are.

## Getting started

### Requirements

- Python 3.14 or later
- Internet connection for retrieving and refreshing orbital data from CelesTrak

### Installation

Download the Zip or Clone the repository:

```bash
git clone https://github.com/carsonmorris/Silmaril.git
cd silmaril
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate the virtual environment.

**Windows (PowerShell):**

```powershell
.venv\Scripts\Activate.ps1
```

**macOS / Linux:**

```bash
source .venv/bin/activate
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### Running Silmaril

Start the application from the project root:

```bash
python main.py
```

Silmaril will start a local web server. 

The included `data/satellites.db` database contains the pre-populated satellite catalog and cached orbital data. Cached orbital data is refreshed from CelesTrak when necessary as satellites are selected.

### Running tests

From the project root:

```bash
python -m pytest
```

```text
silmaril/
├── backend/
├── data/
├── docs/
├── img/
├── scripts/
├── tests/
├── main.py
├── styles.css
├── requirements.txt
└── README.md
```

## Coordinate conversions

Silmaril converts SGP4's **TEME** (True Equator, Mean Equinox) coordinates into **ECEF** (Earth-Centered, Earth-Fixed), then into geodetic latitude, longitude, and altitude:

```text
TEME  →  ECEF  →  Latitude / Longitude / Altitude
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

Normalize $\theta$ to $0^\circ$ – $360^\circ$ and convert to radians. Then rotate TEME into ECEF:

$$
x_{ECEF} = x_{TEME}\cos(\theta) + y_{TEME}\sin(\theta)
$$

$$
y_{ECEF} = -x_{TEME}\sin(\theta) + y_{TEME}\cos(\theta)
$$

$$
z_{ECEF} = z_{TEME}
$$

### ECEF → geodetic coordinates

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

The latitude and altitude are solved iteratively using:

$$
N = \frac{a}{\sqrt{1-e^2\sin^2(\phi)}}
$$

$$
h = \frac{p}{\cos(\phi)} - N
$$

Iterations continue until latitude converges. Because Earth is an ellipsoid, latitude and altitude are interdependent: the calculation estimates latitude, uses it to estimate altitude, then uses that altitude to refine latitude until the change becomes negligible.

### Reference models

* **WGS72** — SGP4 propagation
* **WGS84** — geodetic latitude, longitude, and altitude

SGP4 takes the orbital parameters in a TLE/OMM record and propagates them forward or backward from its epoch to calculate a satellite's position and velocity. Its position is in an Earth-centered inertial coordinate system and must be converted for mapping.

## CelesTrak reference

Many thanks to **T.S. Kelso** for his outstanding work on satellite tracking and orbital data.

CelesTrak GP queries use this URL shape:

```text
https://celestrak.org/NORAD/elements/gp.php?{QUERY}=VALUE[&FORMAT=VALUE]
```

`{QUERY}` must be uppercase:

| Query | Meaning |
| --- | --- |
| `CATNR` | Catalog number (1–9 digits); retrieves a single catalog number |
| `INTDES` | International Designator (`yyyy-nnn`); retrieves objects associated with a launch |
| `GROUP` | A satellite group from CelesTrak's Current Data page |
| `NAME` | Search for satellite names by part of the name |
| `SPECIAL` | Special data sets: `GPZ`, `GPZ-PLUS`, or `DECAYING` |

Example: ISS orbital data (catalog number 25544, JSON): https://celestrak.org/NORAD/elements/gp.php?CATNR=25544&FORMAT=JSON

## Orbital elements, at a glance

* **OMM** — Orbit Mean-Elements Message.
* **Epoch** — Date and time at which the orbital data is considered accurate.
* **Inclination** — How tilted the orbit is relative to Earth; zero degrees is in line with the equator.
* **Eccentricity** — How stretched the orbit is; low eccentricity means nearly circular.
* **Mean motion** — How quickly the satellite orbits, expressed in revolutions per day.
* **RAAN** — Right Ascension of the Ascending Node; the orientation of the orbital plane around Earth.
* **Mean anomaly** — A steadily increasing mathematical angle used to track position along an elliptical orbit.
* **Argument of perigee** — The orientation of the orbit's closest point to Earth.
* **BSTAR** — A parameter used to model atmospheric drag.
* **Mean motion derivative** — How mean motion changes over time, in revolutions per day squared.
* **Mean motion second derivative** — How the mean motion derivative changes, in revolutions per day cubed.
* **Revolutions at epoch** — The satellite's orbit revolution count at the epoch.

<div align="center">

*Look up. Something is always in motion.*

</div>
