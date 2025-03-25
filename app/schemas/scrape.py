from pydantic import BaseModel

class ScrapeResonse(BaseModel):
    year: str = "" # 年份 '2024'
    province: str = "" # 招生省份 '江苏'
    type: str = "" # 类型 '普通类, 高校专项'
    academic_category: str = "" # 科类 '历史+不限'
    major_name: str = "" # 专业名称 '会计学'
    admission_score: str = "" # 投档分 '600'
    highest_score: str = "" # 最高分 '700'
    minimum_score: str = "" # 最低分 '500'
    ranking: str = "" # 排名 '200000名次'