/**
 * Performance Metrics Models
 * 
 * TypeScript interfaces for performance baseline and metrics visualization
 * Matches backend PerformanceBaseline schema
 */

/**
 * Performance metric type
 */
export enum MetricType {
  RESPONSE_TIME = 'response_time',
  THROUGHPUT = 'throughput',
  ERROR_RATE = 'error_rate',
  CPU_USAGE = 'cpu_usage',
  MEMORY_USAGE = 'memory_usage',
  DISK_IO = 'disk_io',
  NETWORK_IO = 'network_io',
  DATABASE_QUERY_TIME = 'database_query_time'
}

/**
 * Time-series data point
 */
export interface MetricDataPoint {
  timestamp: string;
  value: number;
  unit: string;
}

/**
 * Statistical summary for a metric
 */
export interface MetricStatistics {
  min: number;
  max: number;
  avg: number;
  median: number;
  p50: number;
  p90: number;
  p95: number;
  p99: number;
  stddev: number;
}

/**
 * Performance metric with time-series data
 */
export interface PerformanceMetric {
  metric_type: MetricType;
  name: string;
  description?: string;
  unit: string;
  
  // Time-series data
  data_points: MetricDataPoint[];
  
  // Statistics
  statistics: MetricStatistics;
  
  // Thresholds
  threshold_warning?: number;
  threshold_critical?: number;
  
  // Status
  status: 'healthy' | 'warning' | 'critical';
}

/**
 * API endpoint performance
 */
export interface EndpointMetrics {
  endpoint: string;
  method: string;
  
  // Request metrics
  total_requests: number;
  successful_requests: number;
  failed_requests: number;
  error_rate: number;
  
  // Response time metrics
  avg_response_time: number;
  min_response_time: number;
  max_response_time: number;
  p95_response_time: number;
  p99_response_time: number;
  
  // Throughput
  requests_per_second: number;
}

/**
 * Resource utilization metrics
 */
export interface ResourceMetrics {
  // CPU
  cpu_usage_percent: number;
  cpu_avg: number;
  cpu_peak: number;
  
  // Memory
  memory_usage_mb: number;
  memory_usage_percent: number;
  memory_avg_mb: number;
  memory_peak_mb: number;
  
  // Disk
  disk_read_mbps?: number;
  disk_write_mbps?: number;
  
  // Network
  network_in_mbps?: number;
  network_out_mbps?: number;
}

/**
 * Database performance metrics
 */
export interface DatabaseMetrics {
  // Query performance
  total_queries: number;
  avg_query_time_ms: number;
  slow_query_count: number;
  slow_query_threshold_ms: number;
  
  // Connection pool
  active_connections: number;
  max_connections: number;
  connection_pool_utilization: number;
  
  // Cache
  cache_hit_rate?: number;
  cache_miss_rate?: number;
}

/**
 * Performance baseline comparison
 */
export interface BaselineComparison {
  metric_name: string;
  baseline_value: number;
  current_value: number;
  difference: number;
  difference_percent: number;
  is_regression: boolean;
  severity: 'none' | 'minor' | 'major' | 'critical';
}

/**
 * Performance test scenario
 */
export interface TestScenario {
  scenario_id: string;
  name: string;
  description?: string;
  
  // Test parameters
  duration_seconds: number;
  virtual_users: number;
  ramp_up_time_seconds?: number;
  
  // Results
  start_time: string;
  end_time: string;
  status: 'running' | 'completed' | 'failed';
}

/**
 * Complete performance baseline data
 */
export interface PerformanceBaseline {
  analysis_id: string;
  project_name: string;
  
  // Test scenario
  test_scenario?: TestScenario;
  
  // Metrics
  metrics: PerformanceMetric[];
  endpoint_metrics: EndpointMetrics[];
  resource_metrics: ResourceMetrics;
  database_metrics?: DatabaseMetrics;
  
  // Comparisons
  baseline_comparisons?: BaselineComparison[];
  
  // Summary
  overall_health: 'healthy' | 'warning' | 'critical';
  total_requests: number;
  avg_response_time: number;
  error_rate: number;
  
  // Metadata
  captured_at: string;
  duration_seconds: number;
  environment: string;
}

/**
 * Chart configuration for metrics visualization
 */
export interface ChartConfig {
  chart_type: 'line' | 'bar' | 'area' | 'pie';
  title: string;
  x_axis_label?: string;
  y_axis_label?: string;
  show_legend: boolean;
  show_grid: boolean;
}

/**
 * Performance alert
 */
export interface PerformanceAlert {
  alert_id: string;
  metric_type: MetricType;
  severity: 'warning' | 'critical';
  message: string;
  threshold_value: number;
  actual_value: number;
  timestamp: string;
}
