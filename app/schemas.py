from typing import Literal
from pydantic import BaseModel, Field

class ActionRequest(BaseModel):
    action: Literal["HOLD", "RELEASE"]
    reason: str = Field(min_length=3, max_length=500)

class ActionResponse(BaseModel):
    request_id: int
    request_number: str
    status: str
    message: str
