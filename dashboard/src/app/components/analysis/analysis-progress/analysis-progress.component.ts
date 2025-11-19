/**
 * Analysis Progress Component
 * 
 * Displays real-time progress of analysis execution with phase tracking,
 * subtask details, and error/warning reporting.
 */

import { Component, Input, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatListModule } from '@angular/material/list';
import { MatButtonModule } from '@angular/material/button';
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDividerModule } from '@angular/material/divider';
import { Subject, takeUntil } from 'rxjs';

import { AnalysisProgressService } from '../../../services/analysis-progress.service';
import {
  AnalysisProgress,
  AnalysisPhase,
  PhaseStatus,
  PhaseProgress,
  getPhaseConfig,
  getPhaseStatusColor
} from '../../../models/analysis-progress.model';

@Component({
  selector: 'app-analysis-progress',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatProgressBarModule,
    MatProgressSpinnerModule,
    MatIconModule,
    MatChipsModule,
    MatExpansionModule,
    MatListModule,
    MatButtonModule,
    MatTooltipModule,
    MatDividerModule
  ],
  templateUrl: './analysis-progress.component.html',
  styleUrls: ['./analysis-progress.component.scss']
})
export class AnalysisProgressComponent implements OnInit, OnDestroy {
  @Input() analysisId!: string;
  @Input() autoRefresh: boolean = true;
  @Input() refreshInterval: number = 2000;

  progress: AnalysisProgress | null = null;
  loading: boolean = true;
  error: string | null = null;

  private destroy$ = new Subject<void>();

  // Expose enums for template
  AnalysisPhase = AnalysisPhase;
  PhaseStatus = PhaseStatus;

  constructor(private progressService: AnalysisProgressService) {}

  ngOnInit(): void {
    if (!this.analysisId) {
      this.error = 'Analysis ID is required';
      this.loading = false;
      return;
    }

    this.loadProgress();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  /**
   * Load progress data
   */
  loadProgress(): void {
    this.loading = true;
    this.error = null;

    const progressObservable = this.autoRefresh
      ? this.progressService.pollProgress(this.analysisId, this.refreshInterval)
      : this.progressService.getProgress(this.analysisId);

    progressObservable
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (data) => {
          this.progress = data;
          this.loading = false;
          
          // Stop polling if analysis is complete, failed, or cancelled
          if (this.isTerminalState(data.status)) {
            this.destroy$.next();
          }
        },
        error: (err) => {
          this.error = err.message || 'Failed to load analysis progress';
          this.loading = false;
        }
      });
  }

  /**
   * Cancel analysis
   */
  cancelAnalysis(): void {
    if (!this.analysisId) return;

    this.progressService.cancelAnalysis(this.analysisId)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: () => {
          // Refresh progress to show cancelled state
          this.loadProgress();
        },
        error: (err) => {
          this.error = err.message || 'Failed to cancel analysis';
        }
      });
  }

  /**
   * Check if analysis is in terminal state
   */
  isTerminalState(status: string): boolean {
    return ['completed', 'failed', 'cancelled'].includes(status);
  }

  /**
   * Get phase configuration
   */
  getPhaseConfig(phase: AnalysisPhase) {
    return getPhaseConfig(phase);
  }

  /**
   * Get phase status color
   */
  getPhaseStatusColor(status: PhaseStatus): string {
    return getPhaseStatusColor(status);
  }

  /**
   * Get overall status color
   */
  getOverallStatusColor(): string {
    if (!this.progress) return 'basic';
    
    switch (this.progress.status) {
      case 'completed':
        return 'accent';
      case 'failed':
        return 'warn';
      case 'cancelled':
        return 'basic';
      case 'running':
        return 'primary';
      default:
        return 'basic';
    }
  }

  /**
   * Get phase icon
   */
  getPhaseIcon(phase: AnalysisPhase): string {
    return this.getPhaseConfig(phase).icon;
  }

  /**
   * Get phase label
   */
  getPhaseLabel(phase: AnalysisPhase): string {
    return this.getPhaseConfig(phase).label;
  }

  /**
   * Get phase description
   */
  getPhaseDescription(phase: AnalysisPhase): string {
    return this.getPhaseConfig(phase).description;
  }

  /**
   * Format timestamp
   */
  formatTimestamp(timestamp?: string): string {
    if (!timestamp) return 'N/A';
    
    const date = new Date(timestamp);
    return date.toLocaleString();
  }

  /**
   * Calculate elapsed time
   */
  getElapsedTime(): string {
    if (!this.progress?.started_at) return 'N/A';
    
    const start = new Date(this.progress.started_at);
    const end = this.progress.completed_at 
      ? new Date(this.progress.completed_at) 
      : new Date();
    
    const diffMs = end.getTime() - start.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const remainingMins = diffMins % 60;
    
    if (diffHours > 0) {
      return `${diffHours}h ${remainingMins}m`;
    }
    return `${diffMins}m`;
  }

  /**
   * Get estimated remaining time
   */
  getEstimatedRemaining(): string {
    if (!this.progress?.estimated_completion) return 'Calculating...';
    
    const estimated = new Date(this.progress.estimated_completion);
    const now = new Date();
    
    if (estimated <= now) return 'Almost done...';
    
    const diffMs = estimated.getTime() - now.getTime();
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMins / 60);
    const remainingMins = diffMins % 60;
    
    if (diffHours > 0) {
      return `~${diffHours}h ${remainingMins}m remaining`;
    }
    return `~${diffMins}m remaining`;
  }

  /**
   * Get progress bar mode
   */
  getProgressMode(): 'determinate' | 'indeterminate' {
    return this.progress && this.progress.overall_progress > 0 
      ? 'determinate' 
      : 'indeterminate';
  }

  /**
   * Refresh progress manually
   */
  refresh(): void {
    this.loadProgress();
  }
}
