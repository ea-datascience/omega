export interface AnalysisProject {
  id: string;
  name: string;
  description: string;
  repository_url: string;
  codebase_path: string;
  status: 'pending' | 'in_progress' | 'completed' | 'failed';
  created_at: string;
  updated_at: string;
  metadata: {
    language?: string;
    framework?: string;
    lines_of_code?: number;
  };
}

export interface ProjectListResponse {
  projects: AnalysisProject[];
  total: number;
  page: number;
  page_size: number;
}
