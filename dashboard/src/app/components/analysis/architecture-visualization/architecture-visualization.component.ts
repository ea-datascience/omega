import { Component, Input, OnInit, OnDestroy, ElementRef, ViewChild, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatCardModule } from '@angular/material/card';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatDividerModule } from '@angular/material/divider';
import { ArchitectureService } from '../../../services/architecture.service';
import { 
  SystemArchitecture, 
  ArchitectureComponent, 
  ComponentRelationship,
  GraphNode,
  GraphLink,
  ArchitectureGraph
} from '../../../models/architecture.model';
import * as d3 from 'd3';

/**
 * Architecture Visualization Component
 * Displays interactive system architecture graph with D3.js
 */
@Component({
  selector: 'app-architecture-visualization',
  standalone: true,
  imports: [
    CommonModule,
    MatCardModule,
    MatProgressSpinnerModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatSelectModule,
    MatFormFieldModule,
    MatExpansionModule,
    MatDividerModule
  ],
  templateUrl: './architecture-visualization.component.html',
  styleUrls: ['./architecture-visualization.component.scss']
})
export class ArchitectureVisualizationComponent implements OnInit, OnDestroy, AfterViewInit {
  @Input() analysisId!: string;
  @ViewChild('graphContainer', { static: false }) graphContainer!: ElementRef;

  architecture: SystemArchitecture | null = null;
  loading = true;
  error: string | null = null;
  
  selectedComponent: ArchitectureComponent | null = null;
  filterType: string = 'all';
  
  // D3.js visualization
  private svg: any;
  private simulation: any;
  private graphData: ArchitectureGraph | null = null;

  constructor(private architectureService: ArchitectureService) {}

  ngOnInit(): void {
    this.loadArchitecture();
  }

  ngAfterViewInit(): void {
    if (this.architecture && !this.svg) {
      this.initializeVisualization();
    }
  }

  ngOnDestroy(): void {
    if (this.simulation) {
      this.simulation.stop();
    }
  }

  /**
   * Load architecture data from API
   */
  loadArchitecture(): void {
    this.loading = true;
    this.error = null;

    this.architectureService.getArchitecture(this.analysisId).subscribe({
      next: (data) => {
        this.architecture = data;
        this.loading = false;
        if (this.graphContainer) {
          this.initializeVisualization();
        }
      },
      error: (err) => {
        this.error = 'Failed to load architecture data. Please try again.';
        this.loading = false;
        console.error('Error loading architecture:', err);
      }
    });
  }

  /**
   * Initialize D3.js force-directed graph
   */
  private initializeVisualization(): void {
    if (!this.architecture || !this.graphContainer) {
      return;
    }

    // Convert architecture data to graph format
    this.graphData = this.convertToGraph(this.architecture);

    // Clear any existing SVG
    d3.select(this.graphContainer.nativeElement).select('svg').remove();

    const container = this.graphContainer.nativeElement;
    const width = container.clientWidth;
    const height = 600;

    // Create SVG
    this.svg = d3.select(container)
      .append('svg')
      .attr('width', width)
      .attr('height', height)
      .attr('viewBox', `0 0 ${width} ${height}`)
      .attr('preserveAspectRatio', 'xMidYMid meet');

    // Add zoom behavior
    const g = this.svg.append('g');
    const zoom = d3.zoom()
      .scaleExtent([0.1, 4])
      .on('zoom', (event: any) => {
        g.attr('transform', event.transform);
      });
    this.svg.call(zoom);

    // Create force simulation
    this.simulation = d3.forceSimulation(this.graphData.nodes)
      .force('link', d3.forceLink(this.graphData.links)
        .id((d: any) => d.id)
        .distance(100)
        .strength((d: any) => d.strength * 0.5))
      .force('charge', d3.forceManyBody().strength(-300))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(30));

    // Create links
    const link = g.append('g')
      .attr('class', 'links')
      .selectAll('line')
      .data(this.graphData.links)
      .enter()
      .append('line')
      .attr('class', 'link')
      .attr('stroke', '#999')
      .attr('stroke-opacity', 0.6)
      .attr('stroke-width', (d: any) => Math.sqrt(d.strength * 5));

