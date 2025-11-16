from pydantic import BaseModel
from typing import Optional
from datetime import date

class cropInput(BaseModel):
    crop:Optional[str]=None
    sowing_date: date
    n: Optional[float]=None
    p: Optional[float]=None
    k: Optional[float]=None