import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.resume_version import ResumeVersionResponse


class ResumeCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    target_role: str | None = Field(default=None, max_length=150)
    # Optional initial version data
    input_source: str | None = Field(default=None, pattern="^(FILE_UPLOAD|URL_IMPORT|DIRECT_TEXT)$")
    resume_file_id: uuid.UUID | None = None
    source_url: str | None = Field(default=None, max_length=1000)
    raw_text: str | None = Field(default=None, max_length=5000)


class ResumeUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    target_role: str | None = Field(default=None, max_length=150)


class ResumeListItem(BaseModel):
    id: uuid.UUID
    title: str
    target_role: str | None
    current_version_id: uuid.UUID | None
    version_count: int = 1
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeDetailResponse(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    title: str
    target_role: str | None
    current_version_id: uuid.UUID | None
    current_version: ResumeVersionResponse | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class UploadUrlRequest(BaseModel):
    filename: str = Field(min_length=1, max_length=255)
    mime_type: str = Field(pattern="^(application/pdf|application/vnd.openxmlformats-officedocument.wordprocessingml.document)$")
    file_size_bytes: int = Field(gt=0, le=10485760)  # Max 10MB


class UploadUrlResponse(BaseModel):
    upload_url: str
    storage_path: str
    resume_file_id: uuid.UUID
