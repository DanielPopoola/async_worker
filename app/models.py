from pydantic import BaseModel, Field, field_validator
from typing import Any
import json


class JobCreateRequest(BaseModel):
    payload: dict[str, Any] = Field(..., description="Job payload as a dictionary")

    @field_validator('payload')
    @classmethod
    def validate_payload(cls, v: dict):
        try:
            json.dumps(v)
        except (TypeError, ValueError):
            raise ValueError("Payload must be JSON serializable.")
        
        if len(json.dumps(v)) > 1024 * 1024:
            raise ValueError("Payload to large (max 1MB)")
        
        return v
    

class JobCreateResponse(BaseModel):
    job_id: str
    status: str ='queued'

class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    attempt_count: int
    payload: dict[str, Any]