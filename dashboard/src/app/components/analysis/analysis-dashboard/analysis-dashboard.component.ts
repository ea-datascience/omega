import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ActivatedRoute, Router, RouterModule } from '@angular/router';
import { MatSidenavModule } from '@angular/material/sidenav';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';
import { MatChipsModule } from '@angular/material/chips';
import { MatProgressBarModule } from '@angular/material/progress-bar';
import { MatMenuModule } from '@angular/material/menu';
import { MatBadgeModule } from '@angular/material/badge';
import { MatDividerModule } from '@angular/material/divider';
import { Subject, takeUntil } from 'rxjs';

import { AnalysisDashboardService } from '../../../services/analysis-dashboard.service';
import { 
  DashboardOverview, 
  NavigationItem, 
  BreadcrumbItem,
  DashboardCard,
  Finding,
  Recommendation
} from '../../../models/analysis-dashboard.model';

/**
 * Analysis Dashboard Component
 * 
 * Main integration dashboard that provides:
 * - Project and analysis overview
 * - Navigation to detailed analysis views
 * - Quick stats and metrics cards
 * - Recent findings and recommendations
 * - Analysis status and controls
 */
@Component({
  selector: 'app-analysis-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    RouterModule,
    MatSidenavModule,
    MatToolbarModule,
    MatListModule,
    MatIconModule,
    MatButtonModule,
    MatCardModule,
    MatChipsModule,
    MatProgressBarModule,
    MatMenuModule,
    MatBadgeModule,
    MatDividerModule
  ],
  templateUrl: './analysis-dashboard.component.html',
  styleUrls: ['./analysis-dashboard.component.scss']
})
export class AnalysisDashboardComponent implements OnInit, OnDestroy {
  private destroy$ = new Subject<void>();
  
  analysisId: string = '';
  projectId: string = '';
  overview?: DashboardOverview;
  loading = true;
  error: string | null = null;
  
  // Navigation
  navigationItems: NavigationItem[] = [];
  breadcrumbs: BreadcrumbItem[] = [];
  sidenavOpened = true;
  
  // Dashboard cards
  overviewCards: DashboardCard[] = [];
  
  // Findings and recommendations
  recentFindings: Finding[] = [];
  topRecommendations: Recommendation[] = [];

  constructor(
    private route: ActivatedRoute,
    private router: Router,
    private dashboardService: AnalysisDashboardService
  ) {}

  ngOnInit(): void {
    // Get analysis ID from route
    this.route.paramMap
      .pipe(takeUntil(this.destroy$))
      .subscribe(params => {
        const id = params.get('id');
        if (id) {
          this.analysisId = id;
          this.loadDashboardData();
        }
      });
    
    // Initialize navigation
    this.initializeNavigation();
    
    // Update breadcrumbs based on current route
    this.updateBreadcrumbs();
  }

  ngOnDestroy(): void {
    this.destroy$.next();
    this.destroy$.complete();
  }

