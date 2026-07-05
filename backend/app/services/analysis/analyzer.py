import re
from app.schemas.analysis import AnalyzeResponse, DimensionScore

EMOTION_WORDS = {
    "positive": ["治愈","温暖","感动","美好","幸福","喜欢","爱了","绝了","惊艳","太好","值得","推荐","宝藏","神仙","爆款","必备","回购","惊喜","舒服","高级","精致","上手","种草","安利","超赞","真香","完美"],
    "empathetic": ["焦虑","烦恼","困扰","崩溃","踩雷","劝退","失望","后悔","尴尬","无奈","心累","哭了","卑微","翻车","同款","谁懂"],
    "anxious": ["紧急","限时","限量","最后","赶紧","错过","涨价","手慢无","库存告急","倒计时","秒杀"],
    "trust": ["实测","亲测","测评","体验","试用","开箱","对比","正品","官方","认证","成分","数据","报告"]
}

def _extract_title(text):
    lines = [l.strip() for l in text.split("\n") if l.strip()]
    return lines[0] if lines else text[:20]

def _has_emoji(t):
    import re
    return bool(re.compile("[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF\U0001F1E0-\U0001F1FF\U00002702-\U000027B0\U000024C2-\U0001F251]").search(t))

def _has_numbers(t):
    return bool(re.search(r"\d+", t))

def _has_question(t):
    return "?" in t or "？" in t

def _has_exclamation(t):
    return "!" in t or "！" in t

def _analyze_title(text, track):
    title = _extract_title(text) or text[:30]
    score = 40
    missing = []
    items = []
    if len(title) < 5:
        missing.append({"name":"标题过短","value":"仅"+str(len(title))+"字"})
    else:
        score += 10 if len(title) >= 15 else 5
        items.append({"name":"标题长度","value":str(len(title))+"字"})
    if _has_numbers(title):
        score += 8
        items.append({"name":"含数字","value":"增强可信度"})
    else:
        missing.append({"name":"缺少数字","value":"数字能提升点击率"})
    if _has_emoji(title):
        score += 6
        items.append({"name":"含emoji","value":"提升视觉吸引力"})
    else:
        missing.append({"name":"缺少emoji","value":"emoji可提升点击率"})
    if _has_question(title):
        score += 7
        items.append({"name":"使用问句","value":"引发好奇"})
    else:
        missing.append({"name":"建议用问句","value":"问句开头更吸引点击"})
    hook_words = ["如何","怎么","揭秘","干货","攻略","教程","指南","保姆级","私藏","小众","清单","必看"]
    if any(h in title for h in hook_words):
        score += 8
        items.append({"name":"含钩子词","value":"提升打开率"})
    else:
        missing.append({"name":"缺少钩子词","value":"如干货、攻略等"})
    score = min(99, max(20, score))
    if score >= 85:
        comment = "标题吸引力强，包含有效的钩子和情绪触发点"
    elif score >= 70:
        comment = "标题基本合格，建议增加数字/问句/emoji进一步提升"
    elif score >= 50:
        comment = "标题偏弱，缺少吸引读者的关键要素"
    else:
        comment = "标题需要重写，长度和内容均不足以吸引注意"
    return {"score":score,"items":items,"missing":missing,"comment":comment}

def _analyze_emotion(text, track):
    score = 30
    found = {k:[] for k in EMOTION_WORDS}
    for cat, words in EMOTION_WORDS.items():
        for w in words:
            if w in text:
                found[cat].append(w)
    total = sum(len(v) for v in found.values())
    elements = []
    missing = []
    if total == 0:
        missing.append({"name":"缺少情绪词","value":"建议增加感性表达"})
    else:
        score += min(total * 5, 25)
        if found["positive"]:
            elements.append({"name":"正向词","value":"、".join(found["positive"][:5])})
        if found["empathetic"]:
            elements.append({"name":"共情词","value":"、".join(found["empathetic"][:5])})
        if found["anxious"]:
            elements.append({"name":"焦虑词","value":"、".join(found["anxious"][:3])})
        if found["trust"]:
            elements.append({"name":"信任词","value":"、".join(found["trust"][:3])})
    if track in ("xiaohongshu","local_tourism") and len(found["empathetic"]) < 2:
        missing.append({"name":"共情不足","value":"需要更多共情表达"})
    if track == "ecommerce" and len(found["trust"]) < 2:
        missing.append({"name":"信任感不足","value":"建议增加实测、测评等词"})
    if track == "short_video" and len(found["anxious"]) < 1:
        missing.append({"name":"紧迫感不足","value":"短视频需要紧迫感钩子"})
    if _has_exclamation(text):
        score += 5
    if _has_question(text):
        score += 5
    if track == "xiaohongshu":
        score += 5
    score = min(99, max(20, score))
    if score >= 80:
        comment = "情感表达丰富，能引起目标用户的情绪共鸣"
    elif score >= 60:
        comment = "有一定情感色彩，建议增加共情或焦虑词提升感染力"
    else:
        comment = "情绪表达较弱，文案偏理性干涩，建议加入感性词汇"
    return {"score":score,"elements":elements,"positive":found["positive"],"empathetic":found["empathetic"],"missing":missing,"comment":comment}

