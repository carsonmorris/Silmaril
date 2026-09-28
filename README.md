# Silmaril: Satellite Tracking & Orbital Visualization

**Silmaril** is a satellite tracking and orbital visualization platform that calculates and displays the current and predicted positions of satellites in Earth orbit.

The project combines orbital mechanics, public spaceflight data, backend development, databases, APIs, and interactive 3D visualization into a single application.

> *"The Silmarils were three great jewels, created by Fëanor in the Years of the Trees, which captured the light of the Two Trees of Valinor."*

The name is a nod to the Silmarils' association with light and the heavens, while the project itself focuses on tracking objects that actually orbit Earth.

---

## Project Goals

The goal of Silmaril is to build a complete satellite tracking system from the ground up rather than relying on a third-party tracking application.

The project will:

* Retrieve publicly available satellite orbital data
* Parse and maintain satellite orbital elements
* Propagate satellite orbits using the SGP4 model
* Calculate satellite positions and velocities
* Convert orbital coordinates into latitude, longitude, and altitude
* Store satellite data in a searchable database
* Provide a REST API for satellite information and calculations
* Display satellites on an interactive map
* Visualize satellite orbits around a 3D Earth
* Calculate satellite visibility and upcoming passes for an observer
* Provide tools for exploring and searching the satellite catalog

---

# Architecture

Silmaril is designed as a multi-layer application:

```text
                 Public Satellite Data
                         │
                         ▼
               ┌──────────────────┐
               │ Data Ingestion   │
               │  TLE / OMM Data  │
               └────────┬─────────┘
                        │
                        ▼
               ┌──────────────────┐
               │ Orbital Engine   │
               │      SGP4        │
               └────────┬─────────┘
                        │
             ┌──────────┴──────────┐
             ▼                     ▼
      ┌──────────────┐      ┌──────────────┐
      │   Database   │      │  Calculations│
      │    SQLite    │      │ Position etc.│
      └──────┬───────┘      └──────┬───────┘
             │                     │
             └──────────┬──────────┘
                        ▼
                ┌───────────────┐
                │   FastAPI     │
                │   REST API    │
                └───────┬───────┘
                        │
                        ▼
                ┌───────────────┐
                │ Web Frontend   │
                │ React + Three  │
                │      .js       │
                └───────────────┘
```

---

# Roadmap

## Phase 1: Satellite Data

Build the foundation for retrieving and working with real satellite data.

### Goals

* Find a reliable public satellite data source
* Download TLE/OMM orbital data
* Parse orbital elements
* Create a basic satellite model
* Search satellites by name or catalog number
* Build command-line tools for exploring the data
* Add automated tests for data parsing

### Example

```text
ISS (ZARYA)
NORAD ID: 25544

Inclination:       51.64°
Eccentricity:      0.00041
Mean Motion:       15.50 rev/day
Epoch:             2026-XX-XX
```

---

## Phase 2: Orbital Propagation

Implement the orbital mechanics layer.

Silmaril will use the **SGP4 (Simplified General Perturbations 4)** model to propagate satellite positions from their orbital elements.

### Goals

* Integrate an SGP4 implementation
* Calculate position at a specified time
* Calculate velocity
* Convert coordinates between reference frames
* Calculate latitude, longitude, and altitude
* Predict future satellite positions
* Validate calculations against known satellite tracking data

Example:

```python
satellite.position_at(datetime.now())
```

Could return:

```text
Latitude:   43.615°
Longitude: -116.202°
Altitude:   418.7 km
Velocity:     7.66 km/s
```

---

## Phase 3: Satellite Database

Move satellite data into a persistent database.

### Initial Database

SQLite will be used during development.

Potential entities include:

```text
Satellite
├── NORAD ID
├── Name
├── International Designator
├── Object Type
├── Country
├── Launch Date
├── TLE / OMM Data
└── Last Updated

Orbital Data
├── Satellite ID
├── Epoch
├── Inclination
├── Eccentricity
├── Mean Motion
└── Orbital Elements
```

### Features

* Satellite search
* Filtering by orbit characteristics
* Filtering by country or object type
* Database updates
* Historical orbital data
* Indexed queries for large satellite catalogs

---

## Phase 4: REST API

Build a backend API using **FastAPI**.

Potential endpoints:

```text
GET /satellites
GET /satellites/{id}
GET /satellites/{id}/position
GET /satellites/{id}/trajectory
GET /satellites/{id}/passes
```

Example:

```http
GET /satellites/25544/position
```

Response:

```json
{
  "satellite": "ISS (ZARYA)",
  "norad_id": 25544,
  "latitude": 43.615,
  "longitude": -116.202,
  "altitude_km": 418.7
}
```

The API will eventually provide the foundation for the web application and potentially other clients.

---

# Phase 5: Interactive Satellite Map

Build an interactive map displaying satellite positions.

### Features

* Current satellite positions
* Satellite search
* Satellite selection
* Ground tracks
* Orbit paths
* Position updates
* Satellite information panels
* Filtering by satellite type
* Tracking multiple satellites simultaneously

The map should allow a user to select a satellite and follow its movement around Earth.

---

# Phase 6: 3D Earth Visualization

Move beyond a traditional map and create a 3D orbital visualization using **Three.js/WebGL**.

The visualization will include:

* 3D Earth
* Satellite positions
* Orbital paths
* Ground tracks
* Camera controls
* Satellite labels
* Multiple simultaneous satellites
* Time acceleration

Example:

```text
                    Satellite
                       ●
                      / \
                     /   \
                    /     \
               ────/───────\────
             /                   \
            /       Earth         \
           |         🌎            |
            \                     /
             \___________________/
```

A simulation clock could allow the user to accelerate time:

