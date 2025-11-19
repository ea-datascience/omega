/**
 * Analysis Progress Service
 * 
 * Service for fetching real-time analysis progress data from the backend API.
 */

import { Injectable } from '@angular/core';
import { HttpClient, HttpErrorResponse } from '@angular/common/http';
import { Observable, throwError, timer } from 'rxjs';
import { catchError, retry, switchMap, shareReplay } from 'rxjs/operators';
import { environment } from '../../environments/environment';
import { AnalysisProgress } from '../models/analysis-progress.model';

@Injectable({
  providedIn: 'root'
})
export class AnalysisProgressService {
  private readonly baseUrl = `${environment.apiBaseUrl}/api/v1/analysis`;

  constructor(private http: HttpClient) {}

  /**
   * Get current progress for an analysis
   * 
   * @param analysisId - UUID of the analysis
   * @returns Observable of analysis progress
   */
  getProgress(analysisId: string): Observable<AnalysisProgress> {
    return this.http.get<AnalysisProgress>(`${this.baseUrl}/${analysisId}/progress`)
      .pipe(
        retry(2),
        catchError(this.handleError)
      );
  }

  /**
   * Poll progress updates at regular intervals
   * 
   * @param analysisId - UUID of the analysis
   * @param intervalMs - Polling interval in milliseconds (default: 2000)
   * @returns Observable that emits progress updates
   */
  pollProgress(analysisId: string, intervalMs: number = 2000): Observable<AnalysisProgress> {
    return timer(0, intervalMs).pipe(
      switchMap(() => this.getProgress(analysisId)),
      shareReplay(1)
    );
  }

  /**
   * Start analysis execution
   * 
   * @param projectId - UUID of the project
   * @param config - Analysis configuration
   * @returns Observable of analysis ID
   */
  startAnalysis(projectId: string, config?: any): Observable<{ analysis_id: string }> {
    return this.http.post<{ analysis_id: string }>(
      `${this.baseUrl}/start/${projectId}`,
      config || {}
    ).pipe(
      catchError(this.handleError)
    );
  }

  /**
   * Cancel running analysis
   * 
   * @param analysisId - UUID of the analysis
   * @returns Observable of cancellation result
   */
  cancelAnalysis(analysisId: string): Observable<void> {
    return this.http.post<void>(`${this.baseUrl}/${analysisId}/cancel`, {})
      .pipe(
        catchError(this.handleError)
      );
  }

  /**
   * Handle HTTP errors
   */
  private handleError(error: HttpErrorResponse): Observable<never> {
    let errorMessage = 'An error occurred while fetching analysis progress';
    
    if (error.error instanceof ErrorEvent) {
      // Client-side error
      errorMessage = `Error: ${error.error.message}`;
    } else {
      // Server-side error
      errorMessage = `Error ${error.status}: ${error.error?.detail || error.message}`;
    }
    
    console.error('AnalysisProgressService error:', errorMessage);
    return throwError(() => new Error(errorMessage));
  }
}
