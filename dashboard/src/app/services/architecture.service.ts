import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { SystemArchitecture } from '../models/architecture.model';

/**
 * Service for fetching system architecture data
 */
@Injectable({
  providedIn: 'root'
})
export class ArchitectureService {
  private readonly apiUrl = `${environment.apiBaseUrl}/api/v1/analysis`;

  constructor(private http: HttpClient) {}

  /**
   * Get system architecture for an analysis
   * @param analysisId The analysis ID
   * @returns Observable of system architecture data
   */
  getArchitecture(analysisId: string): Observable<SystemArchitecture> {
    return this.http.get<SystemArchitecture>(`${this.apiUrl}/${analysisId}/architecture`);
  }
}
