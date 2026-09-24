from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, Field, field_validator, model_validator
from pulse.services.query import parse_query


class TimeRange(BaseModel):
    start: datetime
    end: datetime

    @model_validator(mode="after")
    def valid(self):
        if self.start.tzinfo is None or self.end.tzinfo is None or self.start >= self.end:
            raise ValueError("Time range must have UTC offsets and start before end")
        if self.end > datetime.now(timezone.utc) + timedelta(minutes=1):
            raise ValueError("Future end times are unsupported")
        return self


class SearchCreate(BaseModel):
    query: str = Field(min_length=1, max_length=256)
    platforms: list[str] = Field(min_length=1, max_length=3)
    time_range: TimeRange | None = None
    language: str = Field(default="en", description="Language of supported analysis; provider discovery may include other languages")
    allow_partial_sources: bool = True
    max_items_per_source: int = Field(default=50, ge=10, le=50)

    @field_validator("query")
    @classmethod
    def query_valid(cls, value):
        parse_query(value)
        return value

    @field_validator("platforms")
    @classmethod
    def platforms_valid(cls, value):
        if len(set(value)) != len(value) or any(v not in ("x", "youtube", "reddit") for v in value):
            raise ValueError("Platforms must be unique values from x, youtube, reddit")
        return value

    @field_validator("language")
    @classmethod
    def language_valid(cls, value):
        if value != "en":
            raise ValueError("Only English analysis is supported")
        return value


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    terms: list[str] = Field(min_length=1, max_length=20)

    @field_validator("terms")
    @classmethod
    def terms_valid(cls, value):
        if any(not 1 <= len(t.strip()) <= 80 for t in value):
            raise ValueError("Each category term must be 1–80 characters")
        return value
