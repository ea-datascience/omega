/**
 * Architecture Visualization Models
 * 
 * TypeScript interfaces for system architecture visualization
 * Matches backend ArchitectureDiscovery schema
 */

/**
 * Technology stack information for a component
 */
export interface TechnologyStack {
  languages: string[];
  frameworks: string[];
  libraries: string[];
  databases?: string[];
  messaging?: string[];
}

/**
 * Component or module in the system architecture
 */
export interface ArchitectureComponent {
  id: string;
  name: string;
  type: 'module' | 'package' | 'class' | 'service' | 'repository' | 'controller' | 'component';
  description?: string;
  technology_stack?: TechnologyStack;
  responsibilities: string[];
  
  // Boundaries and scope
  package_path?: string;
  class_count?: number;
  line_count?: number;
  
  // Metadata
  is_candidate_service?: boolean;
  cohesion_score?: number;
  coupling_score?: number;
}

/**
 * Relationship between architecture components
 */
export interface ComponentRelationship {
  id: string;
  source_id: string;
  target_id: string;
  relationship_type: 'depends_on' | 'calls' | 'imports' | 'extends' | 'implements' | 'aggregates' | 'composes';
  strength: number; // 0.0 to 1.0
  description?: string;
  
  // Interaction metadata
  call_count?: number;
  data_shared?: string[];
}

/**
 * Service candidate identified during decomposition analysis
 */
export interface ServiceCandidate {
  id: string;
  name: string;
  description: string;
  components: string[]; // Component IDs
  bounded_context?: string;
  
  // Metrics
  cohesion_score: number;
  coupling_score: number;
  size_estimate: {
    classes: number;
    lines_of_code: number;
  };
  
  // Recommendations
  confidence_score: number;
  migration_complexity: 'low' | 'medium' | 'high';
  recommended_priority: number;
}

/**
 * Layered architecture pattern information
 */
export interface ArchitectureLayer {
  name: string;
  components: string[]; // Component IDs
  responsibilities: string[];
  dependencies: string[]; // Layer names this layer depends on
}

/**
 * Complete architecture visualization data
 */
export interface SystemArchitecture {
  analysis_id: string;
  project_name: string;
  
  // Architecture components
  components: ArchitectureComponent[];
  relationships: ComponentRelationship[];
  
  // Architecture patterns
  layers?: ArchitectureLayer[];
  service_candidates?: ServiceCandidate[];
  
  // Statistics
  statistics: {
    total_components: number;
    total_relationships: number;
    average_cohesion: number;
    average_coupling: number;
    cyclomatic_complexity?: number;
  };
  
  // Metadata
  discovered_at: string;
  discovery_tool: string;
  analysis_version: string;
}

/**
 * Graph visualization node (D3.js compatible)
 */
export interface GraphNode {
  id: string;
  label: string;
  type: string;
  group?: string;
  size?: number;
  color?: string;
  x?: number;
  y?: number;
  fx?: number | null;
  fy?: number | null;
}

/**
 * Graph visualization link (D3.js compatible)
 */
export interface GraphLink {
  source: string | GraphNode;
  target: string | GraphNode;
  type: string;
  strength: number;
  label?: string;
}

/**
 * Graph visualization data
 */
export interface ArchitectureGraph {
  nodes: GraphNode[];
  links: GraphLink[];
}
