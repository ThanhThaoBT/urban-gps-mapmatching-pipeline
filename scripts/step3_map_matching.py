import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import psycopg2
from shapely import wkt

df_raw = pd.read_csv("../data/raw_gps_data.csv")
geometry = [Point(xy) for xy in zip(df_raw['longitude'], df_raw['latitude'])]
gdf_gps = gpd.GeoDataFrame(df_raw, geometry=geometry, crs="EPSG:4326")
gdf_gps = gdf_gps.to_crs("EPSG:32648")
conn = psycopg2.connect(dbname="gps_matching", user="postgres", password="your-password", 
host="localhost")
cursor = conn.cursor()
snapped_points = []
print("Bắt đầu thực hiện thuật toán Map-Matching không gian...")
for idx, row in gdf_gps.iterrows():
    point_wkt = row['geometry'].wkt
    # Tìm kiếm con đường gần nhất trong bán kính 30m
    query = """
        SELECT edge_id, street_name, speed_limit,
               ST_AsText(ST_ClosestPoint(geom, ST_GeomFromText(%s, 32648))) as 
snapped_geom,
               ST_Distance(geom, ST_GeomFromText(%s, 32648)) as distance
        FROM road_network
        WHERE ST_DWithin(geom, ST_GeomFromText(%s, 32648), 30)
        ORDER BY ST_Distance(geom, ST_GeomFromText(%s, 32648)) ASC
        LIMIT 1;
    """
    cursor.execute(query, (point_wkt, point_wkt, point_wkt, point_wkt))
    result = cursor.fetchone()
    if result:
        edge_id, street_name, speed_limit, snapped_wkt, dist = result
        snapped_point_geom = wkt.loads(snapped_wkt)
        snapped_points.append({
            "vehicle_id": row['vehicle_id'],
            "timestamp": row['timestamp'],
            "original_lon": row['longitude'],
            "original_lat": row['latitude'],
            "street_name": street_name,
            "distance_error_meters": round(dist, 2),
            "geometry": snapped_point_geom
        })
gdf_output = gpd.GeoDataFrame(snapped_points, geometry="geometry", crs="EPSG:32648")
gdf_output = gdf_output.to_crs("EPSG:4326")
gdf_output.to_file("../data/snapped_gps_route.gpkg", layer="snapped_points", driver="GPKG")
cursor.close()
conn.close()
