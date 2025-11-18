"""Pydantic schemas for AnalysisProject API endpoints."""
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator
import uuid

from omega_analysis.models.analysis import ProjectStatus, ValidationStatus, SystemType


class AnalysisProjectBase(BaseModel):
    """Base schema for AnalysisProject."""
    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    repository_url: str = Field(..., min_length=1, max_length=512, description="Repository URL")
    repository_branch: str = Field(default="main", max_length=128, description="Repository branch")
    target_system_type: SystemType = Field(..., description="Target system type")
    analysis_configuration: Dict[str, Any] = Field(default_factory=dict, description="Analysis configuration")
    created_by: str = Field(..., min_length=1, max_length=128, description="Created by user")
    validation_notes: Optional[str] = Field(None, description="Validation notes")

    @validator('repository_url')
    def validate_repository_url(cls, v):
        """Validate repository URL format."""
        # Basic validation - could be enhanced with regex for specific Git providers
        if not v.startswith(('http://', 'https://', 'git@')):
            raise ValueError('Repository URL must start with http://, https://, or git@')
        return v

    @validator('analysis_configuration')
    def validate_analysis_configuration(cls, v):
        """Validate analysis configuration structure."""
        # Basic validation - ensure it's a valid dict
        if not isinstance(v, dict):
            raise ValueError('Analysis configuration must be a dictionary')
        return v


class AnalysisProjectCreate(AnalysisProjectBase):
    """Schema for creating a new AnalysisProject."""
    pass


class AnalysisProjectUpdate(BaseModel):
    """Schema for updating an existing AnalysisProject."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    repository_url: Optional[str] = Field(None, min_length=1, max_length=512)
    repository_branch: Optional[str] = Field(None, max_length=128)
    target_system_type: Optional[SystemType] = None
    analysis_configuration: Optional[Dict[str, Any]] = None
    status: Optional[ProjectStatus] = None
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)
    validation_status: Optional[ValidationStatus] = None
    validation_notes: Optional[str] = None

    @validator('repository_url')
    def validate_repository_url(cls, v):
        """Validate repository URL format."""
        if v is not None and not v.startswith(('http://', 'https://', 'git@')):
            raise ValueError('Repository URL must start with http://, https://, or git@')
        return v


class AnalysisProjectResponse(AnalysisProjectBase):
    """Schema for AnalysisProject responses."""
    id: uuid.UUID
    status: ProjectStatus
    progress_percentage: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]
    validation_status: ValidationStatus

    class Config:
        from_attributes = True


class AnalysisProjectListResponse(BaseModel):
    """Schema for paginated AnalysisProject list responses."""
    items: List[AnalysisProjectResponse]
    total: int
    page: int
    size: int
    pages: int


class AnalysisProjectFilters(BaseModel):
    """Schema for AnalysisProject query filters."""
    status: Optional[ProjectStatus] = None
    target_system_type: Optional[SystemType] = None
    validation_status: Optional[ValidationStatus] = None
    created_by: Optional[str] = None
    name_contains: Optional[str] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None