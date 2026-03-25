from __future__ import annotations

from dataclasses import dataclass

from pydantic import BaseModel, ConfigDict, Field


class SummaryOutput(BaseModel):
    model_config = ConfigDict(extra="ignore")

    title: str = Field(default="")
    summary: str = Field(default="")
    keyPoints: list[str] = Field(default_factory=list)
    actionItems: list[str] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)


@dataclass(frozen=True)
class ExtractedContent:
    title: str
    text: str


@dataclass(frozen=True)
class PipelineResult:
    summary: SummaryOutput
    source_url: str
    final_url: str
    extracted_title: str
    raw_text_chars: int
    truncated_chars: int
    language: str
