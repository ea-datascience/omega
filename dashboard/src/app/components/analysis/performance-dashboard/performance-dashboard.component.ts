import { Component, Input, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatTableModule } from '@angular/material/table';
import { MatTabsModule } from '@angular/material/tabs';
import { MatDividerModule } from '@angular/material/divider';
import { NgChartsModule } from 'ng2-charts';
import { ChartConfiguration, ChartType } from 'chart.js';
import { PerformanceService } from '../../../services/performance.service';
import {
  PerformanceBaseline,
  PerformanceMetric,
  EndpointMetrics,
  ResourceMetrics,
  BaselineComparison,
  MetricType,
  PerformanceAlert
} from '../../../models/performance-metrics.model';

/**
 * Performance Metrics Dashboard Component
 * Displays performance baseline data with charts and metrics
 */
@Component({
  selector: 'app-performance-dashboard',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatProgressSpinnerModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatTableModule,
    MatTabsModule,
    MatDividerModule,
    NgChartsModule
  ],
  templateUrl: './performance-dashboard.component.html',
  styleUrls: ['./performance-dashboard.component.scss']
})
export class PerformanceDashboardComponent implements OnInit {
  @Input() analysisId!: string;

  baseline: PerformanceBaseline | null = null;
  loading = true;
  error: string | null = null;

  // Chart configurations
  responseTimeChartData: ChartConfiguration['data'] | null = null;
  throughputChartData: ChartConfiguration['data'] | null = null;
  resourceChartData: ChartConfiguration['data'] | null = null;
  endpointChartData: ChartConfiguration['data'] | null = null;

  responseTimeChartOptions: ChartConfiguration['options'];
  throughputChartOptions: ChartConfiguration['options'];
  resourceChartOptions: ChartConfiguration['options'];
  endpointChartOptions: ChartConfiguration['options'];

  lineChartType: ChartType = 'line';
  barChartType: ChartType = 'bar';

  // Table columns
  endpointColumns = ['endpoint', 'method', 'requests', 'avg_response', 'p95_response', 'error_rate', 'throughput'];
  comparisonColumns = ['metric', 'baseline', 'current', 'difference', 'status'];

  // Expose enum to template
  MetricType = MetricType;

  constructor(private performanceService: PerformanceService) {
    // Initialize chart options
    this.responseTimeChartOptions = this.createChartOptions('Response Time (ms)', 'Time', 'Milliseconds');
    this.throughputChartOptions = this.createChartOptions('Throughput (req/s)', 'Time', 'Requests/Second');
    this.resourceChartOptions = this.createChartOptions('Resource Usage (%)', 'Resource', 'Percentage');
    this.endpointChartOptions = this.createChartOptions('Endpoint Performance', 'Endpoint', 'Response Time (ms)');
  }

  ngOnInit(): void {
    this.loadBaseline();
  }

  /**
   * Load performance baseline from API
   */
  loadBaseline(): void {
    this.loading = true;
    this.error = null;

    this.performanceService.getBaseline(this.analysisId).subscribe({
      next: (data) => {
        this.baseline = data;
        this.loading = false;
        this.prepareChartData();
      },
      error: (err) => {
        this.error = 'Failed to load performance baseline. Please try again.';
        this.loading = false;
        console.error('Error loading baseline:', err);
      }
    });
  }

