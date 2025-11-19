import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { DashboardOverview } from '../models/analysis-dashboard.model';
import { environment } from '../../environments/environment';

/**
 * Analysis Dashboard Service
 * 
 * HTTP service for fetching aggregated dashboard overview data.
 * Provides the main dashboard with project summary, analysis status,
 * quick stats, findings, and recommendations.
 */
@Injectable({
  providedIn: 'root'
})
export class AnalysisDashboardService {
  private apiUrl = `${environment.apiBaseUrl}/api/v1/analysis`;

  constructor(private http: HttpClient) {}

  /**
   * Get dashboard overview for an analysis
   * 
   * @param analysisId - The analysis ID
   * @returns Observable of dashboard overview data
   */
  getDashboardOverview(analysisId: string): Observable<DashboardOverview> {
    return this.http.get<DashboardOverview>(`${this.apiUrl}/${analysisId}/dashboard`);
  }

  /**
   * Export analysis report
   * 
   * @param analysisId - The analysis ID
   * @param format - Export format (pdf, html, json, markdown)
   * @returns Observable of export blob
   */
  exportReport(analysisId: string, format: string): Observable<Blob> {
    return this.http.get(`${this.apiUrl}/${analysisId}/export/${format}`, {
      responseType: 'blob'
    });
  }

  /**
   * Cancel a running analysis
   * 
   * @param analysisId - The analysis ID
   * @returns Observable of cancellation confirmation
   */
  cancelAnalysis(analysisId: string): Observable<void> {
    return this.http.post<void>(`${this.apiUrl}/${analysisId}/cancel`, {});
  }

  /**
   * Restart a failed analysis
   * 
   * @param analysisId - The analysis ID
   * @returns Observable of restart confirmation
   */
  restartAnalysis(analysisId: string): Observable<void> {
    return this.http.post<void>(`${this.apiUrl}/${analysisId}/restart`, {});
  }
}