  /**
   * Load dashboard overview data
   */
  loadDashboardData(): void {
    this.loading = true;
    this.error = null;
    
    this.dashboardService.getDashboardOverview(this.analysisId)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (data) => {
          this.overview = data;
          this.projectId = data.project_id;
          this.recentFindings = data.recent_findings.slice(0, 5);
          this.topRecommendations = data.recommendations.slice(0, 5);
          this.createOverviewCards();
          this.updateNavigationBadges();
          this.loading = false;
        },
        error: (err) => {
          this.error = 'Failed to load dashboard data';
          console.error('Dashboard load error:', err);
          this.loading = false;
        }
      });
  }

  /**
   * Initialize sidebar navigation items
   */
  private initializeNavigation(): void {
    this.navigationItems = [
      {
        id: 'overview',
        label: 'Overview',
        icon: 'dashboard',
        route: `/projects/${this.analysisId}/dashboard`,
        disabled: false
      },
      {
        id: 'progress',
        label: 'Analysis Progress',
        icon: 'timeline',
        route: `/projects/${this.analysisId}/progress`,
        disabled: false
      },
      {
        id: 'architecture',
        label: 'Architecture',
        icon: 'account_tree',
        route: `/projects/${this.analysisId}/architecture`,
        disabled: false
      },
      {
        id: 'dependencies',
        label: 'Dependencies',
        icon: 'device_hub',
        route: `/projects/${this.analysisId}/dependencies`,
        disabled: false
      },
      {
        id: 'performance',
        label: 'Performance',
        icon: 'speed',
        route: `/projects/${this.analysisId}/performance`,
        disabled: false
      }
    ];
  }

  /**
   * Update navigation item badges based on overview data
   */
  private updateNavigationBadges(): void {
    if (!this.overview) return;
    
    const dependenciesItem = this.navigationItems.find(item => item.id === 'dependencies');
    if (dependenciesItem) {
      dependenciesItem.badge = this.overview.quick_stats.circular_dependencies;
    }
    
    const performanceItem = this.navigationItems.find(item => item.id === 'performance');
    if (performanceItem) {
      performanceItem.badge = this.overview.quick_stats.performance_issues;
    }
  }

  /**
   * Create overview cards from dashboard data
   */
  private createOverviewCards(): void {
    if (!this.overview) return;
    
    const { summary, quick_stats } = this.overview;
    
    this.overviewCards = [
      {
        id: 'components',
        title: 'Total Components',
        icon: 'widgets',
        value: summary.total_components,
        subtitle: `${quick_stats.service_candidates} service candidates`,
        color: 'primary',
        route: `/projects/${this.analysisId}/architecture`
      },
      {
        id: 'dependencies',
        title: 'Dependencies',
        icon: 'link',
        value: summary.total_dependencies,
        subtitle: `${quick_stats.circular_dependencies} circular`,
        color: quick_stats.circular_dependencies > 0 ? 'warn' : 'accent',
        route: `/projects/${this.analysisId}/dependencies`
      },
      {
        id: 'performance',
        title: 'Performance Issues',
        icon: 'warning',
        value: quick_stats.performance_issues,
        color: quick_stats.performance_issues > 5 ? 'warn' : 'accent',
        route: `/projects/${this.analysisId}/performance`
      },
      {
        id: 'complexity',
        title: 'Complexity Score',
        icon: 'assessment',
        value: summary.complexity_score.toFixed(1),
        subtitle: 'out of 10',
        color: summary.complexity_score > 7 ? 'warn' : 'primary'
      },
      {
        id: 'readiness',
        title: 'Migration Readiness',
        icon: 'check_circle',
        value: `${summary.migration_readiness_score}%`,
        color: summary.migration_readiness_score > 70 ? 'accent' : 'warn'
      },
      {
        id: 'effort',
        title: 'Estimated Effort',
        icon: 'schedule',
        value: `${summary.estimated_effort_days}`,
        subtitle: 'days',
        color: 'primary'
      }
    ];
  }

  /**
   * Update breadcrumbs based on current route
   */
  private updateBreadcrumbs(): void {
    this.breadcrumbs = [
      { label: 'Projects', route: '/projects' },
      { label: this.overview?.project_name || 'Analysis', active: true }
    ];
  }

  /**
   * Navigate to a specific view
   */
  navigateTo(route: string): void {
    this.router.navigate([route]);
  }

  /**
   * Navigate to card route
   */
  onCardClick(card: DashboardCard): void {
    if (card.route) {
      this.router.navigate([card.route]);
    }
  }

  /**
   * Toggle sidebar
   */
  toggleSidenav(): void {
    this.sidenavOpened = !this.sidenavOpened;
  }

  /**
   * Export analysis report
   */
  exportReport(format: string): void {
    this.dashboardService.exportReport(this.analysisId, format)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (blob) => {
          const url = window.URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          link.download = `analysis-${this.analysisId}.${format}`;
          link.click();
          window.URL.revokeObjectURL(url);
        },
        error: (err) => {
          console.error('Export error:', err);
        }
      });
  }

  /**
   * Cancel analysis
   */
  cancelAnalysis(): void {
    if (confirm('Are you sure you want to cancel this analysis?')) {
      this.dashboardService.cancelAnalysis(this.analysisId)
        .pipe(takeUntil(this.destroy$))
        .subscribe({
          next: () => {
            this.loadDashboardData();
          },
          error: (err) => {
            console.error('Cancel error:', err);
          }
        });
    }
  }

  /**
   * Restart failed analysis
   */
  restartAnalysis(): void {
    this.dashboardService.restartAnalysis(this.analysisId)
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: () => {
          this.loadDashboardData();
        },
        error: (err) => {
          console.error('Restart error:', err);
        }
      });
  }

  /**
   * Get status color
   */
  getStatusColor(): string {
    if (!this.overview) return 'primary';
    
    switch (this.overview.analysis_status) {
      case 'completed':
        return 'accent';
      case 'running':
        return 'primary';
      case 'failed':
        return 'warn';
      default:
        return 'primary';
    }
  }

  /**
   * Get severity color for findings
   */
  getSeverityColor(severity: string): string {
    switch (severity) {
      case 'critical':
        return 'warn';
      case 'high':
        return 'warn';
      case 'medium':
        return 'accent';
      default:
        return 'primary';
    }
  }

  /**
   * Get priority color for recommendations
   */
  getPriorityColor(priority: string): string {
    switch (priority) {
      case 'critical':
      case 'high':
        return 'warn';
      case 'medium':
        return 'accent';
      default:
        return 'primary';
    }
  }
}
