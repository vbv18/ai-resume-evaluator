import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.ai_contracts import ResumeData


class ResumeVersionCreate(BaseModel):
    input_source: str = Field(pattern="^(FILE_UPLOAD|URL_IMPORT|DIRECT_TEXT)$")
    resume_file_id: uuid.UUID | None = None
    source_url: str | None = Field(default=None, max_length=1000)
    raw_text: str | None = Field(default=None, max_length=5000)
    change_summary: str | None = Field(default=None, max_length=500)


class ResumeVersionResponse(BaseModel):
    id: uuid.UUID
    resume_id: uuid.UUID
    version_number: int
    input_source: str
    resume_file_id: uuid.UUID | None
    source_url: str | None
    raw_text: str
    structured_data: ResumeData
    parsing_metadata: dict
    change_summary: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeVersionSummary(BaseModel):
    id: uuid.UUID
    version_number: int
    input_source: str
    change_summary: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
