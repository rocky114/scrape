from pydantic import BaseModel

class ScrapeResonse(BaseModel):
    year: str = "" # 年份 '2024'
    province: str = "" # 招生省份 '江苏'
    university_name: str = "" # 学校名称
    admission_batch: str = "" # 录取批次
    admission_type: str = "" # 类型 '普通类, 高校专项'
    admission_region: str = "" # 定向区域
    subject_category: str = "" # 科类 '历史+不限'
    major_name: str = "" # 专业名称 '会计学'
    major_group: str = "" # 专业组
    highest_score: str = "" # 最高分 '700'
    highest_score_rank: str = "" # 排名 '200000名次'
    lowest_score: str = "" # 最低分 '500'
    lowest_score_rank: str = "" # 排名 '200000名次'

class ScrapeRequest(BaseModel):
    url: str # 录取分数地址
    year: str = "2024" # 年份 '2024'
    province: str = "江苏" # 招生省份 '江苏'
    admission_type: str = "普通类" # 类型 '普通类, 高校专项'
    university_name: str