    // Create nodes
    const node = g.append('g')
      .attr('class', 'nodes')
      .selectAll('g')
      .data(this.graphData.nodes)
      .enter()
      .append('g')
      .attr('class', 'node')
      .call(this.drag(this.simulation) as any);

    // Add circles for nodes
    node.append('circle')
      .attr('r', (d: any) => d.size || 10)
      .attr('fill', (d: any) => d.color || this.getNodeColor(d.type))
      .attr('stroke', '#fff')
      .attr('stroke-width', 2);

    // Add labels
    node.append('text')
      .attr('dx', 12)
      .attr('dy', 4)
      .text((d: any) => d.label)
      .attr('font-size', '12px')
      .attr('fill', '#333');

    // Add node click handler
    node.on('click', (event: any, d: any) => {
      event.stopPropagation();
      this.onNodeClick(d.id);
    });

    // Update positions on simulation tick
    this.simulation.on('tick', () => {
      link
        .attr('x1', (d: any) => d.source.x)
        .attr('y1', (d: any) => d.source.y)
        .attr('x2', (d: any) => d.target.x)
        .attr('y2', (d: any) => d.target.y);

      node.attr('transform', (d: any) => `translate(${d.x},${d.y})`);
    });
  }

  /**
   * Convert SystemArchitecture to graph data structure
   */
  private convertToGraph(architecture: SystemArchitecture): ArchitectureGraph {
    const nodes: GraphNode[] = architecture.components.map(comp => ({
      id: comp.id,
      label: comp.name,
      type: comp.type,
      group: comp.is_candidate_service ? 'service-candidate' : comp.type,
      size: this.calculateNodeSize(comp)
    }));

    const links: GraphLink[] = architecture.relationships.map(rel => ({
      source: rel.source_id,
      target: rel.target_id,
      type: rel.relationship_type,
      strength: rel.strength,
      label: rel.relationship_type
    }));

    return { nodes, links };
  }

  /**
   * Calculate node size based on component metrics
   */
  private calculateNodeSize(component: ArchitectureComponent): number {
    const baseSize = 10;
    const lineCount = component.line_count || 0;
    const sizeMultiplier = Math.log10(lineCount + 1) * 2;
    return Math.min(baseSize + sizeMultiplier, 30);
  }

  /**
   * Get color for node based on type
   */
  private getNodeColor(type: string): string {
    const colors: { [key: string]: string } = {
      'module': '#4CAF50',
      'service': '#2196F3',
      'controller': '#FF9800',
      'repository': '#9C27B0',
      'component': '#607D8B',
      'service-candidate': '#F44336'
    };
    return colors[type] || '#999';
  }

  /**
   * Handle node click event
   */
  onNodeClick(nodeId: string): void {
    const component = this.architecture?.components.find(c => c.id === nodeId);
    if (component) {
      this.selectedComponent = component;
    }
  }

  /**
   * Get relationships for selected component
   */
  getComponentRelationships(): ComponentRelationship[] {
    if (!this.selectedComponent || !this.architecture) {
      return [];
    }
    return this.architecture.relationships.filter(
      r => r.source_id === this.selectedComponent!.id || r.target_id === this.selectedComponent!.id
    );
  }

  /**
   * Close component details panel
   */
  closeDetails(): void {
    this.selectedComponent = null;
  }

  /**
   * D3 drag behavior
   */
  private drag(simulation: any) {
    function dragstarted(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0.3).restart();
      d.fx = d.x;
      d.fy = d.y;
    }

    function dragged(event: any, d: any) {
      d.fx = event.x;
      d.fy = event.y;
    }

    function dragended(event: any, d: any) {
      if (!event.active) simulation.alphaTarget(0);
      d.fx = null;
      d.fy = null;
    }

    return d3.drag()
      .on('start', dragstarted)
      .on('drag', dragged)
      .on('end', dragended);
  }

  /**
   * Reset graph view
   */
  resetView(): void {
    if (this.svg) {
      this.svg.transition()
        .duration(750)
        .call(
          d3.zoom().transform,
          d3.zoomIdentity
        );
    }
  }

  /**
   * Get component type display name
   */
  getComponentTypeDisplay(type: string): string {
    return type.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
  }
}
