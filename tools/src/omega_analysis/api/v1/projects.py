"""FastAPI router for AnalysisProject CRUD operations."""
from datetime import datetime
from typing import Optional, List
from uuid import UUID
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import selectinload

from omega_analysis.models.base import get_db_session
from omega_analysis.models.analysis import AnalysisProject, ProjectStatus, SystemType, ValidationStatus
from omega_analysis.api.v1.schemas import (
    AnalysisProjectCreate,
    AnalysisProjectUpdate,
    AnalysisProjectResponse,
    AnalysisProjectListResponse,
    AnalysisProjectFilters
)
from omega_analysis.auth.middleware import require_scopes

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/",
    response_model=AnalysisProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new analysis project",
    description="Create a new analysis project with the provided configuration"
)
async def create_analysis_project(
    project_data: AnalysisProjectCreate,
    db: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(require_scopes("projects:write"))
):
    """Create a new analysis project."""
    try:
        # Create new project instance
        project = AnalysisProject(
            name=project_data.name,
            description=project_data.description,
            repository_url=project_data.repository_url,
            repository_branch=project_data.repository_branch,
            target_system_type=project_data.target_system_type,
            analysis_configuration=project_data.analysis_configuration,
            created_by=project_data.created_by,
            validation_notes=project_data.validation_notes,
            status=ProjectStatus.QUEUED,
            progress_percentage=0,
            validation_status=ValidationStatus.PENDING
        )

        # Add to database
        db.add(project)
        await db.commit()
        await db.refresh(project)

        logger.info(f"Created analysis project: {project.id}", extra={
            "project_id": str(project.id),
            "name": project.name,
            "created_by": project.created_by
        })

        return project

    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to create analysis project: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create analysis project"
        )


@router.get(
    "/",
    response_model=AnalysisProjectListResponse,
    summary="List analysis projects",
    description="Retrieve a paginated list of analysis projects with optional filtering"
)
async def list_analysis_projects(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    status_filter: Optional[ProjectStatus] = Query(None, description="Filter by project status"),
    system_type: Optional[SystemType] = Query(None, description="Filter by target system type"),
    validation_status: Optional[ValidationStatus] = Query(None, description="Filter by validation status"),
    created_by: Optional[str] = Query(None, description="Filter by creator"),
    name_contains: Optional[str] = Query(None, description="Filter by name containing text"),
    created_after: Optional[datetime] = Query(None, description="Filter by creation date after"),
    created_before: Optional[datetime] = Query(None, description="Filter by creation date before"),
    db: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(require_scopes("projects:read"))
):
    """List analysis projects with pagination and filtering."""
    try:
        # Build base query
        query = select(AnalysisProject)
        count_query = select(func.count(AnalysisProject.id))

        # Apply filters
        conditions = []
        
        if status_filter:
            conditions.append(AnalysisProject.status == status_filter)
        
        if system_type:
            conditions.append(AnalysisProject.target_system_type == system_type)
        
        if validation_status:
            conditions.append(AnalysisProject.validation_status == validation_status)
        
        if created_by:
            conditions.append(AnalysisProject.created_by == created_by)
        
        if name_contains:
            conditions.append(AnalysisProject.name.ilike(f"%{name_contains}%"))
        
        if created_after:
            conditions.append(AnalysisProject.created_at >= created_after)
        
        if created_before:
            conditions.append(AnalysisProject.created_at <= created_before)

        # Apply conditions if any
        if conditions:
            query = query.where(and_(*conditions))
            count_query = count_query.where(and_(*conditions))

        # Get total count
        total_result = await db.execute(count_query)
        total = total_result.scalar()

        # Apply pagination and ordering
        query = query.order_by(AnalysisProject.created_at.desc())
        query = query.offset((page - 1) * size).limit(size)

        # Execute query
        result = await db.execute(query)
        projects = result.scalars().all()

        # Calculate pagination info
        pages = (total + size - 1) // size  # Ceiling division

        logger.info(f"Listed {len(projects)} analysis projects", extra={
            "page": page,
            "size": size,
            "total": total,
            "filters_applied": bool(conditions)
        })

        return AnalysisProjectListResponse(
            items=projects,
            total=total,
            page=page,
            size=size,
            pages=pages
        )

    except Exception as e:
        logger.error(f"Failed to list analysis projects: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analysis projects"
        )