def _analyze_structure(text, track):
    score = 30
    paras = [p.strip() for p in text.split("\n") if p.strip()]
    char_count = len(text)
    elements = []
    missing = []
    if len(paras) == 0:
        missing.append({"name":"无分段","value":"建议分段"})
    elif len(paras) == 1:
        elements.append({"name":"单段落","value":str(char_count)+"字"})
        missing.append({"name":"建议分段","value":"建议3-5段"})
        score += 10
    elif len(paras) <= 3:
        score += 18
        elements.append({"name":"段落数","value":str(len(paras))+"段"})
    elif len(paras) <= 7:
        score += 25
        elements.append({"name":"段落合理","value":str(len(paras))+"段"})
    else:
        score += 20
        elements.append({"name":"段落偏多","value":str(len(paras))+"段"})
    sentences = len(re.findall(r"[。！？.!?]", text))
    if sentences < 3:
        missing.append({"name":"句式单调","value":"缺少句尾标点"})
    else:
        elements.append({"name":"句式变化","value":str(sentences)+"个句尾"})
        score += 5
    cta_words = ["试试","入手","收藏","关注","点赞","分享","评论","链接"]
    if any(w in text for w in cta_words):
        elements.append({"name":"有行动号召","value":"引导互动"})
        score += 8
    else:
        missing.append({"name":"缺少行动号召","value":"建议加引导语"})
    if track == "xiaohongshu" and not _has_emoji(text):
        missing.append({"name":"缺少emoji","value":"每个段落可以配emoji"})
    if track == "ecommerce":
        if not any(w in text for w in cta_words):
            missing.append({"name":"缺少促单","value":"需要购买引导"})
    score = min(99, max(20, score))
    comment = "结构清晰" if score>=80 else "结构基本完整" if score>=60 else "结构松散"
    return {"score":score,"elements":elements,"missing":missing,"comment":comment}

def _analyze_audience(text, track):
    score = 35
    elements = []
    missing = []
    char_count = len(text)
    if char_count < 50:
        missing.append({"name":"内容过短","value":"信息量不足"})
    elif char_count < 200:
        score += 15
        elements.append({"name":"短文风格","value":str(char_count)+"字"})
    elif char_count < 800:
        score += 20
        elements.append({"name":"适中长度","value":str(char_count)+"字"})
    else:
        score += 18
        elements.append({"name":"长文","value":str(char_count)+"字"})
    track_keywords = {
        "xiaohongshu": ["种草","安利","测评","好物","宝藏","小众","私藏","推荐","分享"],
        "ecommerce": ["下单","购买","优惠","包邮","品质","正品","售后","价格"],
        "local_tourism": ["景点","打卡","攻略","民宿","路线","风景","旅行"],
        "short_video": ["关注","点赞","评论区","教程","步骤","结果"]
    }
    keywords = track_keywords.get(track, [])
    found_keywords = [w for w in keywords if w in text]
    if found_keywords:
        elements.append({"name":"赛道关键词","value":"、".join(found_keywords[:4])})
        score += min(len(found_keywords)*4, 20)
    else:
        missing.append({"name":"缺少赛道词","value":"未检测到"+str(track)+"典型词汇"})
    audience_words = ["姐妹们","宝宝们","朋友们","亲们","集美","打工人","学生党","宝妈"]
    if any(w in text for w in audience_words):
        elements.append({"name":"人群指向","value":"明确受众"})
        score += 8
    else:
        missing.append({"name":"缺人群指向","value":"建议定位受众"})
    score = min(99, max(20, score))
    if score >= 80:
        comment = "与"+str(track)+"赛道匹配度高"
    elif score >= 60:
        comment = "与"+str(track)+"赛道基本匹配"
    else:
        comment = "匹配度较低，建议调整语言风格"
    return {"score":score,"elements":elements,"missing":missing,"comment":comment}

