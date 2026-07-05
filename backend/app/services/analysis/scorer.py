def calculate_grade(score: float) -> str:
    if score >= 85: return "S"
    if score >= 70: return "A"
    if score >= 50: return "B"
    return "C"
def calculate_overall(scores: dict) -> float:
    w = {"title":0.25,"emotion":0.25,"structure":0.25,"audience":0.25}
    return round(sum(scores.get(k,0)*v for k,v in w.items()), 1)
