# map_tools.py (V6.1 - 终极健壮与可视化版)

import requests
import json
import folium
from typing import Optional, List, Dict
from langchain.tools import tool
from config import AMAP_API_KEY, AMAP_BASE_URL


# search_place_info 工具函数保持不变，它工作得很好
@tool
def search_place_info(place_name: str, city: str) -> Optional[str]:
    """
    【铁律1: 必须最先调用】此工具用于精确查找任何地点的官方名称、地址和经纬度坐标('location')。
    在进行任何路线规划之前，必须对用户提到的每一个地点（包括景点、酒店、餐厅、车站）都使用此工具。
    后续的路线规划工具严重依赖此工具返回的'location'值。

    例如:
    - 输入: place_name="东方明珠", city="上海"
    - 返回: 包含精确"location"的JSON字符串。
    """
    # (此函数代码与您之前的版本完全相同，无需修改)
    print(f"--- 🛠️ 调用工具 [search_place_info]: 在'{city}'搜索'{place_name}' ---")
    url = f"{AMAP_BASE_URL}/assistant/inputtips"
    params = {'key': AMAP_API_KEY, 'keywords': place_name, 'city': city, 'datatype': 'poi'}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if data['status'] == '1' and data.get('tips'):
            best_tip = data['tips'][0]
            if isinstance(best_tip.get('location'), str) and ',' in best_tip['location']:
                result = {"name": best_tip.get("name", place_name), "location": best_tip.get("location"),
                          "address": best_tip.get("address", "") if isinstance(best_tip.get("address"),
                                                                               str) else best_tip.get('district', '')}
                result_str = json.dumps(result, ensure_ascii=False)
                print(f"--- ✅ [search_place_info] 成功: '{place_name}' -> {result_str} ---")
                return result_str
        print(f"--- ⚠️ [search_place_info] 警告: 无法为'{place_name}'找到有效坐标。---")
        return None
    except Exception as e:
        print(f"--- ❌ [search_place_info] 错误: {e} ---")
        return None


# --- 【核心修正】get_route_info 函数 ---
@tool
def get_route_info(origin: str, destination: str, city: str, mode: str = 'transit') -> Optional[str]:
    """
    【铁律2: 必须在获取坐标后调用】此工具用于计算两个地点之间的实际交通路线。
    严禁直接使用地名作为'origin'或'destination'参数，必须使用`search_place_info`工具返回的"经度,纬度"格式的'location'值。
    在规划行程中，只要涉及从A点到B点的移动，就必须调用此工具获取真实的交通数据。

    例如:
    - 输入: origin="121.4997,31.2397", destination="121.5063,31.2451", city="上海", mode="transit"
    - 返回: 一个包含详细交通步骤('steps')的JSON字符串。
    """
    print(f"--- 🛠️ 调用工具 [get_route_info-v3]: 从 {origin} 到 {destination} by {mode} in {city} ---")

    if mode == 'transit':
        url = f"{AMAP_BASE_URL}/direction/transit/integrated"
        params = {'key': AMAP_API_KEY, 'origin': origin, 'destination': destination, 'city': city}
    elif mode in ['walking', 'driving']:
        api_path = 'walking' if mode == 'walking' else 'driving'
        url = f"{AMAP_BASE_URL}/direction/{api_path}"
        params = {'key': AMAP_API_KEY, 'origin': origin, 'destination': destination}
    else:
        return f"错误: 不支持的交通方式 '{mode}'。"

    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()

        if data.get('status') == '1' and 'route' in data:
            result = {}
            # --- 处理公交/地铁(transit)的详细逻辑 ---
            if mode == 'transit' and data['route'].get('transits'):
                plan = data['route']['transits'][0]

                # --- 更健壮的步骤和polyline提取逻辑 ---
                steps_description = []
                polyline_parts = []

                for segment in plan.get('segments', []):
                    # 步行部分
                    walking = segment.get('walking', {})
                    if walking and walking.get('distance') and int(walking['distance']) > 0:
                        steps_description.append(
                            f"步行约{int(walking.get('duration', 0)) // 60}分钟 ({walking.get('distance')}米)")
                        if walking.get('polyline'):
                            polyline_parts.append(walking['polyline'])

                    # 公交部分
                    bus = segment.get('bus', {})
                    if bus and bus.get('buslines'):
                        # buslines 是一个列表，需要安全地处理
                        for busline in bus.get('buslines', []):
                            steps_description.append(
                                f"在「{busline.get('departure_stop', {}).get('name', '')}」站乘坐「{busline.get('name', '')}」，经过{busline.get('via_num', 0)}站后，在「{busline.get('arrival_stop', {}).get('name', '')}」站下车")
                            if busline.get('polyline'):
                                polyline_parts.append(busline['polyline'])

                result = {
                    "duration_minutes": int(plan.get('duration', 0)) // 60,
                    "distance_meters": int(plan.get('distance', 0)),
                    "cost_yuan": float(plan.get('cost', 0)),
                    "steps": steps_description,
                    "polyline": ";".join(polyline_parts)
                }

            # --- 处理步行(walking)或驾车(driving)的逻辑 ---
            elif mode in ['walking', 'driving'] and data['route'].get('paths'):
                path = data['route']['paths'][0]

                # 安全地拼接所有步骤的polyline
                polyline_parts = [step.get('polyline') for step in path.get('steps', []) if step.get('polyline')]

                result = {
                    "duration_minutes": int(path.get('duration', 0)) // 60,
                    "distance_meters": int(path.get('distance', 0)),
                    "polyline": ";".join(polyline_parts)
                }

            if result:
                result_str = json.dumps(result, ensure_ascii=False)
                print(f"--- ✅ [get_route_info] 成功: 返回了包含polyline的数据 ---")
                return result_str

        print(f"--- ⚠️ [get_route_info] 警告: 无法规划路线。高德返回: {data.get('info', '')} ---")
        return None
    except Exception as e:
        import traceback
        traceback.print_exc()  # 打印详细的错误堆栈信息
        print(f"--- ❌ [get_route_info] 错误: {e} ---")
        return None


