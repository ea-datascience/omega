/**
 * Analysis Dashboard Models
 * 
 * TypeScript interfaces for the main analysis dashboard integration component.
 * Provides overview data, navigation context, and aggregated metrics.
 */

/**
 * Dashboard Overview
 * Aggregated data for the main dashboard view
 */
export interface DashboardOverview {
  project_id: string;
  project_name: string;
  analysis_id: string;
  analysis_status: AnalysisStatus;
  started_at: string;
  completed_at?: string;
  summary: AnalysisSummary;
  quick_stats: QuickStats;
  recent_findings: Finding[];
  recommendations: Recommendation[];
}

/**
 * Analysis Status
 */
export type AnalysisStatus = 
  | 'pending' 
  | 'running' 
  | 'completed' 
  | 'failed' 
  | 'cancelled';

/**
 * Analysis Summary
 * High-level summary of analysis results
 */
export interface AnalysisSummary {
  total_components: number;
  total_dependencies: number;
  total_endpoints: number;
  total_issues: number;
  complexity_score: number;
  migration_readiness_score: number;
  estimated_effort_days: number;
}

/**
 * Quick Stats
 * Key metrics displayed as cards
 */
export interface QuickStats {
  service_candidates: number;
  circular_dependencies: number;
  high_coupling_components: number;
  performance_issues: number;
  code_smells: number;
  test_coverage_percentage: number;
}

/**
 * Finding
 * Individual analysis finding or issue
 */
export interface Finding {
  id: string;
  category: FindingCategory;
  severity: Severity;
  title: string;
  description: string;
  affected_components: string[];
  recommendation: string;
  created_at: string;
}

/**
 * Finding Category
 */
export type FindingCategory = 
  | 'architecture' 
  | 'dependency' 
  | 'performance' 
  | 'security' 
  | 'code_quality' 
  | 'testing';

/**
 * Severity Level
 */
export type Severity = 'low' | 'medium' | 'high' | 'critical';

/**
 * Recommendation
 * Actionable recommendation for migration
 */
export interface Recommendation {
  id: string;
  priority: Priority;
  title: string;
  description: string;
  impact: string;
  effort: string;
  category: string;
}

/**
 * Priority Level
 */
export type Priority = 'low' | 'medium' | 'high' | 'critical';

/**
 * Navigation Item
 * Sidebar navigation menu item
 */
export interface NavigationItem {
  id: string;
  label: string;
  icon: string;
  route: string;
  badge?: number;
  disabled?: boolean;
}

/**
 * Breadcrumb Item
 */
export interface BreadcrumbItem {
  label: string;
  route?: string;
  active?: boolean;
}

/**
 * Dashboard Card
 * Overview card configuration
 */
export interface DashboardCard {
  id: string;
  title: string;
  icon: string;
  value: string | number;
  subtitle?: string;
  trend?: Trend;
  color?: string;
  route?: string;
}

/**
 * Trend
 * Value change trend indicator
 */
export interface Trend {
  direction: 'up' | 'down' | 'neutral';
  percentage: number;
  label: string;
}

/**
 * Analysis Phase
 * Current phase of analysis execution
 */
export interface AnalysisPhase {
  name: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress_percentage: number;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
}

/**
 * Export Configuration
 * Settings for exporting analysis reports
 */
export interface ExportConfiguration {
  format: 'pdf' | 'html' | 'json' | 'markdown';
  include_charts: boolean;
  include_raw_data: boolean;
  sections: string[];
}
