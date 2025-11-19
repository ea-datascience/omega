"""
Progress Tracker for Analysis Workflows.

Tracks detailed progress of analysis execution through multiple phases,
providing real-time status updates, phase transitions, and completion estimates.
"""

import logging
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

logger = logging.getLogger(__name__)


class AnalysisPhase(Enum):
    """Analysis workflow phases."""
    INITIALIZING = "initializing"
    STATIC_ANALYSIS = "static_analysis"
    RUNTIME_ANALYSIS = "runtime_analysis"
    GAP_ANALYSIS = "gap_analysis"
    RESULT_AGGREGATION = "result_aggregation"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PhaseStatus(Enum):
    """Status of individual phase."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


class ProgressTracker:
    """
    Tracks analysis progress through multiple phases.
    
    Responsibilities:
    - Track current phase and overall progress percentage
    - Maintain phase transition history
    - Calculate estimated completion time
    - Provide detailed status for each phase
    - Track sub-tasks within phases
    """
    
    # Phase weights for progress calculation (must sum to 1.0)
    PHASE_WEIGHTS = {
        AnalysisPhase.INITIALIZING: 0.05,
        AnalysisPhase.STATIC_ANALYSIS: 0.35,
        AnalysisPhase.RUNTIME_ANALYSIS: 0.30,
        AnalysisPhase.GAP_ANALYSIS: 0.20,
        AnalysisPhase.RESULT_AGGREGATION: 0.10,
    }
    
    def __init__(self, analysis_id: UUID, project_id: UUID):
        """
        Initialize progress tracker for an analysis.
        
        Args:
            analysis_id: UUID of the analysis
            project_id: UUID of the project being analyzed
        """
        self.analysis_id = analysis_id
        self.project_id = project_id
        self.started_at = datetime.utcnow()
        self.completed_at: Optional[datetime] = None
        self.current_phase = AnalysisPhase.INITIALIZING
        
        # Phase tracking
        self.phase_status: Dict[AnalysisPhase, PhaseStatus] = {
            phase: PhaseStatus.PENDING
            for phase in AnalysisPhase
            if phase not in [AnalysisPhase.COMPLETED, AnalysisPhase.FAILED, AnalysisPhase.CANCELLED]
        }
        self.phase_progress: Dict[AnalysisPhase, float] = {
            phase: 0.0
            for phase in AnalysisPhase
            if phase not in [AnalysisPhase.COMPLETED, AnalysisPhase.FAILED, AnalysisPhase.CANCELLED]
        }
        self.phase_start_times: Dict[AnalysisPhase, Optional[datetime]] = {
            phase: None
            for phase in AnalysisPhase
            if phase not in [AnalysisPhase.COMPLETED, AnalysisPhase.FAILED, AnalysisPhase.CANCELLED]
        }
        self.phase_end_times: Dict[AnalysisPhase, Optional[datetime]] = {
            phase: None
            for phase in AnalysisPhase
            if phase not in [AnalysisPhase.COMPLETED, AnalysisPhase.FAILED, AnalysisPhase.CANCELLED]
        }
        
        # Sub-task tracking within phases
        self.phase_subtasks: Dict[AnalysisPhase, List[Dict[str, Any]]] = {
            phase: []
            for phase in AnalysisPhase
            if phase not in [AnalysisPhase.COMPLETED, AnalysisPhase.FAILED, AnalysisPhase.CANCELLED]
        }
        
        # Error tracking
        self.errors: List[Dict[str, Any]] = []
        self.warnings: List[Dict[str, Any]] = []
        
        logger.info(f"Progress tracker initialized for analysis {analysis_id}")
    
    def start_phase(self, phase: AnalysisPhase) -> None:
        """
        Mark a phase as started.
        
        Args:
            phase: The phase to start
        """
        if phase in [AnalysisPhase.COMPLETED, AnalysisPhase.FAILED, AnalysisPhase.CANCELLED]:
            logger.warning(f"Cannot start terminal phase {phase.value}")
            return
        
        logger.info(f"Starting phase {phase.value} for analysis {self.analysis_id}")
        self.current_phase = phase
        self.phase_status[phase] = PhaseStatus.IN_PROGRESS
        self.phase_start_times[phase] = datetime.utcnow()
        self.phase_progress[phase] = 0.0
    
    def complete_phase(self, phase: AnalysisPhase) -> None:
        """
        Mark a phase as completed.
        
        Args:
            phase: The phase to complete
        """
        if phase in [AnalysisPhase.COMPLETED, AnalysisPhase.FAILED, AnalysisPhase.CANCELLED]:
            logger.warning(f"Cannot complete terminal phase {phase.value}")
            return
        
        logger.info(f"Completing phase {phase.value} for analysis {self.analysis_id}")
        self.phase_status[phase] = PhaseStatus.COMPLETED
        self.phase_progress[phase] = 100.0
        self.phase_end_times[phase] = datetime.utcnow()
    
    def fail_phase(self, phase: AnalysisPhase, error_message: str) -> None:
        """
        Mark a phase as failed.
        
        Args:
            phase: The phase that failed
            error_message: Description of the failure
        """
        if phase in [AnalysisPhase.COMPLETED, AnalysisPhase.FAILED, AnalysisPhase.CANCELLED]:
            logger.warning(f"Cannot fail terminal phase {phase.value}")
            return
        
        logger.error(f"Phase {phase.value} failed for analysis {self.analysis_id}: {error_message}")
        self.phase_status[phase] = PhaseStatus.FAILED
        self.phase_end_times[phase] = datetime.utcnow()
        self.add_error(phase.value, error_message)
    
    def skip_phase(self, phase: AnalysisPhase, reason: str) -> None:
        """
        Mark a phase as skipped.
        
        Args:
            phase: The phase to skip
            reason: Reason for skipping
        """
        if phase in [AnalysisPhase.COMPLETED, AnalysisPhase.FAILED, AnalysisPhase.CANCELLED]:
            logger.warning(f"Cannot skip terminal phase {phase.value}")
            return
        
        logger.info(f"Skipping phase {phase.value} for analysis {self.analysis_id}: {reason}")
        self.phase_status[phase] = PhaseStatus.SKIPPED
        self.phase_progress[phase] = 0.0
    
    def update_phase_progress(self, phase: AnalysisPhase, progress: float) -> None:
        """
        Update progress for a specific phase.
        
        Args:
            phase: The phase to update
            progress: Progress percentage (0-100)
        """
        if phase in [AnalysisPhase.COMPLETED, AnalysisPhase.FAILED, AnalysisPhase.CANCELLED]:
            logger.warning(f"Cannot update progress for terminal phase {phase.value}")
            return
        
        progress = max(0.0, min(100.0, progress))
        self.phase_progress[phase] = progress
        logger.debug(f"Phase {phase.value} progress: {progress}%")
    
    def add_subtask(
        self,
        phase: AnalysisPhase,
        task_name: str,
        task_description: Optional[str] = None
    ) -> int:
        """
        Add a sub-task to a phase.
        
        Args:
            phase: The phase this task belongs to
            task_name: Name of the sub-task
            task_description: Optional description
        
        Returns:
            Index of the added sub-task
        """
        if phase in [AnalysisPhase.COMPLETED, AnalysisPhase.FAILED, AnalysisPhase.CANCELLED]:
            logger.warning(f"Cannot add subtask to terminal phase {phase.value}")
            return -1
        
        subtask = {
            "name": task_name,
            "description": task_description,
            "status": "pending",
            "started_at": None,
            "completed_at": None,
            "progress": 0.0
        }
        self.phase_subtasks[phase].append(subtask)
        return len(self.phase_subtasks[phase]) - 1
    
    def update_subtask(
        self,
        phase: AnalysisPhase,
        task_index: int,
        status: Optional[str] = None,
        progress: Optional[float] = None
    ) -> None:
        """
        Update a sub-task's status or progress.
        
        Args:
            phase: The phase the task belongs to
            task_index: Index of the task
            status: New status (pending, in_progress, completed, failed)
            progress: New progress percentage
        """
        if phase not in self.phase_subtasks or task_index >= len(self.phase_subtasks[phase]):
            logger.warning(f"Invalid subtask index {task_index} for phase {phase.value}")
            return
        
        subtask = self.phase_subtasks[phase][task_index]
        
        if status is not None:
            subtask["status"] = status
            if status == "in_progress" and subtask["started_at"] is None:
                subtask["started_at"] = datetime.utcnow()
            elif status in ["completed", "failed"]:
                subtask["completed_at"] = datetime.utcnow()
        
        if progress is not None:
            subtask["progress"] = max(0.0, min(100.0, progress))
    
    def add_error(self, context: str, message: str) -> None:
        """
        Add an error to the tracker.
        
        Args:
            context: Context where error occurred (phase name, etc.)
            message: Error message
        """
        error = {
            "timestamp": datetime.utcnow().isoformat(),
            "context": context,
            "message": message
        }
        self.errors.append(error)
        logger.error(f"Error in {context}: {message}")
    
    def add_warning(self, context: str, message: str) -> None:
        """
        Add a warning to the tracker.
        
        Args:
            context: Context where warning occurred
            message: Warning message
        """
        warning = {
            "timestamp": datetime.utcnow().isoformat(),
            "context": context,
            "message": message
        }
        self.warnings.append(warning)
        logger.warning(f"Warning in {context}: {message}")
    
    def calculate_overall_progress(self) -> float:
        """
        Calculate overall analysis progress percentage.
        
        Returns:
            Progress percentage (0-100)
        """
        total_progress = 0.0
        
        for phase, weight in self.PHASE_WEIGHTS.items():
            phase_progress = self.phase_progress.get(phase, 0.0)
            
            # Adjust for phase status
            if self.phase_status.get(phase) == PhaseStatus.COMPLETED:
                phase_progress = 100.0
            elif self.phase_status.get(phase) == PhaseStatus.SKIPPED:
                phase_progress = 100.0  # Count skipped as complete for progress
            elif self.phase_status.get(phase) == PhaseStatus.FAILED:
                phase_progress = 0.0
            
            total_progress += (phase_progress / 100.0) * weight
        
        return total_progress * 100.0
    
    def estimate_completion_time(self) -> Optional[datetime]:
        """
        Estimate when analysis will complete.
        
        Returns:
            Estimated completion datetime, or None if cannot estimate
        """
        overall_progress = self.calculate_overall_progress()
        
        if overall_progress <= 0.0:
            return None
        
        elapsed = datetime.utcnow() - self.started_at
        total_estimated = elapsed / (overall_progress / 100.0)
        remaining = total_estimated - elapsed
        
        return datetime.utcnow() + remaining
    
    def get_phase_duration(self, phase: AnalysisPhase) -> Optional[timedelta]:
        """
        Get duration of a completed phase.
        
        Args:
            phase: The phase to check
        
        Returns:
            Duration as timedelta, or None if not completed
        """
        start = self.phase_start_times.get(phase)
        end = self.phase_end_times.get(phase)
        
        if start and end:
            return end - start
        return None
    
    def mark_completed(self) -> None:
        """Mark the entire analysis as completed."""
        self.current_phase = AnalysisPhase.COMPLETED
        self.completed_at = datetime.utcnow()
        logger.info(f"Analysis {self.analysis_id} completed")
    
    def mark_failed(self, reason: str) -> None:
        """
        Mark the entire analysis as failed.
        
        Args:
            reason: Reason for failure
        """
        self.current_phase = AnalysisPhase.FAILED
        self.completed_at = datetime.utcnow()
        self.add_error("analysis", reason)
        logger.error(f"Analysis {self.analysis_id} failed: {reason}")
    
    def mark_cancelled(self, reason: Optional[str] = None) -> None:
        """
        Mark the entire analysis as cancelled.
        
        Args:
            reason: Optional reason for cancellation
        """
        self.current_phase = AnalysisPhase.CANCELLED
        self.completed_at = datetime.utcnow()
        if reason:
            self.add_warning("analysis", f"Cancelled: {reason}")
        logger.info(f"Analysis {self.analysis_id} cancelled")
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get complete status of analysis progress.
        
        Returns:
            Dict containing comprehensive progress information
        """
        # Determine simple status from current phase
        if self.current_phase == AnalysisPhase.COMPLETED:
            simple_status = "completed"
        elif self.current_phase == AnalysisPhase.FAILED:
            simple_status = "failed"
        elif self.current_phase == AnalysisPhase.CANCELLED:
            simple_status = "cancelled"
        else:
            simple_status = "running"
        
        return {
            "analysis_id": str(self.analysis_id),
            "project_id": str(self.project_id),
            "status": simple_status,
            "current_phase": self.current_phase.value,
            "overall_progress": round(self.calculate_overall_progress(), 2),
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "estimated_completion": (
                self.estimate_completion_time().isoformat()
                if self.estimate_completion_time() else None
            ),
            "duration_seconds": (
                (datetime.utcnow() - self.started_at).total_seconds()
                if not self.completed_at
                else (self.completed_at - self.started_at).total_seconds()
            ),
            "phases": {
                phase.value: {
                    "status": self.phase_status.get(phase, PhaseStatus.PENDING).value,
                    "progress": round(self.phase_progress.get(phase, 0.0), 2),
                    "started_at": (
                        self.phase_start_times.get(phase).isoformat()
                        if self.phase_start_times.get(phase) else None
                    ),
                    "completed_at": (
                        self.phase_end_times.get(phase).isoformat()
                        if self.phase_end_times.get(phase) else None
                    ),
                    "duration_seconds": (
                        self.get_phase_duration(phase).total_seconds()
                        if self.get_phase_duration(phase) else None
                    ),
                    "subtasks": self.phase_subtasks.get(phase, [])
                }
                for phase in AnalysisPhase
                if phase not in [AnalysisPhase.COMPLETED, AnalysisPhase.FAILED, AnalysisPhase.CANCELLED]
            },
            "errors": self.errors,
            "warnings": self.warnings,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings)
        }
