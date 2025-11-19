import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../../environments/environment';
import { DependencyGraph } from '../models/dependency-graph.model';

/**
 * Service for fetching dependency graph data
 */
@Injectable({
  providedIn: 'root'
})
export class DependencyService {
  private readonly apiUrl = `${environment.apiBaseUrl}/api/v1/analysis`;

  constructor(private http: HttpClient) {}

  /**
   * Get dependency graph for an analysis
   * @param analysisId The analysis ID
   * @returns Observable of dependency graph data
   */
  getDependencies(analysisId: string): Observable<DependencyGraph> {
    return this.http.get<DependencyGraph>(`${this.apiUrl}/${analysisId}/dependencies`);
  }
}
