import { Component, Input, OnInit, OnDestroy, ElementRef, ViewChild, AfterViewInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatCardModule } from '@angular/material/card';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { MatChipsModule } from '@angular/material/chips';
import { MatSelectModule } from '@angular/material/select';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatExpansionModule } from '@angular/material/expansion';
import { MatDividerModule } from '@angular/material/divider';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { DependencyService } from '../../../services/dependency.service';
import {
  DependencyGraph,
  DependencyNode,
  DependencyEdge,
  CircularDependency,
  GraphVisualizationNode,
  GraphVisualizationEdge,
  DependencyType,
  CouplingStrength
} from '../../../models/dependency-graph.model';
import * as d3 from 'd3';

/**
 * Dependency Graph Visualization Component
 * Displays interactive dependency graph with D3.js hierarchical and force layouts
 */
@Component({
  selector: 'app-dependency-graph',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatCardModule,
    MatProgressSpinnerModule,
    MatButtonModule,
    MatIconModule,
    MatChipsModule,
    MatSelectModule,
    MatFormFieldModule,
    MatInputModule,
    MatExpansionModule,
    MatDividerModule,
    MatButtonToggleModule
  ],
  templateUrl: './dependency-graph.component.html',
  styleUrls: ['./dependency-graph.component.scss']
})
export class DependencyGraphComponent implements OnInit, OnDestroy, AfterViewInit {
  @Input() analysisId!: string;
  @ViewChild('graphContainer', { static: false }) graphContainer!: ElementRef;

  dependencyGraph: DependencyGraph | null = null;
  loading = true;
  error: string | null = null;

  selectedNode: DependencyNode | null = null;
  selectedEdge: DependencyEdge | null = null;
  searchTerm = '';
  
  // Filters
  layoutType: 'force' | 'hierarchy' = 'force';
  showExternal = true;
  showTransitive = true;
  filterType: DependencyType | 'all' = 'all';
  maxDepth = 0; // 0 = no limit

  // D3.js visualization
  private svg: any;
  private simulation: any;
  private graphData: { nodes: GraphVisualizationNode[], edges: GraphVisualizationEdge[] } | null = null;

  // Expose enums to template
  DependencyType = DependencyType;
  CouplingStrength = CouplingStrength;

  constructor(private dependencyService: DependencyService) {}

  ngOnInit(): void {
    this.loadDependencies();
  }

  ngAfterViewInit(): void {
    if (this.dependencyGraph && !this.svg) {
      this.initializeVisualization();
    }
  }

  ngOnDestroy(): void {
    if (this.simulation) {
      this.simulation.stop();
    }
  }

  /**
   * Load dependency graph from API
   */
  loadDependencies(): void {
    this.loading = true;
    this.error = null;

    this.dependencyService.getDependencies(this.analysisId).subscribe({
      next: (data) => {
        this.dependencyGraph = data;
        this.loading = false;
        if (this.graphContainer) {
          this.initializeVisualization();
        }
      },
      error: (err) => {
        this.error = 'Failed to load dependency graph. Please try again.';
        this.loading = false;
        console.error('Error loading dependencies:', err);
      }
    });
  }

  /**
   * Initialize D3.js visualization
   */
  private initializeVisualization(): void {
    if (!this.dependencyGraph || !this.graphContainer) {
      return;
    }

    // Convert to visualization format
    this.graphData = this.convertToVisualization(this.dependencyGraph);

    if (this.layoutType === 'force') {
      this.createForceLayout();
    } else {
      this.createHierarchicalLayout();
    }
  }

  /**
   * Create force-directed layout
   */
  private createForceLayout(): void {
    if (!this.graphData || !this.graphContainer) return;

    // Clear existing
    d3.select(this.graphContainer.nativeElement).select('svg').remove();

    const container = this.graphContainer.nativeElement;
    const width = container.clientWidth;
    const height = 700;

    this.svg = d3.select(container)
      .append('svg')
      .attr('width', width)
      .attr('height', height)
      .attr('viewBox', `0 0 ${width} ${height}`)
      .attr('preserveAspectRatio', 'xMidYMid meet');

    const g = this.svg.append('g');

    // Zoom
    const zoom = d3.zoom()
      .scaleExtent([0.1, 4])
      .on('zoom', (event: any) => g.attr('transform', event.transform));
    this.svg.call(zoom);

    // Force simulation
    this.simulation = d3.forceSimulation(this.graphData.nodes)
      .force('link', d3.forceLink(this.graphData.edges)
        .id((d: any) => d.id)
        .distance(150)
        .strength(0.3))
      .force('charge', d3.forceManyBody().strength(-400))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(40));

    // Links with arrows
    const defs = this.svg.append('defs');
    defs.append('marker')
      .attr('id', 'arrowhead')
      .attr('viewBox', '-0 -5 10 10')
      .attr('refX', 20)
      .attr('refY', 0)
      .attr('orient', 'auto')
      .attr('markerWidth', 8)
      .attr('markerHeight', 8)
      .append('svg:path')
      .attr('d', 'M 0,-5 L 10,0 L 0,5')
      .attr('fill', '#999');

