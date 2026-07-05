from fastapi import APIRouter, Depends, HTTPException
from app.schemas.analysis import AnalyzeRequest, AnalyzeResponse, DimensionScore
from app.utils.string_utils import is_blank, is_pure_symbols
from datetime import datetime
import random
router = APIRouter()
@router.post("/api/v1/analyze")
async def analyze_text(req: AnalyzeRequest):
    text = req.original_text.strip()
    if is_blank(text) or is_pure_symbols(text):
        raise HTTPException(status_code=400, detail={"code": 400, "message": "invalid text"})
    if len(text) > 5000:
        raise HTTPException(status_code=413, detail={"code": 413, "message": "text too long"})
    base_score = {"xiaohongshu":82,"ecommerce":78,"local_tourism":85,"short_video":75}.get(req.track_type,75)
    overall = max(30, min(99, base_score + random.randint(-5,8)))
    overall_grade = "S" if overall>=85 else "A" if overall>=70 else "B" if overall>=50 else "C"
    dim_configs = [("title","title"),("emotion","emotion"),("structure","structure"),("audience","audience")]
    dims = []
    for i,(dim_id,dim_name) in enumerate(dim_configs):
        s = max(30, min(99, base_score + random.randint(-15,10) + i*3))
        g = "S" if s>=85 else "A" if s>=70 else "B" if s>=50 else "C"
        dims.append(DimensionScore(id=dim_id, name=dim_name, score=s, grade=g, conclusion="ok"))
    id_val = int(datetime.now().timestamp()*1000) % 10000000
    analysis_raw = {
        "title_analysis":{"score":dims[0].score,"comment":dims[0].conclusion},
        "emotion_analysis":{"score":dims[1].score,"comment":dims[1].conclusion,"empathy_words":["warm"],"anxiety_words":[]},
        "structure_analysis":{"score":dims[2].score,"comment":dims[2].conclusion},
        "audience_analysis":{"score":dims[3].score,"comment":dims[3].conclusion},
        "overall_scoring":{"overall_score":overall,"overall_grade":overall_grade},
        "suggestions":[
            {"type":"title","content":"suggestion 1"},
            {"type":"title","content":"suggestion 2"},
            {"type":"title","content":"suggestion 3"},
            {"type":"structure","content":"restructure"},
            {"type":"emotion","content":"add emotion"},
        ]
    }
    result = AnalyzeResponse(id=id_val,overall_score=overall,overall_grade=overall_grade,word_count=len(text),dimensions=dims,analysis_raw=analysis_raw)
    return {"code":0,"message":"success","data":result.model_dump()}
from fastapi import APIRouter, Depends, HTTPException
from app.schemas.analysis import AnalyzeRequest, AnalyzeResponse, DimensionScore
from app.services.analysis.analyzer import analyze_text as do_analyze
from app.utils.string_utils import is_blank
from datetime import datetime

router = APIRouter()

@router.post("/api/v1/analyze")
async def analyze_text(req: AnalyzeRequest):
    text = req.original_text.strip()
    if is_blank(text):
        raise HTTPException(status_code=400, detail={"code": 400, "message": "请输入有效的文案内容"})
    if len(text) > 5000:
        raise HTTPException(status_code=413, detail={"code": 413, "message": "文案超过5000字上限，请分段提交"})

    result = do_analyze(text, req.track_type)
    result.id = int(datetime.now().timestamp() * 1000) % 10000000
    result.word_count = len(text)

    return {"code": 0, "message": "success", "data": result.model_dump()}
