import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { Router } from '@angular/router';
import { MatTableModule } from '@angular/material/table';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatTooltipModule } from '@angular/material/tooltip';
import { ProjectService } from '../../../services/project.service';
import { AnalysisProject } from '../../../models/analysis-project.model';

@Component({
  selector: 'app-project-list',
  standalone: true,
  imports: [
    CommonModule,
    MatTableModule,
    MatButtonModule,
    MatIconModule,
    MatCardModule,
    MatChipsModule,
    MatProgressSpinnerModule,
    MatTooltipModule
  ],
  templateUrl: './project-list.component.html',
  styleUrls: ['./project-list.component.scss']
})
export class ProjectListComponent implements OnInit {
  projects: AnalysisProject[] = [];
  displayedColumns: string[] = ['name', 'status', 'framework', 'created_at', 'actions'];
  loading = true;
  error: string | null = null;

  constructor(
    private projectService: ProjectService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.loadProjects();
  }

  loadProjects(): void {
    this.loading = true;
    this.error = null;

    this.projectService.getProjects().subscribe({
      next: (response) => {
        this.projects = response.projects;
        this.loading = false;
      },
      error: (err) => {
        this.error = 'Failed to load projects. Please try again.';
        this.loading = false;
        console.error('Error loading projects:', err);
      }
    });
  }

  getStatusColor(status: string): string {
    const colors: { [key: string]: string } = {
      'pending': 'accent',
      'in_progress': 'primary',
      'completed': 'primary',
      'failed': 'warn'
    };
    return colors[status] || 'accent';
  }

  viewProject(project: AnalysisProject): void {
    this.router.navigate(['/projects', project.id]);
  }

  deleteProject(project: AnalysisProject, event: Event): void {
    event.stopPropagation();
    
    if (confirm(`Are you sure you want to delete project "${project.name}"?`)) {
      this.projectService.deleteProject(project.id).subscribe({
        next: () => {
          this.loadProjects();
        },
        error: (err) => {
          console.error('Error deleting project:', err);
          alert('Failed to delete project. Please try again.');
        }
      });
    }
  }

  createNewProject(): void {
    this.router.navigate(['/projects/new']);
  }

  formatDate(dateString: string): string {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
  }
}