    const link = g.append('g')
      .selectAll('line')
      .data(this.graphData.edges)
      .enter()
      .append('line')
      .attr('stroke', (d: any) => this.getEdgeColor(d.data))
      .attr('stroke-width', (d: any) => this.getEdgeWidth(d.data))
      .attr('stroke-opacity', 0.6)
      .attr('marker-end', 'url(#arrowhead)');

    // Nodes
    const node = g.append('g')
      .selectAll('g')
      .data(this.graphData.nodes)
      .enter()
      .append('g')
      .attr('class', 'node')
      .call(this.drag(this.simulation) as any);

    node.append('circle')
      .attr('r', (d: any) => d.size)
      .attr('fill', (d: any) => d.color || this.getNodeColor(d.data))
      .attr('stroke', '#fff')
      .attr('stroke-width', 2);

    node.append('text')
      .attr('dx', 15)
      .attr('dy', 4)
      .text((d: any) => d.label)
      .attr('font-size', '11px')
      .attr('fill', '#333');

    // Click handlers
    node.on('click', (event: any, d: any) => {
      event.stopPropagation();
      this.onNodeClick(d.data);
    });

    link.on('click', (event: any, d: any) => {
      event.stopPropagation();
      this.onEdgeClick(d.data);
    });

    // Simulation tick
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
   * Create hierarchical tree layout
   */
  private createHierarchicalLayout(): void {
    if (!this.graphData || !this.graphContainer) return;

    d3.select(this.graphContainer.nativeElement).select('svg').remove();

    const container = this.graphContainer.nativeElement;
    const width = container.clientWidth;
    const height = 800;

    this.svg = d3.select(container)
      .append('svg')
      .attr('width', width)
      .attr('height', height);

    const g = this.svg.append('g').attr('transform', 'translate(40,40)');

    // Build hierarchy from graph
    const hierarchy = this.buildHierarchy(this.graphData);
    
    const treeLayout = d3.tree()
      .size([height - 80, width - 160]);

    const root = d3.hierarchy(hierarchy);
    treeLayout(root);

    // Links
    g.selectAll('.link')
      .data(root.links())
      .enter()
      .append('path')
      .attr('class', 'link')
      .attr('d', d3.linkHorizontal()
        .x((d: any) => d.y)
        .y((d: any) => d.x) as any)
      .attr('fill', 'none')
      .attr('stroke', '#999')
      .attr('stroke-width', 2);

    // Nodes
    const nodes = g.selectAll('.node')
      .data(root.descendants())
      .enter()
      .append('g')
      .attr('class', 'node')
      .attr('transform', (d: any) => `translate(${d.y},${d.x})`);

    nodes.append('circle')
      .attr('r', 8)
      .attr('fill', (d: any) => this.getNodeColor(d.data.nodeData))
      .attr('stroke', '#fff')
      .attr('stroke-width', 2);

    nodes.append('text')
      .attr('dx', 12)
      .attr('dy', 4)
      .text((d: any) => d.data.name)
      .attr('font-size', '11px');

    nodes.on('click', (event: any, d: any) => {
      event.stopPropagation();
      if (d.data.nodeData) {
        this.onNodeClick(d.data.nodeData);
      }
    });
  }

  /**
   * Build hierarchy from flat graph structure
   */
  private buildHierarchy(graphData: { nodes: GraphVisualizationNode[], edges: GraphVisualizationEdge[] }): any {
    // Find root nodes (nodes with no incoming edges)
    const hasIncoming = new Set(graphData.edges.map(e => typeof e.target === 'string' ? e.target : e.target.id));
    const roots = graphData.nodes.filter(n => !hasIncoming.has(n.id));

    if (roots.length === 0 && graphData.nodes.length > 0) {
      // Use first node as root if no clear root
      return this.buildNodeHierarchy(graphData.nodes[0], graphData, new Set());
    }

    return {
      name: 'Root',
      nodeData: null,
      children: roots.map(root => this.buildNodeHierarchy(root, graphData, new Set()))
    };
  }

  /**
   * Recursively build hierarchy for a node
   */
  private buildNodeHierarchy(
    node: GraphVisualizationNode,
    graphData: { nodes: GraphVisualizationNode[], edges: GraphVisualizationEdge[] },
    visited: Set<string>
  ): any {
    if (visited.has(node.id)) {
      return { name: node.label + ' (circular)', nodeData: node.data, children: [] };
    }

    visited.add(node.id);

    const children = graphData.edges
      .filter(e => (typeof e.source === 'string' ? e.source : e.source.id) === node.id)
      .map(e => {
        const targetId = typeof e.target === 'string' ? e.target : e.target.id;
        const targetNode = graphData.nodes.find(n => n.id === targetId);
        return targetNode ? this.buildNodeHierarchy(targetNode, graphData, new Set(visited)) : null;
      })
      .filter(c => c !== null);

    return {
      name: node.label,
      nodeData: node.data,
      children: children
    };
  }