# generate_map_visualization 工具函数保持不变
@tool
def generate_map_visualization(daily_plans: str) -> str:
    """【可视化工具】... (文档字符串与之前版本相同)"""
    # (此函数代码与V6.0版本完全相同，无需修改)
    print(f"--- 🛠️ 调用工具 [generate_map_visualization]: 正在生成地图... ---")
    try:
        list_of_days = json.loads(daily_plans)
        if not list_of_days: return "错误: 没有路线数据，无法生成地图。"
        first_spot_loc_str = list_of_days[0]['spots'][0]['location']
        lng, lat = map(float, first_spot_loc_str.split(','))
        map_center = [lat, lng]
        m = folium.Map(location=map_center, zoom_start=12,
                       tiles='https://webrd01.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}',
                       attr='高德地图')
        colors = ['blue', 'green', 'purple', 'orange', 'darkred', 'lightred', 'beige']
        for i, day_plan in enumerate(list_of_days):
            color = colors[i % len(colors)]
            for spot in day_plan['spots']:
                lng, lat = map(float, spot['location'].split(','))
                folium.Marker(location=[lat, lng], popup=f"<strong>{spot['name']}</strong><br>Day {day_plan['day']}",
                              tooltip=spot['name'], icon=folium.Icon(color=color, icon='flag')).add_to(m)
            for route in day_plan.get('routes', []):
                if route and route.get('polyline'):
                    points = [p.split(',') for p in route['polyline'].split(';') if p]
                    lat_lng_points = [[float(p[1]), float(p[0])] for p in points if len(p) == 2]
                    if lat_lng_points:
                        folium.PolyLine(locations=lat_lng_points, color=color, weight=5, opacity=0.8).add_to(m)
        map_filename = "trip_map.html"
        m.save(map_filename)
        print(f"--- ✅ [generate_map_visualization] 成功: 地图已保存至 {map_filename} ---")
        return f"地图已成功生成，并保存为 {map_filename} 文件。请在浏览器中打开它查看。"
    except Exception as e:
        import traceback
        traceback.print_exc()
        print(f"--- ❌ [generate_map_visualization] 错误: {e} ---")
        return f"生成地图时发生错误: {e}"


# --- 测试代码保持不变 ---
if __name__ == '__main__':
    # (测试代码与V6.0版本完全相同，无需修改)
    print("--- 正在独立测试 map_tools.py (V6.1) ---")
    print("\n--- 1&2. 测试地点搜索和路线规划 (大连) ---")
    xinghai_info_str = search_place_info.invoke({"place_name": "星海广场", "city": "大连"})
    laohutan_info_str = search_place_info.invoke({"place_name": "老虎滩海洋公园", "city": "大连"})
    route_str = None
    if xinghai_info_str and laohutan_info_str:
        xinghai_loc = json.loads(xinghai_info_str)['location']
        laohutan_loc = json.loads(laohutan_info_str)['location']
        route_str = get_route_info.invoke(
            {"origin": xinghai_loc, "destination": laohutan_loc, "mode": "transit", "city": "大连"})
    print("\n--- 3. 测试地图生成 ---")
    if xinghai_info_str and laohutan_info_str and route_str:
        mock_daily_plans = [{"day": 1, "spots": [json.loads(xinghai_info_str), json.loads(laohutan_info_str)],
                             "routes": [json.loads(route_str)]}]
        map_result = generate_map_visualization.invoke(json.dumps(mock_daily_plans))
        print(f"地图生成结果: {map_result}")
    else:
        print("因前面的步骤失败，跳过地图生成测试。")