def _generate_suggestions(text, track, scores):
    title = _extract_title(text) or text[:15]
    suggestions = {"titles":[],"paragraphs":[],"emotions":[],"structure":[]}
    if scores.get("title",0) < 80:
        suggestions["titles"].append({"rewrite":title[:12]+"？这3个细节告诉你答案"})
        suggestions["titles"].append({"rewrite":"后悔没早看！"+title[:10]+"的满分攻略"})
        suggestions["titles"].append({"rewrite":title[:10]+"！建议收藏"})
    paras = [p.strip() for p in text.split("\n") if p.strip()]
    if len(paras) <= 2:
        suggestions["paragraphs"].append({"pos":"开头","suggestion":"首段抛出痛点或问题，吸引读者继续阅读","detail":"用问句或数据开头"})
        suggestions["paragraphs"].append({"pos":"中段","suggestion":"增加分点论述，每点配一个案例或数据","detail":"使用第一/第二/第三结构"})
        suggestions["paragraphs"].append({"pos":"结尾","suggestion":"加入行动号召，引导读者互动","detail":"如评论区告诉我你的想法"})
    if scores.get("emotion",0) < 70:
        suggestions["emotions"].append({"word":"治愈/温暖","reason":"增强情感共鸣，适合小红书/文旅赛道"})
        suggestions["emotions"].append({"word":"后悔/踩雷","reason":"利用焦虑心理提升打开率"})
        suggestions["emotions"].append({"word":"实测/亲测","reason":"增加信任感，适合电商评测"})
    if scores.get("structure",0) < 70:
        suggestions["structure"].append({"original":"当前结构","new":"先抛痛点->给出解决方案->列举卖点->行动号召","reason":"经典营销结构转化率最高"})
    return suggestions

def analyze_text(text, track):
    title_r = _analyze_title(text, track)
    emotion_r = _analyze_emotion(text, track)
    structure_r = _analyze_structure(text, track)
    audience_r = _analyze_audience(text, track)
    w_map = {"xiaohongshu":(0.25,0.30,0.20,0.25),"ecommerce":(0.20,0.20,0.30,0.30),"local_tourism":(0.25,0.25,0.25,0.25),"short_video":(0.30,0.25,0.25,0.20)}
    w = w_map.get(track, (0.25,0.25,0.25,0.25))
    overall = round(title_r["score"]*w[0] + emotion_r["score"]*w[1] + structure_r["score"]*w[2] + audience_r["score"]*w[3])
    def g(s):
        return "S" if s>=85 else "A" if s>=70 else "B" if s>=50 else "C"
    dims = [
        DimensionScore(id="title",name="标题吸引力",score=title_r["score"],grade=g(title_r["score"]),conclusion=title_r["comment"],elements=title_r["missing"]+title_r.get("items",[])),
        DimensionScore(id="emotion",name="情绪共鸣",score=emotion_r["score"],grade=g(emotion_r["score"]),conclusion=emotion_r["comment"],elements=emotion_r["elements"]+[{"name":"缺失","value":m["name"]} for m in emotion_r["missing"]]),
        DimensionScore(id="structure",name="结构逻辑",score=structure_r["score"],grade=g(structure_r["score"]),conclusion=structure_r["comment"],elements=structure_r["elements"]+[{"name":"缺失","value":m["name"]} for m in structure_r["missing"]]),
        DimensionScore(id="audience",name="人群匹配",score=audience_r["score"],grade=g(audience_r["score"]),conclusion=audience_r["comment"],elements=audience_r["elements"]+[{"name":"缺失","value":m["name"]} for m in audience_r["missing"]]),
    ]
    sugg = _generate_suggestions(text,track,{"title":title_r["score"],"emotion":emotion_r["score"],"structure":structure_r["score"],"audience":audience_r["score"]})
    analysis_raw = {
        "title_analysis":{"score":title_r["score"],"comment":title_r["comment"]},
        "emotion_analysis":{"score":emotion_r["score"],"comment":emotion_r["comment"],"empathy_words":emotion_r.get("empathetic",[]),"anxiety_words":[]},
        "structure_analysis":{"score":structure_r["score"],"comment":structure_r["comment"]},
        "audience_analysis":{"score":audience_r["score"],"comment":audience_r["comment"]},
        "overall_scoring":{"overall_score":overall,"overall_grade":g(overall)},
        "suggestions":[{"type":"title","content":s["rewrite"]} for s in sugg["titles"]]+[{"type":"structure","content":s["suggestion"]} for s in sugg["paragraphs"]]+[{"type":"emotion","content":s["word"]+": "+s["reason"]} for s in sugg["emotions"]]+([{"type":"structure","content":s["new"]} for s in sugg["structure"]] if sugg["structure"] else [])
    }
    return AnalyzeResponse(overall_score=overall,overall_grade=g(overall),dimensions=dims,analysis_raw=analysis_raw)
