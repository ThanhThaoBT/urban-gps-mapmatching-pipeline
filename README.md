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
2. Activate your GIS environment and run the data:
   ```bash
   python step2_generate_gps.py
3. Execute the PostGIS map-matching pipeline:
   ```bash
   python step3_map_matching.py
4. Open the generated snapped_gps_route.gpkg file in QGIS to visualize the layers.

## 📊 Visual Quality Control (QC) & Error Analysis

To make the map data readable and audit the pipeline's accuracy, a professional QGIS Print Layout was configured with a clear Map Legend and Scale Bar. This allows us to distinguish between raw noisy coordinates and the post-processed tracks while diagnosing structural urban edge cases:

### 1. Overall Pipeline Output (Raw vs. Snapped)
The PostGIS matching algorithm successfully processes telemetry noise, filtering out the urban drift to produce a clean, synchronized sequence of points bound tightly to the road centerlines.
* **Categorized Rainbow Palette:** Each vehicle (from XE_01 to XE_10) is assigned a distinct color from a spectral color ramp, allowing simultaneous tracking of multiple trips without confusion.
* **Raw Points vs. Snapped Points:** The raw data appears as white circles with explicit text labels, clearly showcasing hardware drift inside buildings or parks. In contrast, the post-processed PostGIS output is rendered as a clean sequence of color-coded points aligned perfectly along the road segments (highway_district 1).
<img width="3507" height="2480" alt="Map Matching Report" src="https://github.com/user-attachments/assets/2da25b95-eaf2-43ca-9302-19c33fb654c9" />

### 2. Deep-Dive: Lane-Jumping Error (On Dual Carriageways)
On major arterial roads like Le Loi Street, which features wide physical central barriers separating opposite traffic directions, heavy GPS drift causes points to cross the median line. Because the current ST_ClosestPoint algorithm matches points independently based strictly on geometric distance, the snapped coordinates "teleport" or jump across lanes, showing an impossible physical movement.

### 3. Deep-Dive: Street-Jumping Error (On Parallel Streets)
In grid-like urban sectors where narrow streets run tightly parallel to each other (such as Ly Tu Trong Street and Le Thanh Ton Street), a large GPS drift variance can push a point closer to the adjacent street. Without a temporal network continuity check, the geometric algorithm mistakenly snaps the point to the wrong street entirely.

## ⚠️ Limitations & Future Work

While the current Geometric Map-Matching approach (ST_ClosestPoint) is highly efficient—processing thousands of rows in milliseconds—point-by-point spatial queries are highly susceptible to severe urban noise.

## 🔮 Planned Enhancements:

* **Spatio-Temporal Constraints:** Incorporate vehicle heading (bearing/orientation) and calculate speed constraints between sequential timestamps to eliminate physically impossible jumps between lanes or streets.

* **Advanced Algorithms:** Transition from independent point snapping to sequence-to-line matching by researching and implementing Hidden Markov Models (HMM) to solve path-probability estimation across complex road network topologies.

