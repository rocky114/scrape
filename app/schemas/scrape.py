from pydantic import BaseModel

class ScrapeResonse(BaseModel):
    year: str = "" # 年份 '2024'
    province: str = "" # 招生省份 '江苏'
    admission_type: str = "" # 类型 '普通类, 高校专项'
    academic_category: str = "" # 科类 '历史+不限'
    major_name: str = "" # 专业名称 '会计学'
    enrollment_quota: str = "" # 招生人数
    admission_batch: str = "" # 批次
    min_admission_score: str = "" # 投档分 '600'
    min_admission_rank: str = "" # 排名 '200000名次'
    highest_score: str = "" # 最高分 '700'
    highest_score_rank: str = "" # 排名 '200000名次'
    lowest_score: str = "" # 最低分 '500'
    lowest_score_rank: str = "" # 排名 '200000名次'

class ScrapeRequest(BaseModel):
    year: str = "2024" # 年份 '2024'
    province: str = "江苏" # 招生省份 '江苏'
    admission_type: str = "普通类" # 类型 '普通类, 高校专项'