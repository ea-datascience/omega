"""
Integration tests for Progress Tracker (T041).

Tests the progress tracking service for analysis workflows.
"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from omega_analysis.services.orchestration.progress_tracker import (
    ProgressTracker,
    AnalysisPhase,
    PhaseStatus
)


class TestProgressTrackerBasics:
    """Test basic progress tracker functionality."""
    
    def test_tracker_initialization(self):
        """Test progress tracker initializes correctly."""
        analysis_id = uuid4()
        project_id = uuid4()
        
        tracker = ProgressTracker(analysis_id, project_id)
        
        assert tracker.analysis_id == analysis_id
        assert tracker.project_id == project_id
        assert tracker.current_phase == AnalysisPhase.INITIALIZING
        assert tracker.completed_at is None
        assert tracker.started_at is not None
    
    def test_initial_phase_statuses(self):
        """Test all phases start as pending."""
        tracker = ProgressTracker(uuid4(), uuid4())
        
        for phase in [AnalysisPhase.INITIALIZING, AnalysisPhase.STATIC_ANALYSIS,
                     AnalysisPhase.RUNTIME_ANALYSIS, AnalysisPhase.GAP_ANALYSIS,
                     AnalysisPhase.RESULT_AGGREGATION]:
            assert tracker.phase_status[phase] == PhaseStatus.PENDING
            assert tracker.phase_progress[phase] == 0.0
    
    def test_initial_overall_progress(self):
        """Test overall progress starts at 0."""
        tracker = ProgressTracker(uuid4(), uuid4())
        
        assert tracker.calculate_overall_progress() == 0.0


class TestPhaseTransitions:
    """Test phase lifecycle transitions."""
    
    def test_start_phase(self):
        """Test starting a phase."""
        tracker = ProgressTracker(uuid4(), uuid4())
        
        tracker.start_phase(AnalysisPhase.STATIC_ANALYSIS)
        
        assert tracker.current_phase == AnalysisPhase.STATIC_ANALYSIS
        assert tracker.phase_status[AnalysisPhase.STATIC_ANALYSIS] == PhaseStatus.IN_PROGRESS
        assert tracker.phase_start_times[AnalysisPhase.STATIC_ANALYSIS] is not None
        assert tracker.phase_progress[AnalysisPhase.STATIC_ANALYSIS] == 0.0
    
    def test_complete_phase(self):
        """Test completing a phase."""
        tracker = ProgressTracker(uuid4(), uuid4())
        
        tracker.start_phase(AnalysisPhase.STATIC_ANALYSIS)
        tracker.complete_phase(AnalysisPhase.STATIC_ANALYSIS)
        
        assert tracker.phase_status[AnalysisPhase.STATIC_ANALYSIS] == PhaseStatus.COMPLETED
        assert tracker.phase_progress[AnalysisPhase.STATIC_ANALYSIS] == 100.0
        assert tracker.phase_end_times[AnalysisPhase.STATIC_ANALYSIS] is not None
    
    def test_fail_phase(self):
        """Test failing a phase."""
        tracker = ProgressTracker(uuid4(), uuid4())
        
        tracker.start_phase(AnalysisPhase.RUNTIME_ANALYSIS)
        tracker.fail_phase(AnalysisPhase.RUNTIME_ANALYSIS, "Test error")
        
        assert tracker.phase_status[AnalysisPhase.RUNTIME_ANALYSIS] == PhaseStatus.FAILED
        assert len(tracker.errors) == 1
        assert tracker.errors[0]["message"] == "Test error"
    
    def test_skip_phase(self):
        """Test skipping a phase."""
        tracker = ProgressTracker(uuid4(), uuid4())
        
        tracker.skip_phase(AnalysisPhase.RUNTIME_ANALYSIS, "Not configured")
        
        assert tracker.phase_status[AnalysisPhase.RUNTIME_ANALYSIS] == PhaseStatus.SKIPPED
        assert tracker.phase_progress[AnalysisPhase.RUNTIME_ANALYSIS] == 0.0
    
    def test_phase_sequence(self):
        """Test transitioning through multiple phases."""
        tracker = ProgressTracker(uuid4(), uuid4())
        
        # Complete initialization
        tracker.start_phase(AnalysisPhase.INITIALIZING)
        tracker.complete_phase(AnalysisPhase.INITIALIZING)
        
        # Start static analysis
        tracker.start_phase(AnalysisPhase.STATIC_ANALYSIS)
        
        assert tracker.current_phase == AnalysisPhase.STATIC_ANALYSIS
        assert tracker.phase_status[AnalysisPhase.INITIALIZING] == PhaseStatus.COMPLETED
        assert tracker.phase_status[AnalysisPhase.STATIC_ANALYSIS] == PhaseStatus.IN_PROGRESS


class TestProgressCalculation:
    """Test progress calculation logic."""
    
    def test_update_phase_progress(self):
        """Test updating phase progress."""
        tracker = ProgressTracker(uuid4(), uuid4())
        
        tracker.start_phase(AnalysisPhase.STATIC_ANALYSIS)
        tracker.update_phase_progress(AnalysisPhase.STATIC_ANALYSIS, 50.0)
        
        assert tracker.phase_progress[AnalysisPhase.STATIC_ANALYSIS] == 50.0
    
    def test_progress_bounds(self):
        """Test progress stays within 0-100 bounds."""
        tracker = ProgressTracker(uuid4(), uuid4())
        
        tracker.start_phase(AnalysisPhase.STATIC_ANALYSIS)
        
        # Test upper bound
        tracker.update_phase_progress(AnalysisPhase.STATIC_ANALYSIS, 150.0)
        assert tracker.phase_progress[AnalysisPhase.STATIC_ANALYSIS] == 100.0
        
        # Test lower bound
        tracker.update_phase_progress(AnalysisPhase.STATIC_ANALYSIS, -50.0)
        assert tracker.phase_progress[AnalysisPhase.STATIC_ANALYSIS] == 0.0
    
    def test_overall_progress_single_phase(self):
        """Test overall progress with one completed phase."""
        tracker = ProgressTracker(uuid4(), uuid4())
        
        # Complete initialization (5% weight)
        tracker.start_phase(AnalysisPhase.INITIALIZING)
        tracker.complete_phase(AnalysisPhase.INITIALIZING)
        
        progress = tracker.calculate_overall_progress()
        assert progress == pytest.approx(5.0, rel=0.01)
    
    def test_overall_progress_multiple_phases(self):
        """Test overall progress with multiple phases."""
        tracker = ProgressTracker(uuid4(), uuid4())
        
        # Complete initialization (5%)
        tracker.start_phase(AnalysisPhase.INITIALIZING)
        tracker.complete_phase(AnalysisPhase.INITIALIZING)
        
        # Complete static analysis (35%)
        tracker.start_phase(AnalysisPhase.STATIC_ANALYSIS)
        tracker.complete_phase(AnalysisPhase.STATIC_ANALYSIS)
        
        # Half complete runtime analysis (15% of 30%)
        tracker.start_phase(AnalysisPhase.RUNTIME_ANALYSIS)
        tracker.update_phase_progress(AnalysisPhase.RUNTIME_ANALYSIS, 50.0)
        
        expected = 5.0 + 35.0 + (30.0 * 0.5)
        progress = tracker.calculate_overall_progress()
        assert progress == pytest.approx(expected, rel=0.01)
    
    def test_skipped_phase_counted_as_complete(self):
        """Test skipped phases count toward completion."""
        tracker = ProgressTracker(uuid4(), uuid4())
        
        # Skip runtime analysis
        tracker.skip_phase(AnalysisPhase.RUNTIME_ANALYSIS, "Not needed")
        
        # Should count as 30% complete
        progress = tracker.calculate_overall_progress()
        assert progress == pytest.approx(30.0, rel=0.01)


class TestSubtaskTracking:
    """Test sub-task tracking within phases."""
    
    def test_add_subtask(self):
        """Test adding a sub-task to a phase."""
        tracker = ProgressTracker(uuid4(), uuid4())
        
        index = tracker.add_subtask(
            AnalysisPhase.STATIC_ANALYSIS,
            "Parse Java files",
            "Use JavaParser to parse source code"
        )
        
        assert index == 0
        assert len(tracker.phase_subtasks[AnalysisPhase.STATIC_ANALYSIS]) == 1
        
        subtask = tracker.phase_subtasks[AnalysisPhase.STATIC_ANALYSIS][0]
        assert subtask["name"] == "Parse Java files"
        assert subtask["status"] == "pending"
        assert subtask["progress"] == 0.0
    
    def test_update_subtask_status(self):
        """Test updating subtask status."""
        tracker = ProgressTracker(uuid4(), uuid4())
        
        idx = tracker.add_subtask(AnalysisPhase.STATIC_ANALYSIS, "Task 1")
        tracker.update_subtask(AnalysisPhase.STATIC_ANALYSIS, idx, status="in_progress")
        
        subtask = tracker.phase_subtasks[AnalysisPhase.STATIC_ANALYSIS][idx]
        assert subtask["status"] == "in_progress"
        assert subtask["started_at"] is not None
    
    def test_update_subtask_progress(self):
        """Test updating subtask progress."""
        tracker = ProgressTracker(uuid4(), uuid4())
        
        idx = tracker.add_subtask(AnalysisPhase.STATIC_ANALYSIS, "Task 1")
        tracker.update_subtask(AnalysisPhase.STATIC_ANALYSIS, idx, progress=75.0)
        
        subtask = tracker.phase_subtasks[AnalysisPhase.STATIC_ANALYSIS][idx]
        assert subtask["progress"] == 75.0
    
    def test_complete_subtask(self):
        """Test completing a subtask."""
        tracker = ProgressTracker(uuid4(), uuid4())
        
        idx = tracker.add_subtask(AnalysisPhase.STATIC_ANALYSIS, "Task 1")
        tracker.update_subtask(AnalysisPhase.STATIC_ANALYSIS, idx, status="in_progress")
        tracker.update_subtask(AnalysisPhase.STATIC_ANALYSIS, idx, status="completed", progress=100.0)
        
        subtask = tracker.phase_subtasks[AnalysisPhase.STATIC_ANALYSIS][idx]
        assert subtask["status"] == "completed"
        assert subtask["progress"] == 100.0
        assert subtask["completed_at"] is not None
    
    def test_multiple_subtasks(self):
        """Test tracking multiple subtasks."""
        tracker = ProgressTracker(uuid4(), uuid4())
        
        tracker.add_subtask(AnalysisPhase.STATIC_ANALYSIS, "Task 1")
        tracker.add_subtask(AnalysisPhase.STATIC_ANALYSIS, "Task 2")
        tracker.add_subtask(AnalysisPhase.STATIC_ANALYSIS, "Task 3")
        
        assert len(tracker.phase_subtasks[AnalysisPhase.STATIC_ANALYSIS]) == 3


class TestErrorAndWarningTracking:
    """Test error and warning tracking."""
    
    def test_add_error(self):
        """Test adding an error."""
        tracker = ProgressTracker(uuid4(), uuid4())
        
        tracker.add_error("static_analysis", "Failed to parse file.java")
        
        assert len(tracker.errors) == 1
        assert tracker.errors[0]["context"] == "static_analysis"
        assert tracker.errors[0]["message"] == "Failed to parse file.java"
        assert "timestamp" in tracker.errors[0]
    
    def test_add_warning(self):
        """Test adding a warning."""
        tracker = ProgressTracker(uuid4(), uuid4())
        
        tracker.add_warning("runtime_analysis", "Missing optional telemetry data")
        
        assert len(tracker.warnings) == 1
        assert tracker.warnings[0]["context"] == "runtime_analysis"
        assert tracker.warnings[0]["message"] == "Missing optional telemetry data"
    
    def test_multiple_errors(self):
        """Test tracking multiple errors."""
        tracker = ProgressTracker(uuid4(), uuid4())
        
        tracker.add_error("phase1", "Error 1")
        tracker.add_error("phase2", "Error 2")
        tracker.add_error("phase3", "Error 3")
        
        assert len(tracker.errors) == 3


class TestTimeEstimation:
    """Test time estimation and duration tracking."""
    
    def test_estimate_completion_time_zero_progress(self):
        """Test estimation with no progress returns None."""
        tracker = ProgressTracker(uuid4(), uuid4())
        
        estimate = tracker.estimate_completion_time()
        assert estimate is None
    
    def test_get_phase_duration_incomplete(self):
        """Test duration for incomplete phase returns None."""
        tracker = ProgressTracker(uuid4(), uuid4())
        
        tracker.start_phase(AnalysisPhase.STATIC_ANALYSIS)
        duration = tracker.get_phase_duration(AnalysisPhase.STATIC_ANALYSIS)
        
        assert duration is None
    
    def test_get_phase_duration_completed(self):
        """Test duration for completed phase."""
        tracker = ProgressTracker(uuid4(), uuid4())
        
        tracker.start_phase(AnalysisPhase.STATIC_ANALYSIS)
        tracker.complete_phase(AnalysisPhase.STATIC_ANALYSIS)
        
        duration = tracker.get_phase_duration(AnalysisPhase.STATIC_ANALYSIS)
        
        assert duration is not None
        assert duration.total_seconds() >= 0


class TestAnalysisCompletion:
    """Test analysis completion states."""
    
    def test_mark_completed(self):
        """Test marking analysis as completed."""
        tracker = ProgressTracker(uuid4(), uuid4())
        
        tracker.mark_completed()
        
        assert tracker.current_phase == AnalysisPhase.COMPLETED
        assert tracker.completed_at is not None
    
    def test_mark_failed(self):
        """Test marking analysis as failed."""
        tracker = ProgressTracker(uuid4(), uuid4())
        
        tracker.mark_failed("Critical error occurred")
        
        assert tracker.current_phase == AnalysisPhase.FAILED
        assert tracker.completed_at is not None
        assert len(tracker.errors) == 1
    
    def test_mark_cancelled(self):
        """Test marking analysis as cancelled."""
        tracker = ProgressTracker(uuid4(), uuid4())
        
        tracker.mark_cancelled("User requested cancellation")
        
        assert tracker.current_phase == AnalysisPhase.CANCELLED
        assert tracker.completed_at is not None
        assert len(tracker.warnings) == 1


class TestStatusReporting:
    """Test comprehensive status reporting."""
    
    def test_get_status_structure(self):
        """Test status dict has required fields."""
        tracker = ProgressTracker(uuid4(), uuid4())
        
        status = tracker.get_status()
        
        assert "analysis_id" in status
        assert "project_id" in status
        assert "current_phase" in status
        assert "overall_progress" in status
        assert "started_at" in status
        assert "phases" in status
        assert "errors" in status
        assert "warnings" in status
        assert "error_count" in status
        assert "warning_count" in status
    
    def test_get_status_with_progress(self):
        """Test status includes accurate progress information."""
        tracker = ProgressTracker(uuid4(), uuid4())
        
        tracker.start_phase(AnalysisPhase.INITIALIZING)
        tracker.complete_phase(AnalysisPhase.INITIALIZING)
        
        tracker.start_phase(AnalysisPhase.STATIC_ANALYSIS)
        tracker.update_phase_progress(AnalysisPhase.STATIC_ANALYSIS, 50.0)
        
        status = tracker.get_status()
        
        assert status["current_phase"] == "static_analysis"
        assert status["overall_progress"] > 5.0  # More than just initialization
        assert status["phases"]["initializing"]["status"] == "completed"
        assert status["phases"]["static_analysis"]["status"] == "in_progress"
        assert status["phases"]["static_analysis"]["progress"] == 50.0
    
    def test_get_status_with_subtasks(self):
        """Test status includes subtask information."""
        tracker = ProgressTracker(uuid4(), uuid4())
        
        tracker.add_subtask(AnalysisPhase.STATIC_ANALYSIS, "Task 1")
        tracker.add_subtask(AnalysisPhase.STATIC_ANALYSIS, "Task 2")
        
        status = tracker.get_status()
        
        assert len(status["phases"]["static_analysis"]["subtasks"]) == 2
    
    def test_get_status_with_errors(self):
        """Test status includes error and warning counts."""
        tracker = ProgressTracker(uuid4(), uuid4())
        
        tracker.add_error("phase1", "Error 1")
        tracker.add_error("phase2", "Error 2")
        tracker.add_warning("phase3", "Warning 1")
        
        status = tracker.get_status()
        
        assert status["error_count"] == 2
        assert status["warning_count"] == 1
