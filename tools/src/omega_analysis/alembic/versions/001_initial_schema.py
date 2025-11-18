"""Initial database schema migration with core tables and pg_vector extension.

Revision ID: 001_initial_schema
Revises: 
Create Date: 2024-11-17 18:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create initial database schema."""
    
    # Enable pg_vector extension
    op.execute('CREATE EXTENSION IF NOT EXISTS vector')
    
    # Create enum types
    analysis_status_enum = postgresql.ENUM(
        'PENDING', 'RUNNING', 'COMPLETED', 'FAILED', 'CANCELLED',
        name='analysis_status',
        create_type=False
    )
    analysis_status_enum.create(op.get_bind())
    
    analysis_type_enum = postgresql.ENUM(
        'STATIC_ANALYSIS', 'RUNTIME_ANALYSIS', 'DEPENDENCY_ANALYSIS', 'SECURITY_ANALYSIS', 'QUALITY_ANALYSIS',
        name='analysis_type',
        create_type=False
    )
    analysis_type_enum.create(op.get_bind())
    
    recommendation_type_enum = postgresql.ENUM(
        'MICROSERVICE_BOUNDARY', 'REFACTORING', 'SECURITY', 'PERFORMANCE', 'ARCHITECTURE',
        name='recommendation_type',
        create_type=False
    )
    recommendation_type_enum.create(op.get_bind())
    
    confidence_level_enum = postgresql.ENUM(
        'LOW', 'MEDIUM', 'HIGH', 'VERY_HIGH',
        name='confidence_level',
        create_type=False
    )
    confidence_level_enum.create(op.get_bind())
    
    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('repository_url', sa.String(1024)),
        sa.Column('local_path', sa.String(1024)),
        sa.Column('language', sa.String(50)),
        sa.Column('framework', sa.String(100)),
        sa.Column('build_tool', sa.String(50)),
        sa.Column('metadata', sa.JSON),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', sa.String(255)),
        sa.Column('updated_by', sa.String(255))
    )
    
    # Create index on projects
    op.create_index('ix_projects_name', 'projects', ['name'])
    op.create_index('ix_projects_language', 'projects', ['language'])
    op.create_index('ix_projects_framework', 'projects', ['framework'])
    op.create_index('ix_projects_created_at', 'projects', ['created_at'])
    
    # Create analyses table
    op.create_table(
        'analyses',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('analysis_type', analysis_type_enum, nullable=False),
        sa.Column('status', analysis_status_enum, nullable=False, default='PENDING'),
        sa.Column('configuration', sa.JSON),
        sa.Column('results', sa.JSON),
        sa.Column('metrics', sa.JSON),
        sa.Column('error_message', sa.Text),
        sa.Column('started_at', sa.DateTime(timezone=True)),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
        sa.Column('duration_seconds', sa.Integer),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', sa.String(255)),
        sa.Column('updated_by', sa.String(255))
    )
    
    # Create indexes on analyses
    op.create_index('ix_analyses_project_id', 'analyses', ['project_id'])
    op.create_index('ix_analyses_status', 'analyses', ['status'])
    op.create_index('ix_analyses_type', 'analyses', ['analysis_type'])
    op.create_index('ix_analyses_created_at', 'analyses', ['created_at'])
    op.create_index('ix_analyses_started_at', 'analyses', ['started_at'])
    
    # Create code_elements table
    op.create_table(
        'code_elements',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('analysis_id', sa.String(36), sa.ForeignKey('analyses.id', ondelete='CASCADE')),
        sa.Column('element_type', sa.String(50), nullable=False),  # class, method, package, etc.
        sa.Column('name', sa.String(512), nullable=False),
        sa.Column('fully_qualified_name', sa.String(1024)),
        sa.Column('file_path', sa.String(1024)),
        sa.Column('start_line', sa.Integer),
        sa.Column('end_line', sa.Integer),
        sa.Column('complexity_score', sa.Float),
        sa.Column('size_metrics', sa.JSON),
        sa.Column('dependencies', sa.JSON),
        sa.Column('metadata', sa.JSON),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create indexes on code_elements
    op.create_index('ix_code_elements_project_id', 'code_elements', ['project_id'])
    op.create_index('ix_code_elements_analysis_id', 'code_elements', ['analysis_id'])
    op.create_index('ix_code_elements_type', 'code_elements', ['element_type'])
    op.create_index('ix_code_elements_name', 'code_elements', ['name'])
    op.create_index('ix_code_elements_fqn', 'code_elements', ['fully_qualified_name'])
    
    # Create dependencies table
    op.create_table(
        'dependencies',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('analysis_id', sa.String(36), sa.ForeignKey('analyses.id', ondelete='CASCADE')),
        sa.Column('source_element_id', sa.String(36), sa.ForeignKey('code_elements.id', ondelete='CASCADE')),
        sa.Column('target_element_id', sa.String(36), sa.ForeignKey('code_elements.id', ondelete='CASCADE')),
        sa.Column('dependency_type', sa.String(50), nullable=False),  # method_call, inheritance, etc.
        sa.Column('strength', sa.Float),  # dependency strength score
        sa.Column('metadata', sa.JSON),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupload=sa.func.now())
    )
    
    # Create indexes on dependencies
    op.create_index('ix_dependencies_project_id', 'dependencies', ['project_id'])
    op.create_index('ix_dependencies_analysis_id', 'dependencies', ['analysis_id'])
    op.create_index('ix_dependencies_source', 'dependencies', ['source_element_id'])
    op.create_index('ix_dependencies_target', 'dependencies', ['target_element_id'])
    op.create_index('ix_dependencies_type', 'dependencies', ['dependency_type'])
    
    # Create recommendations table
    op.create_table(
        'recommendations',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('analysis_id', sa.String(36), sa.ForeignKey('analyses.id', ondelete='CASCADE')),
        sa.Column('recommendation_type', recommendation_type_enum, nullable=False),
        sa.Column('title', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('rationale', sa.Text),
        sa.Column('confidence_level', confidence_level_enum, nullable=False),
        sa.Column('confidence_score', sa.Float),
        sa.Column('impact_assessment', sa.JSON),
        sa.Column('implementation_steps', sa.JSON),
        sa.Column('affected_elements', sa.JSON),
        sa.Column('metadata', sa.JSON),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create indexes on recommendations
    op.create_index('ix_recommendations_project_id', 'recommendations', ['project_id'])
    op.create_index('ix_recommendations_analysis_id', 'recommendations', ['analysis_id'])
    op.create_index('ix_recommendations_type', 'recommendations', ['recommendation_type'])
    op.create_index('ix_recommendations_confidence', 'recommendations', ['confidence_level'])
    op.create_index('ix_recommendations_created_at', 'recommendations', ['created_at'])
    
    # Create analysis_artifacts table
    op.create_table(
        'analysis_artifacts',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('analysis_id', sa.String(36), sa.ForeignKey('analyses.id', ondelete='CASCADE'), nullable=False),
        sa.Column('artifact_type', sa.String(50), nullable=False),  # report, diagram, data_export, etc.
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('file_path', sa.String(1024)),
        sa.Column('storage_key', sa.String(1024)),  # MinIO object key
        sa.Column('content_type', sa.String(100)),
        sa.Column('size_bytes', sa.BigInteger),
        sa.Column('metadata', sa.JSON),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create indexes on analysis_artifacts
    op.create_index('ix_analysis_artifacts_analysis_id', 'analysis_artifacts', ['analysis_id'])
    op.create_index('ix_analysis_artifacts_type', 'analysis_artifacts', ['artifact_type'])
    op.create_index('ix_analysis_artifacts_created_at', 'analysis_artifacts', ['created_at'])
    
    # Create embeddings table for vector similarity search
    op.create_table(
        'embeddings',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.id', ondelete='CASCADE')),
        sa.Column('code_element_id', sa.String(36), sa.ForeignKey('code_elements.id', ondelete='CASCADE')),
        sa.Column('embedding_type', sa.String(50), nullable=False),  # code2vec, ast, etc.
        sa.Column('embedding_vector', postgresql.ARRAY(sa.Float), nullable=False),
        sa.Column('vector_embedding', sa.Text),  # For pg_vector
        sa.Column('dimension', sa.Integer),
        sa.Column('metadata', sa.JSON),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now())
    )
    
    # Create indexes on embeddings
    op.create_index('ix_embeddings_project_id', 'embeddings', ['project_id'])
    op.create_index('ix_embeddings_code_element_id', 'embeddings', ['code_element_id'])
    op.create_index('ix_embeddings_type', 'embeddings', ['embedding_type'])
    
    # Create pg_vector index for similarity search (after data is populated)
    # op.execute('CREATE INDEX ix_embeddings_vector ON embeddings USING ivfflat (vector_embedding vector_cosine_ops) WITH (lists = 100)')
    
    # Create analysis_sessions table for tracking long-running analysis workflows
    op.create_table(
        'analysis_sessions',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('project_id', sa.String(36), sa.ForeignKey('projects.id', ondelete='CASCADE'), nullable=False),
        sa.Column('session_name', sa.String(255)),
        sa.Column('status', analysis_status_enum, nullable=False, default='PENDING'),
        sa.Column('workflow_config', sa.JSON),
        sa.Column('progress', sa.JSON),
        sa.Column('started_at', sa.DateTime(timezone=True)),
        sa.Column('completed_at', sa.DateTime(timezone=True)),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('created_by', sa.String(255))
    )
    
    # Create indexes on analysis_sessions
    op.create_index('ix_analysis_sessions_project_id', 'analysis_sessions', ['project_id'])
    op.create_index('ix_analysis_sessions_status', 'analysis_sessions', ['status'])
    op.create_index('ix_analysis_sessions_created_at', 'analysis_sessions', ['created_at'])
    
    # Create analysis_session_analyses junction table
    op.create_table(
        'analysis_session_analyses',
        sa.Column('session_id', sa.String(36), sa.ForeignKey('analysis_sessions.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('analysis_id', sa.String(36), sa.ForeignKey('analyses.id', ondelete='CASCADE'), primary_key=True),
        sa.Column('sequence_order', sa.Integer),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    # Create system_settings table for configuration
    op.create_table(
        'system_settings',
        sa.Column('key', sa.String(255), primary_key=True),
        sa.Column('value', sa.JSON, nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('category', sa.String(100)),
        sa.Column('is_sensitive', sa.Boolean, default=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('updated_by', sa.String(255))
    )
    
    # Create index on system_settings
    op.create_index('ix_system_settings_category', 'system_settings', ['category'])
    
    # Create audit_log table for tracking changes
    op.create_table(
        'audit_log',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('table_name', sa.String(100), nullable=False),
        sa.Column('record_id', sa.String(36), nullable=False),
        sa.Column('operation', sa.String(20), nullable=False),  # INSERT, UPDATE, DELETE
        sa.Column('old_values', sa.JSON),
        sa.Column('new_values', sa.JSON),
        sa.Column('changed_by', sa.String(255)),
        sa.Column('changed_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('correlation_id', sa.String(36))
    )
    
    # Create indexes on audit_log
    op.create_index('ix_audit_log_table_record', 'audit_log', ['table_name', 'record_id'])
    op.create_index('ix_audit_log_changed_at', 'audit_log', ['changed_at'])
    op.create_index('ix_audit_log_changed_by', 'audit_log', ['changed_by'])
    op.create_index('ix_audit_log_correlation_id', 'audit_log', ['correlation_id'])


def downgrade() -> None:
    """Drop all tables and extensions."""
    
    # Drop tables in reverse dependency order
    op.drop_table('audit_log')
    op.drop_table('system_settings')
    op.drop_table('analysis_session_analyses')
    op.drop_table('analysis_sessions')
    op.drop_table('embeddings')
    op.drop_table('analysis_artifacts')
    op.drop_table('recommendations')
    op.drop_table('dependencies')
    op.drop_table('code_elements')
    op.drop_table('analyses')
    op.drop_table('projects')
    
    # Drop enum types
    op.execute('DROP TYPE IF EXISTS confidence_level')
    op.execute('DROP TYPE IF EXISTS recommendation_type')
    op.execute('DROP TYPE IF EXISTS analysis_type')
    op.execute('DROP TYPE IF EXISTS analysis_status')
    
    # Drop pg_vector extension
    op.execute('DROP EXTENSION IF EXISTS vector')