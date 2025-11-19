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
  }
];
