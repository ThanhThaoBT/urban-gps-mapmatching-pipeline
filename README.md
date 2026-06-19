# Urban GPS Map-Matching Pipeline for Fleet Management

An automated, end-to-end spatial data pipeline designed to simulate, process, and clean raw vehicle GPS telemetry data. This project solves the classic "GPS drift" and "urban canyon" problems by automatically snapping noisy GPS points onto the real-world road network of District 1, Ho Chi Minh City, using Python and PostGIS.

## 🚀 Key Features

* **Fleet Telemetry Simulation (Python):** Automatically extracts the road network topology using `OSMnx` and generates realistic spatial trajectories for a fleet of 10 vehicles (2000 tracking points).
* **Realistic Noise Injection:** Integrates customized Gaussian Noise to simulate hardware GPS drift and signal multipath reflection in high-density urban areas.
* **Spatial Database Automation (PostGIS):** Optimizes spatial queries with `GIST` indexes and implements an automated pipeline to snap noisy points to the nearest road centerlines using `ST_ClosestPoint` and `ST_DWithin`.
* **High Performance:** Processes and matches the entire dataset in under 0.5 seconds.
* **Visual Quality Control:** Ready-to-use spatial layers for QGIS visualization with advanced rendering (Feature Blending) for hot-spot density analysis.

## 🛠️ Tech Stack

* **Language:** Python 3.12
* **Core Libraries:** GeoPandas, OSMnx, NumPy, Pandas, Shapely
* **Database:** PostgreSQL + PostGIS Extension
* **GIS Software:** QGIS (for visualization and Spatial QC)

## 📐 System Architecture

The pipeline follows a 3-stage data engineering architecture:
1. **Data Generation (`step2_generate_gps.py`):** Downloads OSM road networks, simulates sequential vehicle movements, adds time-series timestamps, injects noise, and exports to a large `raw_gps_data.csv`.
2. **Spatial Processing (`step3_map_matching.py`):** Connects to the spatial database, injects the raw points, builds spatial topology, and executes the geometric map-matching algorithm.
3. **Export & Visualization:** Outputs a structured `.gpkg` (GeoPackage) file containing both raw and snapped layers for immediate QGIS analysis.

## 📋 Database Schema

### 1. `raw_gps_data`
* `id` (SERIAL, Primary Key): Unique point identifier.
* `vehicle_id` (VARCHAR): Vehicle identifier (e.g., `XE_01` to `XE_10`).
* `timestamp` (TIMESTAMP): Chronological tracking time.
* `longitude` / `latitude` (DOUBLE PRECISION): Raw coordinates.
* `geom` (Geometry, Point, 4326): Spatial geometry of the noisy point.

### 2. `snapped_points`
* `id` (SERIAL, Primary Key)
* `vehicle_id` (VARCHAR)
* `timestamp` (TIMESTAMP)
* `distance_error_meters` (DOUBLE PRECISION): Distance between the raw noisy point and the matched road.
* `geom` (Geometry, Point, 4326): Matched geometry exactly on the road centerline.

## 💻 How to Run

1. Clone the repository:
   ```bash
   git clone [https://github.com/YOUR_USERNAME/urban-gps-mapmatching-pipeline.git](https://github.com/YOUR_USERNAME/urban-gps-mapmatching-pipeline.git)
   cd urban-gps-mapmatching-pipeline