@router.get(
    "/{project_id}",
    response_model=AnalysisProjectResponse,
    summary="Get analysis project by ID",
    description="Retrieve a specific analysis project by its UUID"
)
async def get_analysis_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(require_scopes("projects:read"))
):
    """Get a specific analysis project by ID."""
    try:
        # Query with relationships if needed
        query = select(AnalysisProject).where(AnalysisProject.id == project_id)
        result = await db.execute(query)
        project = result.scalar_one_or_none()

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis project {project_id} not found"
            )

        logger.info(f"Retrieved analysis project: {project_id}")
        return project

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get analysis project {project_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve analysis project"
        )


@router.put(
    "/{project_id}",
    response_model=AnalysisProjectResponse,
    summary="Update analysis project",
    description="Update an existing analysis project with the provided data"
)
async def update_analysis_project(
    project_id: UUID,
    project_update: AnalysisProjectUpdate,
    db: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(require_scopes("projects:write"))
):
    """Update an existing analysis project."""
    try:
        # Get existing project
        query = select(AnalysisProject).where(AnalysisProject.id == project_id)
        result = await db.execute(query)
        project = result.scalar_one_or_none()

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis project {project_id} not found"
            )

        # Update fields that are provided
        update_data = project_update.dict(exclude_unset=True, exclude_none=True)
        
        for field, value in update_data.items():
            setattr(project, field, value)

        # Update timestamp
        project.updated_at = datetime.utcnow()

        # Mark as completed if status changed to completed
        if hasattr(project_update, 'status') and project_update.status == ProjectStatus.COMPLETED and not project.completed_at:
            project.completed_at = datetime.utcnow()
            project.progress_percentage = 100

        await db.commit()
        await db.refresh(project)

        logger.info(f"Updated analysis project: {project_id}", extra={
            "project_id": str(project_id),
            "updated_fields": list(update_data.keys())
        })

        return project

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to update analysis project {project_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update analysis project"
        )


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete analysis project",
    description="Delete an analysis project and all associated data"
)
async def delete_analysis_project(
    project_id: UUID,
    db: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(require_scopes("projects:delete"))
):
    """Delete an analysis project."""
    try:
        # Get existing project
        query = select(AnalysisProject).where(AnalysisProject.id == project_id)
        result = await db.execute(query)
        project = result.scalar_one_or_none()

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis project {project_id} not found"
            )

        # Delete project (cascade will handle related entities)
        await db.delete(project)
        await db.commit()

        logger.info(f"Deleted analysis project: {project_id}", extra={
            "project_id": str(project_id),
            "name": project.name
        })

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to delete analysis project {project_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete analysis project"
        )


@router.post(
    "/{project_id}/validate",
    response_model=AnalysisProjectResponse,
    summary="Validate analysis project",
    description="Update the validation status and notes for an analysis project"
)
async def validate_analysis_project(
    project_id: UUID,
    validation_status: ValidationStatus,
    validation_notes: Optional[str] = None,
    db: AsyncSession = Depends(get_db_session),
    current_user: dict = Depends(require_scopes("projects:validate"))
):
    """Update validation status for an analysis project."""
    try:
        # Get existing project
        query = select(AnalysisProject).where(AnalysisProject.id == project_id)
        result = await db.execute(query)
        project = result.scalar_one_or_none()

        if not project:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis project {project_id} not found"
            )

        # Update validation fields
        project.validation_status = validation_status
        if validation_notes is not None:
            project.validation_notes = validation_notes
        project.updated_at = datetime.utcnow()

        await db.commit()
        await db.refresh(project)

        logger.info(f"Validated analysis project: {project_id}", extra={
            "project_id": str(project_id),
            "validation_status": validation_status.value,
            "validator": current_user.get("sub", "unknown")
        })

        return project

    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to validate analysis project {project_id}: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to validate analysis project"
        )