import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field


class ProfileBase(BaseModel):
    display_name: str | None = Field(default=None, max_length=100)
    avatar_url: str | None = Field(default=None, max_length=1000)
    professional_title: str | None = Field(default=None, max_length=150)


class ProfileUpdate(ProfileBase):
    onboarding_completed: bool | None = None


class ProfileResponse(ProfileBase):
    id: uuid.UUID
    email: EmailStr
    onboarding_completed: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
