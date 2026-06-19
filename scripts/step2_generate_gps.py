import os
import random
import numpy as np
import pandas as pd
import osmnx as ox
from shapely.geometry import LineString
from datetime import datetime, timedelta  


# 1. Tải mạng lưới đường dạng đồ thị (Graph)

place_name = "District 1, Ho Chi Minh City, Vietnam"
G = ox.graph_from_place(place_name, network_type="drive")
G_proj = ox.project_graph(G, to_crs="EPSG:4326")

nodes = list(G_proj.nodes())
all_gps_points = []

# 2. Mô phỏng 10 xe chạy các tuyến đường khác nhau

for trip_id in range(1, 11):
    
    # Thiết lập mốc thời gian bắt đầu cho mỗi xe (Ví dụ: xuất phát lúc 8h00 sáng hôm nay)
    current_time = datetime.now().replace(hour=8, minute=0, second=0, microsecond=0)
    
    route = None
    while route is None:
        start_node = random.choice(nodes)
        end_node = random.choice(nodes)
        try:
            route = ox.shortest_path(G_proj, start_node, end_node, weight="length")
        except:
            pass
    
    # 3. Trích xuất và băm nhỏ tọa độ dọc theo tuyến đường

    for i in range(len(route) - 1):
        u, v = route[i], route[i+1]
        edge_data = G_proj.get_edge_data(u, v)
        first_key = list(edge_data.keys())[0]
        data = edge_data[first_key]
        
        if 'geometry' in data:
            line = data['geometry']
        else:
            u_node = G_proj.nodes[u]
            v_node = G_proj.nodes[v]
            line = LineString([(u_node['x'], u_node['y']), (v_node['x'], v_node['y'])])
        
        distances = np.arange(0, line.length, 0.0001)
        if len(distances) == 0:
            distances = [0.0]
            
        for dist in distances:
            point = line.interpolate(dist)
            
            # Giả lập nhiễu GPS Drift
            noise_x = np.random.normal(0, 0.00013)
            noise_y = np.random.normal(0, 0.00013)
            
            # Giả lập thời gian di chuyển: Cứ mỗi điểm tiếp theo cách điểm trước ngẫu nhiên 5 đến 15 giây
            current_time += timedelta(seconds=random.randint(5, 15))
            
            all_gps_points.append({
                'id': len(all_gps_points) + 1,
                'vehicle_id': f"XE_{trip_id:02d}",
                'timestamp': current_time.strftime('%Y-%m-%d %H:%M:%S'),  
                'longitude': point.x + noise_x,
                'latitude': point.y + noise_y
            })

# 4. Xuất ra file CSV lớn đầy đủ thuộc tính

df = pd.DataFrame(all_gps_points)
df.to_csv("raw_gps_data.csv", index=False)