```text
Real Time       1x
10x             10x
100x            100x
1000x           1000x
```

This makes it possible to visualize orbital motion over hours or days.

---

# Phase 7: Observer & Satellite Passes

Allow users to specify an observation location.

Given:

```text
Observer
├── Latitude
├── Longitude
└── Elevation
```

Silmaril can calculate when satellites will be visible from that location.

### Pass Information

For each upcoming pass:

```text
ISS

Rise:           21:14:32
Maximum Elev.:  67.4°
Set:            21:21:08

Azimuth:
Rise:           284°
Maximum:        12°
Set:            101°

Duration:       6m 36s
```

This will introduce additional concepts such as:

* Observer coordinates
* Azimuth/elevation
* Horizon calculations
* Rise and set times
* Maximum elevation
* Visibility windows

---

# Phase 8: Visibility Prediction

Build a higher-level "What can I see?" feature.

A user could provide:

```text
Location: Boise, Idaho
Date:     2026-10-01
Time:     21:00
```

Silmaril could return satellites that are potentially visible during the selected period.

Possible filters:

* Minimum elevation
* Maximum magnitude
* Satellite type
* Duration
* Time window

Eventually, the system could distinguish between satellites that are technically above the horizon and satellites that are likely to be visually observable.

---

# Future Ideas

Once the core system is complete, Silmaril could expand into several additional areas.

### Orbital Analysis

* Orbital decay visualization
* Historical orbit comparison
* Apogee/perigee calculations
* Orbital period calculations
* Inclination analysis
* Eccentricity visualization

### Satellite Constellations

* Starlink visualization
* GPS constellation
* Weather satellites
* Earth observation satellites
* Communications constellations
* Custom constellation creation

### Conjunction Visualization

Visualize close approaches between satellites.

Potential features:

* Closest approach calculation
* Relative velocity
* Distance between objects
* 3D conjunction visualization
* Historical conjunction data

### Ground Stations

Allow users to define ground stations and calculate:

* Communication windows
* Satellite visibility
* Pass duration
* Antenna pointing angles
* Upcoming passes

### Spacecraft Simulation

Allow users to create fictional spacecraft and experiment with:

* Orbital insertion
* Maneuvers
* Hohmann transfers
* Inclination changes
* Transfer orbits

### Solar System Expansion

Eventually expand the visualization beyond Earth orbit.

Potential objects:

* Moon
* Sun
* Planets
* Asteroids
* Interplanetary spacecraft

---

# Technology Stack

## Backend

* Python
* FastAPI
* SGP4
* SQLite
* Pydantic
* Pytest

## Frontend

* TypeScript
* React
* Three.js
* WebGL

## Development

* Git
* GitHub
* Docker
* GitHub Actions
* Automated testing

The technology stack may evolve as the project develops.

---

# Data Sources

Silmaril will use publicly available orbital data.

Potential sources include:

* CelesTrak
* Space-Track
* Other publicly available spaceflight datasets

Orbital data will be treated as time-dependent data rather than permanent satellite properties. In particular, orbital elements such as TLEs have an associated epoch and become less accurate as they age.

---

# Design Principles

### Learn the underlying systems

Silmaril is intended to be more than an application that calls an API and displays the response.

The goal is to understand what is happening between the raw orbital data and the final visualization.

### Separate concerns

The project will maintain clear boundaries between:

```text
Data ingestion
      ↓
Orbital calculations
      ↓
Database
      ↓
API
      ↓
Visualization
```

This allows individual components to be tested and developed independently.

### Test calculations

Orbital calculations are especially important to validate.

Tests will compare calculated results against known values and expected behavior rather than relying solely on visual inspection.

### Build incrementally

The project will start as a small Python application and gradually evolve into a full-stack application.

Each phase should produce something functional before moving to the next.

---

# Project Structure

The planned structure is approximately:

```text
silmaril/
│
├── backend/
│   ├── api/
│   ├── database/
│   ├── orbital/
│   ├── satellites/
│   └── main.py
│
├── frontend/
│   ├── components/
│   ├── scenes/
│   ├── maps/
│   └── App.tsx
│
├── tests/
│   ├── test_orbital.py
│   ├── test_satellites.py
│   └── test_api.py
│
├── scripts/
│   └── data_ingestion.py
│
├── docs/
│
├── docker/
│
├── requirements.txt
├── README.md
└── LICENSE
```

The exact structure will evolve as the application grows.

---

# Why Silmaril?

The Silmarils were three jewels created by Fëanor that contained the light of the Two Trees of Valinor.

The project name is a small Tolkien reference to **light, observation, and the heavens**, while the application itself focuses on real objects moving through Earth's orbit.

The name also leaves room for the project to grow beyond simple satellite tracking into a broader exploration of orbital mechanics and space.

---

# Project Status

🚧 **Early Development**

The project is currently in the planning and architecture stage.

The first milestone is to retrieve real satellite orbital data, parse it correctly, and calculate satellite positions using SGP4.

---

# Long-Term Goal

Silmaril should eventually provide a complete pipeline from raw orbital data to interactive visualization:

```text
             REAL SATELLITE DATA
                     │
                     ▼
              Orbital Elements
                     │
                     ▼
                   SGP4
                     │
                     ▼
             Position / Velocity
                     │
                     ▼
             Orbital Calculations
                     │
                     ▼
                  Database
                     │
                     ▼
                 REST API
                     │
                     ▼
          ┌──────────┴──────────┐
          ▼                     ▼
     2D Map                 3D Earth
          │                     │
          └──────────┬──────────┘
                     ▼
              Satellite Explorer
```

The end result will be a full-stack space application that demonstrates software engineering, data processing, database design, API development, numerical computation, and interactive visualization in one project.
