import os
import osmnx as ox
import psycopg2
from shapely.geometry import LineString

# 1. Tải mạng lưới đường giao thông xe ô tô tại Quận 1, TP.HCM

place_name = "District 1, Ho Chi Minh City, Vietnam"
G = ox.graph_from_place(place_name, network_type="drive")

G_projected = ox.project_graph(G, to_crs="EPSG:32648")

# 2. Kết nối tới PostgreSQL

conn = psycopg2.connect(
    dbname="gps_matching", user="postgres", password="your-password", host="localhost", 
port="5432"
)
cursor = conn.cursor()

# 3. Duyệt qua các cạnh (edges) trong đồ thị và lưu vào CSDL

for u, v, k, data in G_projected.edges(keys=True, data=True):
    osm_id = data.get('osmid', 0)

    if isinstance(osm_id, list): 
        osm_id = osm_id[0]
   
    name = data.get('name', 'Unknown')
    if isinstance(name, list): name = name[0]
    highway = data.get('highway', 'unknown')
    maxspeed = data.get('maxspeed', 50)
    if 'geometry' in data:
        geo = data['geometry']
    else:
        node_u = G_projected.nodes[u]
        node_v = G_projected.nodes[v]
        geo = LineString([(node_u['x'], node_u['y']), (node_v['x'], node_v['y'])])
    wkt_geom = geo.wkt
    cursor.execute("""
 INSERT INTO road_network (osm_id, street_name, highway_type, speed_limit, geom)
        VALUES (%s, %s, %s, %s, ST_GeomFromText(%s, 32648));
    """, (osm_id, name, highway, 50, wkt_geom))
conn.commit()
cursor.close()
conn.close()
print("Hoàn thành nạp dữ liệu mạng lưới đường!")