  /**
   * Prepare chart data from baseline
   */
  private prepareChartData(): void {
    if (!this.baseline) return;

    // Response time chart
    const responseTimeMetric = this.baseline.metrics.find(m => m.metric_type === MetricType.RESPONSE_TIME);
    if (responseTimeMetric) {
      this.responseTimeChartData = {
        labels: responseTimeMetric.data_points.map(dp => new Date(dp.timestamp).toLocaleTimeString()),
        datasets: [{
          label: 'Response Time',
          data: responseTimeMetric.data_points.map(dp => dp.value),
          borderColor: '#2196F3',
          backgroundColor: 'rgba(33, 150, 243, 0.1)',
          fill: true,
          tension: 0.4
        }]
      };
    }

    // Throughput chart
    const throughputMetric = this.baseline.metrics.find(m => m.metric_type === MetricType.THROUGHPUT);
    if (throughputMetric) {
      this.throughputChartData = {
        labels: throughputMetric.data_points.map(dp => new Date(dp.timestamp).toLocaleTimeString()),
        datasets: [{
          label: 'Throughput',
          data: throughputMetric.data_points.map(dp => dp.value),
          borderColor: '#4CAF50',
          backgroundColor: 'rgba(76, 175, 80, 0.1)',
          fill: true,
          tension: 0.4
        }]
      };
    }

    // Resource usage chart (CPU and Memory)
    const cpuMetric = this.baseline.metrics.find(m => m.metric_type === MetricType.CPU_USAGE);
    const memoryMetric = this.baseline.metrics.find(m => m.metric_type === MetricType.MEMORY_USAGE);

    if (cpuMetric && memoryMetric) {
      const labels = cpuMetric.data_points.map(dp => new Date(dp.timestamp).toLocaleTimeString());
      this.resourceChartData = {
        labels: labels,
        datasets: [
          {
            label: 'CPU Usage',
            data: cpuMetric.data_points.map(dp => dp.value),
            borderColor: '#FF9800',
            backgroundColor: 'rgba(255, 152, 0, 0.1)',
            fill: true,
            tension: 0.4
          },
          {
            label: 'Memory Usage',
            data: memoryMetric.data_points.map(dp => dp.value),
            borderColor: '#9C27B0',
            backgroundColor: 'rgba(156, 39, 176, 0.1)',
            fill: true,
            tension: 0.4
          }
        ]
      };
    }

    // Endpoint performance chart (top 10 by response time)
    if (this.baseline.endpoint_metrics.length > 0) {
      const topEndpoints = [...this.baseline.endpoint_metrics]
        .sort((a, b) => b.avg_response_time - a.avg_response_time)
        .slice(0, 10);

      this.endpointChartData = {
        labels: topEndpoints.map(e => `${e.method} ${e.endpoint}`),
        datasets: [{
          label: 'Avg Response Time',
          data: topEndpoints.map(e => e.avg_response_time),
          backgroundColor: '#2196F3'
        },
        {
          label: 'P95 Response Time',
          data: topEndpoints.map(e => e.p95_response_time),
          backgroundColor: '#FF9800'
        }]
      };
    }
  }

  /**
   * Create chart options
   */
  private createChartOptions(title: string, xLabel: string, yLabel: string): ChartConfiguration['options'] {
    return {
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: true,
          position: 'top'
        },
        title: {
          display: true,
          text: title
        }
      },
      scales: {
        x: {
          title: {
            display: true,
            text: xLabel
          }
        },
        y: {
          title: {
            display: true,
            text: yLabel
          },
          beginAtZero: true
        }
      }
    };
  }

  /**
   * Get health status color
   */
  getHealthColor(status: string): string {
    const colors: { [key: string]: string } = {
      'healthy': 'primary',
      'warning': 'accent',
      'critical': 'warn'
    };
    return colors[status] || '';
  }

  /**
   * Get comparison status color
   */
  getComparisonColor(comparison: BaselineComparison): string {
    if (!comparison.is_regression) return 'primary';
    
    switch (comparison.severity) {
      case 'critical': return 'warn';
      case 'major': return 'accent';
      default: return '';
    }
  }

  /**
   * Get metric status icon
   */
  getStatusIcon(status: string): string {
    const icons: { [key: string]: string } = {
      'healthy': 'check_circle',
      'warning': 'warning',
      'critical': 'error'
    };
    return icons[status] || 'info';
  }

  /**
   * Format number with commas
   */
  formatNumber(value: number): string {
    return value.toLocaleString('en-US', { maximumFractionDigits: 2 });
  }

  /**
   * Format percentage
   */
  formatPercent(value: number): string {
    return (value * 100).toFixed(2) + '%';
  }

  /**
   * Get performance alerts
   */
  getAlerts(): PerformanceAlert[] {
    if (!this.baseline) return [];

    const alerts: PerformanceAlert[] = [];

    this.baseline.metrics.forEach(metric => {
      if (metric.status === 'critical' || metric.status === 'warning') {
        const latestValue = metric.data_points[metric.data_points.length - 1]?.value || 0;
        alerts.push({
          alert_id: `alert-${metric.metric_type}`,
          metric_type: metric.metric_type,
          severity: metric.status as 'warning' | 'critical',
          message: `${metric.name} is ${metric.status}`,
          threshold_value: metric.threshold_critical || metric.threshold_warning || 0,
          actual_value: latestValue,
          timestamp: new Date().toISOString()
        });
      }
    });

    return alerts;
  }

  /**
   * Get resource utilization percentage
   */
  getResourceUtilization(type: 'cpu' | 'memory'): number {
    if (!this.baseline) return 0;
    
    if (type === 'cpu') {
      return this.baseline.resource_metrics.cpu_usage_percent;
    } else {
      return this.baseline.resource_metrics.memory_usage_percent;
    }
  }

  /**
   * Check if resource is critical
   */
  isResourceCritical(percentage: number): boolean {
    return percentage >= 90;
  }

  /**
   * Check if resource is warning
   */
  isResourceWarning(percentage: number): boolean {
    return percentage >= 75 && percentage < 90;
  }
}
