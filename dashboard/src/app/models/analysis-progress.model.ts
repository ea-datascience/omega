/**
 * Analysis Progress Models
 * 
 * TypeScript interfaces for real-time analysis progress tracking.
 * Based on backend ProgressTracker service.
 */

/**
 * Analysis workflow phases
 */
export enum AnalysisPhase {
  INITIALIZING = 'initializing',
  STATIC_ANALYSIS = 'static_analysis',
  RUNTIME_ANALYSIS = 'runtime_analysis',
  GAP_ANALYSIS = 'gap_analysis',
  RESULT_AGGREGATION = 'result_aggregation',
  COMPLETED = 'completed',
  FAILED = 'failed',
  CANCELLED = 'cancelled'
}

/**
 * Status of individual phase
 */
export enum PhaseStatus {
  PENDING = 'pending',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  FAILED = 'failed',
  SKIPPED = 'skipped'
}

/**
 * Sub-task within a phase
 */
export interface PhaseSubtask {
  name: string;
  description?: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  started_at?: string;
  completed_at?: string;
  progress: number;
}

/**
 * Progress details for a specific phase
 */
export interface PhaseProgress {
  phase: AnalysisPhase;
  status: PhaseStatus;
  progress: number;
  started_at?: string;
  completed_at?: string;
  subtasks: PhaseSubtask[];
  weight: number;
}

/**
 * Error record
 */
export interface AnalysisError {
  timestamp: string;
  context: string;
  message: string;
}

/**
 * Warning record
 */
export interface AnalysisWarning {
  timestamp: string;
  context: string;
  message: string;
}

/**
 * Complete analysis progress status
 */
export interface AnalysisProgress {
  analysis_id: string;
  project_id: string;
  status: 'queued' | 'running' | 'completed' | 'failed' | 'cancelled';
  current_phase: AnalysisPhase;
  overall_progress: number;
  started_at: string;
  completed_at?: string;
  estimated_completion?: string;
  phases: PhaseProgress[];
  errors: AnalysisError[];
  warnings: AnalysisWarning[];
  error_message?: string;
}

/**
 * Phase configuration with display metadata
 */
export interface PhaseConfig {
  phase: AnalysisPhase;
  label: string;
  description: string;
  icon: string;
  weight: number;
}

/**
 * Helper function to get phase configuration
 */
export function getPhaseConfig(phase: AnalysisPhase): PhaseConfig {
  const configs: Record<AnalysisPhase, PhaseConfig> = {
    [AnalysisPhase.INITIALIZING]: {
      phase: AnalysisPhase.INITIALIZING,
      label: 'Initializing',
      description: 'Setting up analysis environment',
      icon: 'settings',
      weight: 0.05
    },
    [AnalysisPhase.STATIC_ANALYSIS]: {
      phase: AnalysisPhase.STATIC_ANALYSIS,
      label: 'Static Analysis',
      description: 'Analyzing code structure and dependencies',
      icon: 'code',
      weight: 0.35
    },
    [AnalysisPhase.RUNTIME_ANALYSIS]: {
      phase: AnalysisPhase.RUNTIME_ANALYSIS,
      label: 'Runtime Analysis',
      description: 'Analyzing runtime behavior and telemetry',
      icon: 'timeline',
      weight: 0.30
    },
    [AnalysisPhase.GAP_ANALYSIS]: {
      phase: AnalysisPhase.GAP_ANALYSIS,
      label: 'Gap Analysis',
      description: 'Identifying migration gaps and requirements',
      icon: 'compare_arrows',
      weight: 0.20
    },
    [AnalysisPhase.RESULT_AGGREGATION]: {
      phase: AnalysisPhase.RESULT_AGGREGATION,
      label: 'Result Aggregation',
      description: 'Aggregating and finalizing results',
      icon: 'merge_type',
      weight: 0.10
    },
    [AnalysisPhase.COMPLETED]: {
      phase: AnalysisPhase.COMPLETED,
      label: 'Completed',
      description: 'Analysis completed successfully',
      icon: 'check_circle',
      weight: 0
    },
    [AnalysisPhase.FAILED]: {
      phase: AnalysisPhase.FAILED,
      label: 'Failed',
      description: 'Analysis failed',
      icon: 'error',
      weight: 0
    },
    [AnalysisPhase.CANCELLED]: {
      phase: AnalysisPhase.CANCELLED,
      label: 'Cancelled',
      description: 'Analysis was cancelled',
      icon: 'cancel',
      weight: 0
    }
  };
  
  return configs[phase];
}

/**
 * Helper function to get status color
 */
export function getPhaseStatusColor(status: PhaseStatus): string {
  const colors: Record<PhaseStatus, string> = {
    [PhaseStatus.PENDING]: 'basic',
    [PhaseStatus.IN_PROGRESS]: 'primary',
    [PhaseStatus.COMPLETED]: 'accent',
    [PhaseStatus.FAILED]: 'warn',
    [PhaseStatus.SKIPPED]: 'basic'
  };
  
  return colors[status];
}