  /**
   * Convert DependencyGraph to visualization format
   */
  private convertToVisualization(graph: DependencyGraph): { nodes: GraphVisualizationNode[], edges: GraphVisualizationEdge[] } {
    // Filter nodes
    let nodes = graph.nodes.filter(n => {
      if (!this.showExternal && n.is_external) return false;
      return true;
    });

    // Filter edges
    let edges = graph.edges.filter(e => {
      if (!this.showTransitive && e.dependency_type === DependencyType.TRANSITIVE) return false;
      if (this.filterType !== 'all' && e.dependency_type !== this.filterType) return false;
      return true;
    });

    const vizNodes: GraphVisualizationNode[] = nodes.map(n => ({
      id: n.id,
      label: n.name,
      type: n.type,
      group: n.group || n.type,
      size: this.calculateNodeSize(n),
      data: n
    }));

    const vizEdges: GraphVisualizationEdge[] = edges.map(e => ({
      source: e.source_id,
      target: e.target_id,
      type: e.dependency_type,
      strength: this.calculateEdgeStrength(e),
      data: e
    }));

    return { nodes: vizNodes, edges: vizEdges };
  }

  /**
   * Calculate node size based on degree
   */
  private calculateNodeSize(node: DependencyNode): number {
    const degree = node.in_degree + node.out_degree;
    return Math.min(10 + degree * 2, 30);
  }

  /**
   * Calculate edge strength
   */
  private calculateEdgeStrength(edge: DependencyEdge): number {
    switch (edge.coupling_strength) {
      case CouplingStrength.TIGHT: return 0.9;
      case CouplingStrength.MODERATE: return 0.5;
      case CouplingStrength.LOOSE: return 0.2;
      default: return 0.5;
    }
  }

  /**
   * Get node color
   */
  private getNodeColor(node: DependencyNode): string {
    if (node.is_external) return '#FF5722';
    if (node.has_vulnerabilities) return '#F44336';
    
    const colors: { [key: string]: string } = {
      'package': '#4CAF50',
      'module': '#2196F3',
      'class': '#FF9800',
      'component': '#9C27B0',
      'external': '#FF5722'
    };
    return colors[node.type] || '#607D8B';
  }

  /**
   * Get edge color
   */
  private getEdgeColor(edge: DependencyEdge): string {
    if (edge.is_circular) return '#F44336';
    if (edge.is_problematic) return '#FF9800';
    
    switch (edge.coupling_strength) {
      case CouplingStrength.TIGHT: return '#F44336';
      case CouplingStrength.MODERATE: return '#FF9800';
      case CouplingStrength.LOOSE: return '#4CAF50';
      default: return '#999';
    }
  }

  /**
   * Get edge width
   */
  private getEdgeWidth(edge: DependencyEdge): number {
    const base = edge.usage_count ? Math.log10(edge.usage_count + 1) : 1;
    return Math.min(base * 2, 5);
  }

  /**
   * Handle node click
   */
  onNodeClick(node: DependencyNode): void {
    this.selectedNode = node;
    this.selectedEdge = null;
  }

  /**
   * Handle edge click
   */
  onEdgeClick(edge: DependencyEdge): void {
    this.selectedEdge = edge;
    this.selectedNode = null;
  }

  /**
   * Get edges connected to selected node
   */
  getConnectedEdges(): DependencyEdge[] {
    if (!this.selectedNode || !this.dependencyGraph) return [];
    
    return this.dependencyGraph.edges.filter(
      e => e.source_id === this.selectedNode!.id || e.target_id === this.selectedNode!.id
    );
  }

  /**
   * Close details panel
   */
  closeDetails(): void {
    this.selectedNode = null;
    this.selectedEdge = null;
  }

  /**
   * Apply filters and refresh visualization
   */
  applyFilters(): void {
    this.initializeVisualization();
  }

  /**
   * Change layout type
   */
  changeLayout(type: 'force' | 'hierarchy'): void {
    this.layoutType = type;
    this.initializeVisualization();
  }

  /**
   * Reset view
   */
  resetView(): void {
    if (this.svg) {
      this.svg.transition()
        .duration(750)
        .call(d3.zoom().transform, d3.zoomIdentity);
    }
  }

  /**
   * Search dependencies
   */
  searchDependencies(): void {
    if (!this.searchTerm || !this.dependencyGraph) return;
    
    const term = this.searchTerm.toLowerCase();
    const found = this.dependencyGraph.nodes.find(n => 
      n.name.toLowerCase().includes(term) || 
      n.namespace?.toLowerCase().includes(term)
    );
    
    if (found) {
      this.selectedNode = found;
    }
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
   * Get circular dependencies
   */
  getCircularDependencies(): CircularDependency[] {
    return this.dependencyGraph?.circular_dependencies || [];
  }

  /**
   * Get dependency type display name
   */
  getDependencyTypeDisplay(type: string): string {
    return type.replace('_', ' ').toUpperCase();
  }
}
