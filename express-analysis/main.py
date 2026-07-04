import json, os, re, math
from pathlib import Path
import httpx
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from loguru import logger

app = FastAPI(title="CopyMind - 快递网点运营分析")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

DATA_PATH = Path(__file__).parent / "express_data.json"
with open(DATA_PATH, "r", encoding="utf-8") as f:
    RAW_DATA = json.load(f)

AI_API_KEY = os.getenv("AI_API_KEY")
if not AI_API_KEY:
    env_path = Path(__file__).parent.parent / "backend" / ".env"
    if env_path.exists():
        for line in env_path.read_text("utf-8").splitlines():
            if line.strip().startswith("AI_API_KEY="):
                AI_API_KEY = line.split("=", 1)[1].strip()

@app.get("/", response_class=HTMLResponse)
async def index():
    html_path = Path(__file__).parent / "templates" / "index.html"
    return HTMLResponse(html_path.read_text("utf-8"))

@app.get("/api/provinces")
async def list_provinces():
    seen = set()
    result = []
    for c in RAW_DATA["cities"]:
        p = c.get("province", "")
        if p and p not in seen:
            seen.add(p)
            cities_in_prov = [x for x in RAW_DATA["cities"] if x.get("province", "") == p]
            district_count = sum(x.get("districts_count", 0) for x in cities_in_prov)
            result.append({"province": p, "city_count": len(cities_in_prov), "district_count": district_count})
    return result

@app.get("/api/cities")
async def list_cities(province: str = None):
    if province:
        return [c for c in RAW_DATA["cities"] if c.get("province", "") == province]
    return RAW_DATA["cities"]

@app.get("/api/analyze")
async def analyze_city(city: str = Query(...)):
    city_data = None
    for c in RAW_DATA["cities"]:
        if c["city"] == city:
            city_data = c
            break
    if not city_data:
        return {"error": "not found"}
    ai_report = await call_ai(city_data)
    return {"city_data": city_data, "ai_report": ai_report}

async def call_ai(city_data: dict) -> dict:
    if not AI_API_KEY:
        return {"error": "no api key"}
    city = city_data["city"]
    e = city_data.get("std_ellipse", {})
    k = city_data.get("kde", {})
    dd = city_data.get("district_densities", [])
    bs = city_data.get("blind_spots", [])

    # === Compute scores from actual data ===

    # 1. Layout score: based on distribution efficiency
    nnd = city_data.get("avg_nnd_km", 0)
    std_dist = city_data.get("std_distance_km", 0) or 1
    # Expected NND under uniform: 0.5 / sqrt(density)
    dens = max(city_data.get("density_per_km2", 0), 0.0001)
    # More concentrated (smaller std vs area) + higher nnd = better layout
    area = max(city_data.get("area_km2", 0), 1)
    std_ratio = min(std_dist / (math.sqrt(area / math.pi) + 1), 2)
    layout_raw = max(0, min(100, 100 * (1 - std_ratio * 0.3 + min(nnd, 5) * 0.08)))
    layout_score = round(layout_raw)

    # 2. Traffic match: directly from traffic_advantage
    traffic = city_data.get("traffic_advantage", 0)
    traffic_match_score = round(min(100, max(0, traffic * 100 + 10)))

    # 3. Balance score: based on density uniformity across districts
    if len(dd) > 1:
        densities = [x["density"] for x in dd if x.get("density", 0) > 0]
        if len(densities) > 1:
            mean_d = sum(densities) / len(densities) or 1
            std_d = (sum((d - mean_d)**2 for d in densities) / len(densities))**0.5
            cv = std_d / mean_d  # coefficient of variation
            # Lower CV = more balanced
            balance_raw = max(0, min(100, 100 * (1 - min(cv, 3) * 0.3)))
        else:
            balance_raw = 50
    else:
        balance_raw = 100  # single district = perfectly balanced

    # Blind spot penalty
    blind_penalty = min(len(bs) * 5, 40)
    balance_score = round(max(0, balance_raw - blind_penalty))

    # 4. Overall score
    overall_score = round(layout_score * 0.35 + traffic_match_score * 0.35 + balance_score * 0.30)

    # 5. Grade
    if overall_score >= 85:
        overall_grade = "A"
    elif overall_score >= 70:
        overall_grade = "B"
    elif overall_score >= 55:
        overall_grade = "C"
    else:
        overall_grade = "D"

    # === AI for qualitative text only ===
    blind = ", ".join([b["district"] + "(" + b["reason"] + ")" for b in bs]) or "无"
    dden = ", ".join(["{}:{}个/km2".format(x["name"], x["density"]) for x in dd[:5]])
    prompt = "分析" + city + "的快递网点布局。"
    prompt += "数据：网点{}个, 密度{:.4f}个/km2, 最近邻距离{}km, 高密度区{}%低密度区{}%, 盲区{}, 交通优势度{:.4f}。".format(
        city_data["total_points"], dens, nnd,
        k.get("high_density_ratio", 0), k.get("low_density_ratio", 0),
        blind, traffic)
    prompt += "评分：布局合理性{}分, 交通匹配度{}分, 覆盖均衡性{}分, 综合{}分, 等级{}. ".format(
        layout_score, traffic_match_score, balance_score, overall_score, overall_grade)
    prompt += '输出JSON格式：{{"summary":"一句话评价(30字内)","problems":["2-3个具体问题"],"suggestions":["2-3条优化建议"],"site_recommendations":[{{"location":"选址1","reason":"理由"}},{{"location":"选址2","reason":"理由"}}]}}只输出JSON。'

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post("https://api.deepseek.com/chat/completions",
                headers={"Authorization": "Bearer " + AI_API_KEY, "Content-Type": "application/json"},
                json={"model": "deepseek-chat", "messages": [{"role": "user", "content": prompt}], "temperature": 0.5, "max_tokens": 1500})
            resp.raise_for_status()
            c = resp.json()["choices"][0]["message"]["content"]
            match = re.search(r'\{.*\}', c, re.DOTALL)
            ai_part = json.loads(match.group()) if match else {"summary": "", "problems": [], "suggestions": [], "site_recommendations": []}
    except Exception as e:
        logger.error("AI failed: " + str(e))
        ai_part = {"summary": "", "problems": ["AI分析暂不可用"], "suggestions": [], "site_recommendations": []}

    return {
        "layout_score": layout_score,
        "traffic_match_score": traffic_match_score,
        "balance_score": balance_score,
        "overall_score": overall_score,
        "overall_grade": overall_grade,
        "summary": ai_part.get("summary", ""),
        "problems": ai_part.get("problems", []),
        "suggestions": ai_part.get("suggestions", []),
        "site_recommendations": ai_part.get("site_recommendations", [])
    }



