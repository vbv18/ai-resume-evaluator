import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.ai_contracts import JobDescriptionData


class JDVersionResponse(BaseModel):
    id: uuid.UUID
    job_description_id: uuid.UUID
    version_number: int
    input_source: str
    source_url: str | None
    raw_text: str
    structured_data: JobDescriptionData
    parsing_metadata: dict
    change_summary: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JDCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    company_name: str | None = Field(default=None, max_length=150)
    input_source: str = Field(pattern="^(FILE_UPLOAD|URL_IMPORT|DIRECT_TEXT)$")
    source_url: str | None = Field(default=None, max_length=1000)
    raw_text: str = Field(min_length=20, max_length=5000)


class JDUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    company_name: str | None = Field(default=None, max_length=150)


class JDListItem(BaseModel):
    id: uuid.UUID
    title: str
    company_name: str | None
    current_version_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JDDetailResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    company_name: str | None
    current_version_id: uuid.UUID | None
    current_version: JDVersionResponse | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
