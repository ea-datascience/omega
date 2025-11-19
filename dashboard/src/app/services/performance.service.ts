import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { PerformanceBaseline } from '../models/performance-metrics.model';

/**
 * Service for fetching performance baseline data
 */
@Injectable({
  providedIn: 'root'
})
export class PerformanceService {
  private readonly apiUrl = `${environment.apiBaseUrl}/api/v1/analysis`;

  constructor(private http: HttpClient) {}

  /**
   * Get performance baseline for an analysis
   * @param analysisId The analysis ID
   * @returns Observable of performance baseline data
   */
  getBaseline(analysisId: string): Observable<PerformanceBaseline> {
    return this.http.get<PerformanceBaseline>(`${this.apiUrl}/${analysisId}/baselines`);
  }
}
