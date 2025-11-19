import { Injectable } from '@angular/core';
import { HttpClient, HttpParams } from '@angular/common/http';
import { Observable } from 'rxjs';
import { AnalysisProject, ProjectListResponse } from '../models/analysis-project.model';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class ProjectService {
  private apiUrl = `${environment.apiBaseUrl}/api/v1/projects`;

  constructor(private http: HttpClient) {}

  getProjects(page: number = 1, pageSize: number = 10): Observable<ProjectListResponse> {
    const params = new HttpParams()
      .set('page', page.toString())
      .set('page_size', pageSize.toString());
    
    return this.http.get<ProjectListResponse>(this.apiUrl, { params });
  }

  getProject(id: string): Observable<AnalysisProject> {
    return this.http.get<AnalysisProject>(`${this.apiUrl}/${id}`);
  }

  createProject(project: Partial<AnalysisProject>): Observable<AnalysisProject> {
    return this.http.post<AnalysisProject>(this.apiUrl, project);
  }

  deleteProject(id: string): Observable<void> {
    return this.http.delete<void>(`${this.apiUrl}/${id}`);
  }
}
