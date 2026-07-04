"""CopyMind - 快递网点运营分析：数据处理脚本"""

import csv
import json
import math
from collections import Counter


def main():
    # 1. 读取青海省快递网点数据
    cities = {}
    with open(r'C:\Users\Kanran\Desktop\中文数据快递网点.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if row[1] == '青海省' or row[1] == '贵州省':
                city = row[2]
                district = row[3]
                if city not in cities:
                    cities[city] = {'districts': Counter(), 'lngs': [], 'lats': []}
                cities[city]['districts'][district] += 1
                cities[city]['lngs'].append(float(row[4]))
                cities[city]['lats'].append(float(row[5]))

    # 2. 读取全国交通优势度
    traffic_scores = {}
    with open(r'C:\Users\Kanran\Desktop\7.2.csv', 'r', encoding='gbk') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if row[0]:
                traffic_scores[row[0]] = {
                    'traffic_network_density': float(row[1]),
                    'traffic_hub_influence': float(row[2]),
                    'location_advantage': float(row[3]),
                    'traffic_advantage': float(row[4])
                }

    # 3. 计算指标
    results = []
    for city, data in cities.items():
        n = len(data['lngs'])
        lats = data['lats']
        lngs = data['lngs']
        avg_lat = sum(lats) / n
        avg_lng = sum(lngs) / n

        # 估算面积
        min_lat, max_lat = min(lats), max(lats)
        min_lng, max_lng = min(lngs), max(lngs)
        w = haversine(avg_lat, min_lng, avg_lat, max_lng)
        h = haversine(min_lat, avg_lng, max_lat, avg_lng)
        area = w * h

        # 标准差距离
        dists = [haversine(avg_lat, avg_lng, lat, lng) for lat, lng in zip(lats, lngs)]
        std_dist = math.sqrt(sum(d**2 for d in dists) / n)

        districts_data = [{'name': d, 'count': c} for d, c in data['districts'].most_common()]
        traffic = traffic_scores.get(city, {})

        results.append({
            'province': data.get('province', ''),
            'city': city,
            'total_points': n,
            'districts_count': len(data['districts']),
            'districts': districts_data,
            'center': {'lat': round(avg_lat, 4), 'lng': round(avg_lng, 4)},
            'area_km2': round(area, 2),
            'density_per_km2': round(n / area, 4) if area > 0 else 0,
            'std_distance_km': round(std_dist, 2),
            'traffic_network_density': traffic.get('traffic_network_density', 0),
            'traffic_hub_influence': traffic.get('traffic_hub_influence', 0),
            'location_advantage': traffic.get('location_advantage', 0),
            'traffic_advantage': traffic.get('traffic_advantage', 0)
        })

    # 保存
    output = {'cities': results, 'traffic_scores': traffic_scores}
    with open(r'D:\新建文件夹\express-analysis\express_data.json', 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print(json.dumps(results, ensure_ascii=False, indent=2))
    print('\n保存完成！')


def haversine(lat1, lng1, lat2, lng2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng/2)**2
    return 2 * R * math.asin(math.sqrt(a))


if __name__ == '__main__':
    main()
import csv, json, math
from collections import Counter
import numpy as np


def main():
    cities = load_data()
    traffic_scores = load_traffic()
    results = compute_metrics(cities, traffic_scores)
    save(results, traffic_scores)


def load_data():
    cities = {}
    with open(r'C:\Users\Kanran\Desktop\中文数据快递网点.csv', 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if row[1] == '青海省' or row[1] == '贵州省':
                city = row[2]
                district = row[3]
                lng = float(row[4])
                lat = float(row[5])
                if city not in cities:
                    cities[city] = {'province': row[1], 'districts': Counter(), 'lngs': [], 'lats': [], 'coords_by_district': {}}
                cities[city]['districts'][district] += 1
                cities[city]['lngs'].append(lng)
                cities[city]['lats'].append(lat)
                if district not in cities[city]['coords_by_district']:
                    cities[city]['coords_by_district'][district] = {'lngs': [], 'lats': []}
                cities[city]['coords_by_district'][district]['lngs'].append(lng)
                cities[city]['coords_by_district'][district]['lats'].append(lat)
    return cities


def load_traffic():
    traffic_scores = {}
    with open(r'C:\Users\Kanran\Desktop\7.2.csv', 'r', encoding='gbk') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            if row[0]:
                traffic_scores[row[0]] = {
                    'traffic_network_density': float(row[1]),
                    'traffic_hub_influence': float(row[2]),
                    'location_advantage': float(row[3]),
                    'traffic_advantage': float(row[4])
                }
    return traffic_scores


def compute_metrics(cities, traffic_scores):
    results = []
    for city, data in cities.items():
        n = len(data['lngs'])
        lats = np.array(data['lats'])
        lngs = np.array(data['lngs'])
        avg_lat = float(lats.mean())
        avg_lng = float(lngs.mean())

        min_lat, max_lat = float(lats.min()), float(lats.max())
        min_lng, max_lng = float(lngs.min()), float(lngs.max())
        w = haversine(avg_lat, float(lngs.min()), avg_lat, float(lngs.max()))
        h = haversine(float(lats.min()), avg_lng, float(lats.max()), avg_lng)
        area = w * h if w > 0 and h > 0 else 1

        dists = [haversine(avg_lat, avg_lng, lat, lng) for lat, lng in zip(data['lats'], data['lngs'])]
        std_dist = math.sqrt(sum(d**2 for d in dists) / n)

        ellipse = calc_std_ellipse(lngs, lats)
        nnd = calc_nnd(lats, lngs)
        kde_result = calc_kde(lats, lngs)

        district_densities, blind_spots = calc_blind_spots(data['coords_by_district'], n, area)

        districts_data = [{'name': d, 'count': c} for d, c in data['districts'].most_common()]
        traffic = traffic_scores.get(city, {})

        results.append({
            'province': data.get('province', ''),
            'city': city,
            'total_points': n,
            'districts_count': len(data['districts']),
            'districts': districts_data,
            'district_densities': district_densities,
            'blind_spots': blind_spots,
            'center': {'lat': round(avg_lat, 4), 'lng': round(avg_lng, 4)},
            'area_km2': round(area, 2),
            'density_per_km2': round(n / area, 4) if area > 0 else 0,
            'std_distance_km': round(std_dist, 2),
            'std_ellipse': ellipse,
            'avg_nnd_km': round(nnd, 3),
            'kde': kde_result,
            'traffic_network_density': traffic.get('traffic_network_density', 0),
            'traffic_hub_influence': traffic.get('traffic_hub_influence', 0),
            'location_advantage': traffic.get('location_advantage', 0),
            'traffic_advantage': traffic.get('traffic_advantage', 0)
        })
    return results


def calc_blind_spots(coords_by_district, city_total, city_area):
    district_densities = []
    blind_spots = []
    avg_density = city_total / city_area if city_area > 0 else 0
    for d_name, coords in coords_by_district.items():
        dlngs = np.array(coords['lngs'])
        dlats = np.array(coords['lats'])
        d_n = len(dlngs)
        d_min_lat, d_max_lat = float(dlats.min()), float(dlats.max())
        d_min_lng, d_max_lng = float(dlngs.min()), float(dlngs.max())
        d_w = haversine(float(dlats.mean()), d_min_lng, float(dlats.mean()), d_max_lng)
        d_h = haversine(d_min_lat, float(dlngs.mean()), d_max_lat, float(dlngs.mean()))
        d_area = d_w * d_h if d_w > 0 and d_h > 0 else 1
        d_density = d_n / d_area
        district_densities.append({'name': d_name, 'count': d_n, 'density': round(d_density, 4), 'area': round(d_area, 2), 'bounds': {'min_lng': round(d_min_lng, 4), 'max_lng': round(d_max_lng, 4), 'min_lat': round(d_min_lat, 4), 'max_lat': round(d_max_lat, 4)}})
        if avg_density > 0 and d_density < avg_density * 0.3:
            blind_spots.append({
                'district': d_name,
                'count': d_n,
                'density': round(d_density, 4),
                'reason': '密度仅全市平均' + str(round(d_density/avg_density*100, 1)) + '%'
            })
    district_densities.sort(key=lambda x: x['density'], reverse=True)
    return district_densities, blind_spots


def calc_std_ellipse(lngs, lats):
    n = len(lngs)
    cx = float(lngs.mean())
    cy = float(lats.mean())
    dx = lngs - cx
    dy = lats - cy
    A = float(sum(dx**2) - sum(dy**2))
    B = float(2 * sum(dx * dy))
    angle = 0.5 * math.atan2(B, A) if not (A == 0 and B == 0) else 0
    cos_a, sin_a = math.cos(angle), math.sin(angle)
    x_std = math.sqrt(max(0, 2 * sum((dx * cos_a + dy * sin_a)**2).item() / n))
    y_std = math.sqrt(max(0, 2 * sum((dx * (-sin_a) + dy * cos_a)**2).item() / n))
    lat_rad = math.radians(cy)
    km_lat = 111.32
    km_lng = 111.32 * math.cos(lat_rad)
    return {
        'center': {'lat': round(cy, 4), 'lng': round(cx, 4)},
        'angle_deg': round(math.degrees(angle), 2),
        'x_std_km': round(x_std * km_lng, 2),
        'y_std_km': round(y_std * km_lat, 2),
        'area_km2': round(math.pi * max(x_std, 0.001) * max(y_std, 0.001) * km_lng * km_lat, 2)
    }


def calc_nnd(lats, lngs):
    n = len(lats)
    if n < 2:
        return 0
    total = 0.0
    count = 0
    for i in range(n):
        min_d = float('inf')
        li, lni = float(lats[i]), float(lngs[i])
        for j in range(n):
            if i != j:
                d = haversine(li, lni, float(lats[j]), float(lngs[j]))
                if d < min_d:
                    min_d = d
        if min_d < float('inf'):
            total += min_d
            count += 1
    return total / count if count > 0 else 0


def calc_kde(lats, lngs):
    """网格化密度分析"""
    n = len(lats)
    if n < 10:
        return {'high_density_ratio': 0, 'low_density_ratio': 0}
    lat_min, lat_max = float(lats.min()), float(lats.max())
    lng_min, lng_max = float(lngs.min()), float(lngs.max())
    if lat_max == lat_min or lng_max == lng_min:
        return {'high_density_ratio': 100, 'low_density_ratio': 0}
    grid_size = 20
    lat_step = (lat_max - lat_min) / grid_size
    lng_step = (lng_max - lng_min) / grid_size
    grid_counts = np.zeros((grid_size, grid_size))
    for i in range(n):
        gi = min(int((float(lats[i]) - lat_min) / lat_step), grid_size - 1)
        gj = min(int((float(lngs[i]) - lng_min) / lng_step), grid_size - 1)
        grid_counts[gi][gj] += 1
    max_count = grid_counts.max() if grid_counts.max() > 0 else 1
    total_cells = grid_size * grid_size
    high = int(np.sum(grid_counts >= max_count * 0.5))
    low = int(np.sum(grid_counts < max_count * 0.1))
    return {
        'high_density_cells': high,
        'low_density_cells': low,
        'high_density_ratio': round(high / total_cells * 100, 1),
        'low_density_ratio': round(low / total_cells * 100, 1)
    }


def haversine(lat1, lng1, lat2, lng2):
    R = 6371
    dlat = math.radians(lat2 - lat1)
    dlng = math.radians(lng2 - lng1)
    a = math.sin(dlat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlng/2)**2
    return 2 * R * math.asin(min(1, math.sqrt(a)))


def save(results, traffic_scores):
    output = {'cities': results, 'traffic_scores': traffic_scores}
    path = r'D:\新建文件夹\express-analysis\express_data.json'
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    for c in results:
        print('=== {} ==='.format(c['city']))
        print('  网点: {}, 密度: {:.4f}, 最近邻: {:.2f}km'.format(c['total_points'], c['density_per_km2'], c['avg_nnd_km']))
        print('  标准差椭圆: {}km x {}km, 角度: {}°'.format(c['std_ellipse']['x_std_km'], c['std_ellipse']['y_std_km'], c['std_ellipse']['angle_deg']))
        print('  高密度区: {}%, 低密度区: {}%'.format(c['kde']['high_density_ratio'], c['kde']['low_density_ratio']))
        if c['blind_spots']:
            print('  盲区: {}'.format(', '.join([b['district'] for b in c['blind_spots']])))
        else:
            print('  盲区: 无')
    print('\n保存完成!')


if __name__ == '__main__':
    main()
