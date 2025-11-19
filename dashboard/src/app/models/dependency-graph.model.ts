/**
 * Dependency Graph Models
 * 
 * TypeScript interfaces for system dependency visualization
 * Matches backend DependencyGraph schema
 */

/**
 * Dependency type classification
 */
export enum DependencyType {
  DIRECT = 'direct',
  TRANSITIVE = 'transitive',
  COMPILE = 'compile',
  RUNTIME = 'runtime',
  PROVIDED = 'provided',
  TEST = 'test'
}

/**
 * Dependency strength/coupling indicator
 */
export enum CouplingStrength {
  TIGHT = 'tight',
  MODERATE = 'moderate',
  LOOSE = 'loose'
}

/**
 * Node in the dependency graph
 */
export interface DependencyNode {
  id: string;
  name: string;
  type: 'package' | 'class' | 'module' | 'component' | 'external';
  group?: string;
  
  // Metadata
  version?: string;
  namespace?: string;
  package_path?: string;
  
  // Metrics
  in_degree: number;  // Number of dependencies on this node
  out_degree: number; // Number of dependencies from this node
  centrality_score?: number;
  
  // Flags
  is_external: boolean;
  is_deprecated?: boolean;
  has_vulnerabilities?: boolean;
}

/**
 * Edge representing a dependency relationship
 */
export interface DependencyEdge {
  id: string;
  source_id: string;
  target_id: string;
  dependency_type: DependencyType;
  coupling_strength: CouplingStrength;
  
  // Metadata
  usage_count?: number;
  call_sites?: string[];
  
  // Flags
  is_circular?: boolean;
  is_problematic?: boolean;
}

/**
 * Circular dependency cycle
 */
export interface CircularDependency {
  cycle_id: string;
  nodes: string[]; // Node IDs in cycle order
  severity: 'low' | 'medium' | 'high';
  description: string;
}

/**
 * Dependency metrics and statistics
 */
export interface DependencyMetrics {
  total_nodes: number;
  total_edges: number;
  external_dependencies: number;
  internal_dependencies: number;
  circular_dependencies: number;
  
  average_in_degree: number;
  average_out_degree: number;
  max_depth: number;
  
  coupling_score: number;
  cohesion_score: number;
  stability_score: number;
}

/**
 * Dependency layer in architecture
 */
export interface DependencyLayer {
  name: string;
  depth: number;
  nodes: string[]; // Node IDs
  description?: string;
}

/**
 * Complete dependency graph data
 */
export interface DependencyGraph {
  analysis_id: string;
  project_name: string;
  
  // Graph structure
  nodes: DependencyNode[];
  edges: DependencyEdge[];
  
  // Analysis results
  circular_dependencies?: CircularDependency[];
  layers?: DependencyLayer[];
  
  // Metrics
  metrics: DependencyMetrics;
  
  // Metadata
  analyzed_at: string;
  analysis_tool: string;
  scope: 'full' | 'internal' | 'external';
}

/**
 * Graph visualization node (D3.js compatible)
 */
export interface GraphVisualizationNode {
  id: string;
  label: string;
  type: string;
  group: string;
  size: number;
  color?: string;
  
  // D3 simulation properties
  x?: number;
  y?: number;
  vx?: number;
  vy?: number;
  fx?: number | null;
  fy?: number | null;
  
  // Additional data
  data: DependencyNode;
}

/**
 * Graph visualization edge (D3.js compatible)
 */
export interface GraphVisualizationEdge {
  source: string | GraphVisualizationNode;
  target: string | GraphVisualizationNode;
  type: string;
  strength: number;
  color?: string;
  
  // Additional data
  data: DependencyEdge;
}

/**
 * Dependency graph layout configuration
 */
export interface GraphLayoutConfig {
  layout_type: 'force' | 'hierarchy' | 'circular' | 'layered';
  show_external: boolean;
  show_transitive: boolean;
  max_depth?: number;
  filter_type?: string;
}

/**
 * Search/filter result
 */
export interface DependencySearchResult {
  node: DependencyNode;
  path: string[];
  distance: number;
  relevance_score: number;
}
