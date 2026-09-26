from typing import Literal
from pydantic import BaseModel, ConfigDict, field_validator


class ChartRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    gender: Literal["男", "女", "1", "2"]
    birth_datetime: str
    query_datetime: str

    @field_validator("birth_datetime", "query_datetime")
    @classmethod
    def check_length(cls, value):
        if len(value) != 16 or value[4] != "-" or value[7] != "-" or value[10] != " " or value[13] != ":":
            raise ValueError("日期时间应为 YYYY-MM-DD HH:MM")
        return value