@app.get("/api/map-china")
async def map_china():
    map_path = Path(__file__).parent / "china_map.json"
    with open(map_path, "r", encoding="utf-8") as f:
        return json.loads(f.read())



@app.get("/api/geojson/{city}")
async def get_geojson(city: str):
    # First try static GeoJSON file
    mapping = {
        "西宁市": "xining_geo.json",
        "海东市": "haidong_geo.json",
        "贵阳市": "guiyang_geo.json",
        "六盘水市": "liupanshui_geo.json",
        "遵义市": "zunyi_geo.json",
        "安顺市": "anshun_geo.json",
        "毕节市": "bijie_geo.json",
        "铜仁市": "tongren_geo.json",
        "海口市": "haikou_geo.json",
        "三亚市": "sanya_geo.json",
        "儋州市": "danzhou_geo.json",
        "拉萨市": "lasa_geo.json",
        "日喀则市": "rikaze_geo.json",
        "昌都市": "changdu_geo.json",
        "林芝市": "linzhi_geo.json",
        "山南市": "shannan_geo.json",
        "那曲市": "naqu_geo.json",
        "乌鲁木齐市": "wulumuqi_geo.json",
        "克拉玛依市": "kelamayi_geo.json",
        "吐鲁番市": "tulufan_geo.json",
        "哈密市": "hami_geo.json",
        "银川市": "yinchuan_geo.json",
        "石嘴山市": "shizuishan_geo.json",
        "吴忠市": "wuzhong_geo.json",
        "固原市": "guyuan_geo.json",
        "中卫市": "zhongwei_geo.json",
        "上海市": "shanghai_geo.json",
        "重庆市": "chongqing_geo.json",
        "北京市": "beijing_geo.json",
        "天津市": "tianjin_geo.json",
        "福州市": "fuzhou_geo.json",
        "厦门市": "xiamen_geo.json",
        "莆田市": "putian_geo.json",
        "三明市": "sanming_geo.json",
        "泉州市": "quanzhou_geo.json",
        "漳州市": "zhangzhou_geo.json",
        "南平市": "nanping_geo.json",
        "龙岩市": "longyan_geo.json",
        "宁德市": "ningde_geo.json",
        "济南市": "jinan_geo.json",
        "青岛市": "qingdao_geo.json",
        "淄博市": "zibo_geo.json",
        "枣庄市": "zaozhuang_geo.json",
        "东营市": "dongying_geo.json",
        "烟台市": "yantai_geo.json",
        "潍坊市": "weifang_geo.json",
        "济宁市": "jining_geo.json",
        "泰安市": "taian_geo.json",
        "威海市": "weihai_geo.json",
        "日照市": "rizhao_geo.json",
        "临沂市": "linyi_geo.json",
        "德州市": "dezhou_geo.json",
        "聊城市": "liaocheng_geo.json",
        "滨州市": "binzhou_geo.json",
        "菏泽市": "heze_geo.json",
        "长沙市": "changsha_geo.json",
        "株洲市": "zhuzhou_geo.json",
        "湘潭市": "xiangtan_geo.json",
        "衡阳市": "hengyang_geo.json",
        "邵阳市": "shaoyang_geo.json",
        "岳阳市": "yueyang_geo.json",
        "常德市": "changde_geo.json",
        "张家界市": "zhangjiajie_geo.json",
        "益阳市": "yiyang_geo.json",
        "郴州市": "chenzhou_geo.json",
        "永州市": "yongzhou_geo.json",
        "怀化市": "huaihua_geo.json",
        "娄底市": "loudi_geo.json",
        "杭州市": "hangzhou_geo.json",
        "宁波市": "ningbo_geo.json",
        "温州市": "wenzhou_geo.json",
        "嘉兴市": "jiaxing_geo.json",
        "湖州市": "huzhou_geo.json",
        "绍兴市": "shaoxing_geo.json",
        "金华市": "jinhua_geo.json",
        "衢州市": "quzhou_geo.json",
        "舟山市": "zhoushan_geo.json",
        "台州市": "taizhou_geo.json",
        "丽水市": "lishui_geo.json",
        "南京市": "nanjing_geo.json",
        "无锡市": "wuxi_geo.json",
        "徐州市": "xuzhou_geo.json",
        "常州市": "changzhou_geo.json",
        "苏州市": "suzhou_geo.json",
        "南通市": "nantong_geo.json",
        "连云港市": "lianyungang_geo.json",
        "淮安市": "huaian_geo.json",
        "盐城市": "yancheng_geo.json",
        "扬州市": "yangzhou_geo.json",
        "镇江市": "zhenjiang_geo.json",
        "泰州市": "taizhou_js_geo.json",
        "宿迁市": "suqian_geo.json",
        "广州市": "guangzhou_geo.json",
        "韶关市": "shaoguan_geo.json",
        "深圳市": "shenzhen_geo.json",
        "珠海市": "zhuhai_geo.json",
        "汕头市": "shantou_geo.json",
        "佛山市": "foshan_geo.json",
        "江门市": "jiangmen_geo.json",
        "湛江市": "zhanjiang_geo.json",
        "茂名市": "maoming_geo.json",
        "肇庆市": "zhaoqing_geo.json",
        "惠州市": "huizhou_geo.json",
        "梅州市": "meizhou_geo.json",
        "汕尾市": "shanwei_geo.json",
        "河源市": "heyuan_geo.json",
        "阳江市": "yangjiang_geo.json",
        "清远市": "qingyuan_geo.json",
        "东莞市": "dongguan_geo.json",
        "中山市": "zhongshan_geo.json",
        "潮州市": "chaozhou_geo.json",
        "揭阳市": "jieyang_geo.json",
        "云浮市": "yunfu_geo.json",
        "哈尔滨市": "haerbin_geo.json",
        "齐齐哈尔市": "qiqi_geo.json",
        "鸡西市": "jixi_geo.json",
        "鹤岗市": "hegang_geo.json",
        "双鸭山市": "shuangyashan_geo.json",
        "大庆市": "daqing_geo.json",
        "伊春市": "yichun_geo.json",
        "佳木斯市": "jiamusi_geo.json",
        "七台河市": "qitaihe_geo.json",
        "牡丹江市": "mudanjiang_geo.json",
        "黑河市": "heihe_geo.json",
        "绥化市": "suihua_geo.json",
        "长春市": "changchun_geo.json",
        "吉林市": "jilin_geo.json",
        "四平市": "siping_geo.json",
        "辽源市": "liaoyuan_geo.json",
        "通化市": "tonghua_geo.json",
        "白山市": "baishan_geo.json",
        "松原市": "songyuan_geo.json",
        "白城市": "baicheng_geo.json",
        "沈阳市": "shenyang_geo.json",
        "大连市": "dalian_geo.json",
        "鞍山市": "anshan_geo.json",
        "抚顺市": "fushun_geo.json",
        "本溪市": "benxi_geo.json",
        "丹东市": "dandong_geo.json",
        "锦州市": "jinzhou_geo.json",
        "营口市": "yingkou_geo.json",
        "阜新市": "fuxin_geo.json",
        "辽阳市": "liaoyang_geo.json",
        "盘锦市": "panjin_geo.json",
        "铁岭市": "tieling_geo.json",
        "朝阳市": "chaoyang_geo.json",
        "葫芦岛市": "huludao_geo.json",
        "呼和浩特市": "hohhot_geo.json",
        "包头市": "baotou_geo.json",
        "乌海市": "wuhai_geo.json",
        "赤峰市": "chifeng_geo.json",
        "通辽市": "tongliao_geo.json",
        "鄂尔多斯市": "ordos_geo.json",
        "呼伦贝尔市": "hulunbuir_geo.json",
        "巴彦淖尔市": "bayannur_geo.json",
        "乌兰察布市": "ulanqab_geo.json",
        "兰州市": "lanzhou_geo.json",
        "嘉峪关市": "jiayuguan_geo.json",
        "金昌市": "jinchang_geo.json",
        "白银市": "baiyin_geo.json",
        "天水市": "tianshui_geo.json",
        "武威市": "wuwei_geo.json",
        "张掖市": "zhangye_geo.json",
        "平凉市": "pingliang_geo.json",
        "酒泉市": "jiuquan_geo.json",
        "庆阳市": "qingyang_geo.json",
        "定西市": "dingxi_geo.json",
        "陇南市": "longnan_geo.json",
        "合肥市": "hefei_geo.json",
        "芜湖市": "wuhu_geo.json",
        "蚌埠市": "bengbu_geo.json",
        "淮南市": "huainan_geo.json",
        "马鞍山市": "maanshan_geo.json",
        "淮北市": "huaibei_geo.json",
        "铜陵市": "tongling_geo.json",
        "安庆市": "anqing_geo.json",
        "黄山市": "huangshan_geo.json",
        "滁州市": "chuzhou_geo.json",
        "阜阳市": "fuyang_geo.json",
        "宿州市": "suzhou_ah_geo.json",
        "六安市": "luan_geo.json",
        "亳州市": "bozhou_geo.json",
        "池州市": "chizhou_geo.json",
        "宣城市": "xuancheng_geo.json",
        "郑州市": "zhengzhou_geo.json",
        "开封市": "kaifeng_geo.json",
        "洛阳市": "luoyang_geo.json",
        "平顶山市": "pingdingshan_geo.json",
        "安阳市": "anyang_geo.json",
        "鹤壁市": "hebi_geo.json",
        "新乡市": "xinxiang_geo.json",
        "焦作市": "jiaozuo_geo.json",
        "濮阳市": "puyang_geo.json",
        "许昌市": "xuchang_geo.json",
        "漯河市": "luohe_geo.json",
        "三门峡市": "sanmenxia_geo.json",
        "南阳市": "nanyang_geo.json",
        "商丘市": "shangqiu_geo.json",
        "信阳市": "xinyang_geo.json",
        "周口市": "zhoukou_geo.json",
        "驻马店市": "zhumadian_geo.json",
        "济源市": "jiyuan_geo.json",
        "武汉市": "wuhan_geo.json",
        "黄石市": "huangshi_geo.json",
        "十堰市": "shiyan_geo.json",
        "宜昌市": "yichang_geo.json",
        "襄阳市": "xiangyang_geo.json",
        "鄂州市": "ezhou_geo.json",
        "荆门市": "jingmen_geo.json",
        "孝感市": "xiaogan_geo.json",
        "荆州市": "jingzhou_geo.json",
        "黄冈市": "huanggang_geo.json",
        "咸宁市": "xianning_geo.json",
        "随州市": "suizhou_geo.json",
        "仙桃市": "xiantao_geo.json",
        "天门市": "tianmen_geo.json",
        "潜江市": "qianjiang_geo.json",
        "石家庄市": "shijiazhuang_geo.json",
        "唐山市": "tangshan_geo.json",
        "秦皇岛市": "qinhuangdao_geo.json",
        "邯郸市": "handan_geo.json",
        "邢台市": "xingtai_geo.json",
        "保定市": "baoding_geo.json",
        "张家口市": "zhangjiakou_geo.json",
        "承德市": "chengde_geo.json",
        "沧州市": "cangzhou_geo.json",
        "廊坊市": "langfang_geo.json",
        "衡水市": "hengshui_geo.json",
        "南宁市": "nanning_geo.json",
        "柳州市": "liuzhou_geo.json",
        "桂林市": "guilin_geo.json",
        "梧州市": "wuzhou_geo.json",
        "北海市": "beihai_geo.json",
        "防城港市": "fangchenggang_geo.json",
        "钦州市": "qinzhou_geo.json",
        "贵港市": "guigang_geo.json",
        "玉林市": "yulin_geo.json",
        "百色市": "baise_geo.json",
        "贺州市": "hezhou_geo.json",
        "河池市": "hechi_geo.json",
        "来宾市": "laibin_geo.json",
        "崇左市": "chongzuo_geo.json",
        "南昌市": "nanchang_geo.json",
        "景德镇市": "jingdezhen_geo.json",
        "萍乡市": "pingxiang_geo.json",
        "九江市": "jiujiang_geo.json",
        "新余市": "xinyu_geo.json",
        "鹰潭市": "yingtan_geo.json",
        "赣州市": "ganzhou_geo.json",
        "吉安市": "jian_geo.json",
        "宜春市": "yichun_jx_geo.json",
        "抚州市": "fuzhou_jx_geo.json",
        "上饶市": "shangrao_geo.json",
        "太原市": "taiyuan_geo.json",
        "大同市": "datong_geo.json",
        "阳泉市": "yangquan_geo.json",
        "长治市": "changzhi_geo.json",
        "晋城市": "jincheng_geo.json",
        "朔州市": "shuozhou_geo.json",
        "晋中市": "jinzhong_geo.json",
        "运城市": "yuncheng_geo.json",
        "忻州市": "xinzhou_geo.json",
        "临汾市": "linfen_geo.json",
        "吕梁市": "lvliang_geo.json",
        "西安市": "xian_geo.json",
        "铜川市": "tongchuan_geo.json",
        "宝鸡市": "baoji_geo.json",
        "咸阳市": "xianyang_geo.json",
        "渭南市": "weinan_geo.json",
        "延安市": "yanan_geo.json",
        "汉中市": "hanzhong_geo.json",
        "榆林市": "yulin_sx_geo.json",
        "安康市": "ankang_geo.json",
        "商洛市": "shangluo_geo.json",
        "成都市": "chengdu_geo.json",
        "自贡市": "zigong_geo.json",
        "攀枝花市": "panzhihua_geo.json",
        "泸州市": "luzhou_geo.json",
        "德阳市": "deyang_geo.json",
        "绵阳市": "mianyang_geo.json",
        "广元市": "guangyuan_geo.json",
        "遂宁市": "suining_geo.json",
        "内江市": "neijiang_geo.json",
        "乐山市": "leshan_geo.json",
        "南充市": "nanchong_geo.json",
        "眉山市": "meishan_geo.json",
        "宜宾市": "yibin_geo.json",
        "广安市": "guangan_geo.json",
        "达州市": "dazhou_geo.json",
        "雅安市": "yaan_geo.json",
        "巴中市": "bazhong_geo.json",
        "资阳市": "ziyang_geo.json",
        "昆明市": "kunming_geo.json",
        "曲靖市": "qujing_geo.json",
        "玉溪市": "yuxi_geo.json",
        "保山市": "baoshan_geo.json",
        "昭通市": "zhaotong_geo.json",
        "丽江市": "lijiang_geo.json",
        "普洱市": "puer_geo.json",
        "临沧市": "lincang_geo.json"
    }
    filename = mapping.get(city)
    if filename:
        path = Path(__file__).parent / filename
        if path.exists():
            with open(path, "r", encoding="utf-8") as f:
                return json.loads(f.read())

    # Fallback: generate GeoJSON from district bounds in data
    city_data = None
    for c in RAW_DATA["cities"]:
        if c["city"] == city:
            city_data = c
            break
    if not city_data:
        return {"error": "not found"}

    features = []
    dd_list = city_data.get("district_densities", [])
    for dd in dd_list:
        bounds = dd.get("bounds")
        if not bounds:
            continue
        min_lng = bounds["min_lng"]
        max_lng = bounds["max_lng"]
        min_lat = bounds["min_lat"]
        max_lat = bounds["max_lat"]
        # Create a box polygon
        polygon = [[
            [min_lng, min_lat],
            [max_lng, min_lat],
            [max_lng, max_lat],
            [min_lng, max_lat],
            [min_lng, min_lat]
        ]]
        features.append({
            "type": "Feature",
            "properties": {"name": dd["name"], "adcode": 0, "level": "district"},
            "geometry": {"type": "Polygon", "coordinates": polygon}
        })
    return {"type": "FeatureCollection", "features": features}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
