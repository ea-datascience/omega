import { Routes } from '@angular/router';

export const routes: Routes = [
  {
    path: '',
    redirectTo: '/projects',
    pathMatch: 'full'
  },
  {
    path: 'projects',
    loadComponent: () => import('./components/analysis/project-list/project-list.component').then(m => m.ProjectListComponent)
  },
  {
    path: 'projects/:id/progress',
    loadComponent: () => import('./components/analysis/analysis-progress/analysis-progress.component').then(m => m.AnalysisProgressComponent)
  },
  {
    path: 'projects/:id/architecture',
    loadComponent: () => import('./components/analysis/architecture-visualization/architecture-visualization.component').then(m => m.ArchitectureVisualizationComponent)
  },
  {
    path: 'projects/:id/dependencies',
    loadComponent: () => import('./components/analysis/dependency-graph/dependency-graph.component').then(m => m.DependencyGraphComponent)
  }
];
