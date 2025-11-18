"""SQLAlchemy models for Omega Analysis system."""
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Integer, Float, Text, DateTime, ForeignKey, Enum as SQLEnum, Boolean
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship, declarative_base
from sqlalchemy.sql import func
import enum

from .base import Base


class ProjectStatus(enum.Enum):
    """Analysis project status enumeration."""
    QUEUED = "queued"
    RUNNING = "running" 
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ValidationStatus(enum.Enum):
    """Validation status enumeration."""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVIEW = "needs_review"


class SystemType(enum.Enum):
    """Target system type enumeration."""
    SPRING_BOOT = "spring_boot"
    SPRING_MVC = "spring_mvc" 
    JAVA_EE = "java_ee"
    OTHER = "other"


class ArchitectureStyle(enum.Enum):
    """Architecture style enumeration."""
    LAYERED = "layered"
    MODULAR_MONOLITH = "modular_monolith"
    MICROSERVICES = "microservices"
    HYBRID = "hybrid"
    UNKNOWN = "unknown"


class GraphType(enum.Enum):
    """Dependency graph type enumeration."""
    STATIC = "static"
    RUNTIME = "runtime"
    COMBINED = "combined"


class EnvironmentType(enum.Enum):
    """Environment type enumeration."""
    PRODUCTION = "production"
    STAGING = "staging"
    DEVELOPMENT = "development"
    SYNTHETIC = "synthetic"


class AnalysisProject(Base):
    """Analysis project entity - represents a single monolith analysis session."""
    
    __tablename__ = "analysis_projects"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    repository_url = Column(String(512), nullable=False)
    repository_branch = Column(String(128), default="main")
    target_system_type = Column(SQLEnum(SystemType), nullable=False)
    analysis_configuration = Column(JSONB, nullable=False)
    status = Column(SQLEnum(ProjectStatus), nullable=False, default=ProjectStatus.QUEUED)
    progress_percentage = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at = Column(DateTime(timezone=True))
    created_by = Column(String(128), nullable=False)
    validation_status = Column(SQLEnum(ValidationStatus), default=ValidationStatus.PENDING)
    validation_notes = Column(Text)
    
    # Relationships
    system_architectures = relationship("SystemArchitecture", back_populates="analysis_project", cascade="all, delete-orphan")
    dependency_graphs = relationship("DependencyGraph", back_populates="analysis_project", cascade="all, delete-orphan")
    performance_baselines = relationship("PerformanceBaseline", back_populates="analysis_project", cascade="all, delete-orphan")
    risk_assessments = relationship("RiskAssessment", back_populates="analysis_project", cascade="all, delete-orphan")
    compliance_records = relationship("ComplianceRecord", back_populates="analysis_project", cascade="all, delete-orphan")
    service_boundaries = relationship("ServiceBoundary", back_populates="analysis_project", cascade="all, delete-orphan")


class SystemArchitecture(Base):
    """System architecture entity - discovered architectural patterns and components."""
    
    __tablename__ = "system_architectures"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_project_id = Column(UUID(as_uuid=True), ForeignKey("analysis_projects.id"), nullable=False)
    architecture_style = Column(SQLEnum(ArchitectureStyle), nullable=False)
    domain_model = Column(JSONB, nullable=False)
    c4_model = Column(JSONB, nullable=False)
    technology_stack = Column(JSONB, nullable=False)
    architectural_patterns = Column(JSONB, nullable=False)
    quality_metrics = Column(JSONB, nullable=False)
    documentation_coverage = Column(Float)
    test_coverage = Column(Float)
    generated_diagrams = Column(JSONB, nullable=False)
    discovered_at = Column(DateTime(timezone=True), server_default=func.now())
    tool_versions = Column(JSONB, nullable=False)
    
    # Relationships
    analysis_project = relationship("AnalysisProject", back_populates="system_architectures")
    architectural_components = relationship("ArchitecturalComponent", back_populates="system_architecture", cascade="all, delete-orphan")


class DependencyGraph(Base):
    """Dependency graph entity - maps dependencies between modules and external systems."""
    
    __tablename__ = "dependency_graphs"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_project_id = Column(UUID(as_uuid=True), ForeignKey("analysis_projects.id"), nullable=False)
    graph_type = Column(SQLEnum(GraphType), nullable=False)
    nodes = Column(JSONB, nullable=False)
    edges = Column(JSONB, nullable=False)
    coupling_metrics = Column(JSONB, nullable=False)
    external_dependencies = Column(JSONB, nullable=False)
    data_dependencies = Column(JSONB, nullable=False)
    circular_dependencies = Column(JSONB, nullable=False)
    critical_path_analysis = Column(JSONB, nullable=False)
    confidence_score = Column(Float)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    validation_status = Column(SQLEnum(ValidationStatus), default=ValidationStatus.PENDING)
    
    # Relationships
    analysis_project = relationship("AnalysisProject", back_populates="dependency_graphs")
    dependency_relations = relationship("DependencyRelation", back_populates="dependency_graph", cascade="all, delete-orphan")


class PerformanceBaseline(Base):
    """Performance baseline entity - collected metrics including response times and throughput."""
    
    __tablename__ = "performance_baselines"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_project_id = Column(UUID(as_uuid=True), ForeignKey("analysis_projects.id"), nullable=False)
    collection_period_start = Column(DateTime(timezone=True), nullable=False)
    collection_period_end = Column(DateTime(timezone=True), nullable=False)
    environment_type = Column(SQLEnum(EnvironmentType), nullable=False)
    load_characteristics = Column(JSONB, nullable=False)
    response_time_metrics = Column(JSONB, nullable=False)
    throughput_metrics = Column(JSONB, nullable=False)
    error_rate_metrics = Column(JSONB, nullable=False)
    resource_utilization = Column(JSONB, nullable=False)
    database_performance = Column(JSONB, nullable=False)
    external_service_metrics = Column(JSONB, nullable=False)
    statistical_confidence = Column(Float)
    sample_size = Column(Integer, nullable=False)
    data_quality_score = Column(Float)
    
    # Relationships
    analysis_project = relationship("AnalysisProject", back_populates="performance_baselines")
    metric_measurements = relationship("MetricMeasurement", back_populates="performance_baseline", cascade="all, delete-orphan")


class RiskAssessment(Base):
    """Risk assessment entity - identified migration risks and mitigation strategies."""
    
    __tablename__ = "risk_assessments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_project_id = Column(UUID(as_uuid=True), ForeignKey("analysis_projects.id"), nullable=False)
    technical_risks = Column(JSONB, nullable=False)
    business_risks = Column(JSONB, nullable=False)
    operational_risks = Column(JSONB, nullable=False)
    overall_risk_score = Column(Float)
    risk_matrix = Column(JSONB, nullable=False)
    mitigation_strategies = Column(JSONB, nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    analysis_project = relationship("AnalysisProject", back_populates="risk_assessments")
    risk_factors = relationship("RiskFactor", back_populates="risk_assessment", cascade="all, delete-orphan")


class ComplianceRecord(Base):
    """Compliance record entity - security and regulatory compliance findings."""
    
    __tablename__ = "compliance_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_project_id = Column(UUID(as_uuid=True), ForeignKey("analysis_projects.id"), nullable=False)
    compliance_frameworks = Column(JSONB, nullable=False)
    security_findings = Column(JSONB, nullable=False)
    privacy_findings = Column(JSONB, nullable=False)
    regulatory_findings = Column(JSONB, nullable=False)
    compliance_score = Column(Float)
    findings_summary = Column(JSONB, nullable=False)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    analysis_project = relationship("AnalysisProject", back_populates="compliance_records")
    compliance_requirements = relationship("ComplianceRequirement", back_populates="compliance_record", cascade="all, delete-orphan")


class ServiceBoundary(Base):
    """Service boundary entity - recommended microservice boundaries."""
    
    __tablename__ = "service_boundaries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_project_id = Column(UUID(as_uuid=True), ForeignKey("analysis_projects.id"), nullable=False)
    boundary_name = Column(String(255), nullable=False)
    boundary_type = Column(String(128), nullable=False)
    domain_context = Column(String(255), nullable=False)
    components = Column(JSONB, nullable=False)
    interfaces = Column(JSONB, nullable=False)
    data_ownership = Column(JSONB, nullable=False)
    cohesion_score = Column(Float)
    coupling_score = Column(Float)
    confidence_score = Column(Float)
    splitting_rationale = Column(Text)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    analysis_project = relationship("AnalysisProject", back_populates="service_boundaries")
    boundary_metrics = relationship("BoundaryMetric", back_populates="service_boundary", cascade="all, delete-orphan")


# Supporting entities
class ArchitecturalComponent(Base):
    """Architectural component entity - individual components within system architecture."""
    
    __tablename__ = "architectural_components"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    system_architecture_id = Column(UUID(as_uuid=True), ForeignKey("system_architectures.id"), nullable=False)
    component_name = Column(String(255), nullable=False)
    component_type = Column(String(128), nullable=False)
    location = Column(String(512))
    responsibilities = Column(JSONB)
    dependencies = Column(JSONB)
    quality_metrics = Column(JSONB)
    
    # Relationships
    system_architecture = relationship("SystemArchitecture", back_populates="architectural_components")


class DependencyRelation(Base):
    """Dependency relation entity - individual dependencies within dependency graph."""
    
    __tablename__ = "dependency_relations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    dependency_graph_id = Column(UUID(as_uuid=True), ForeignKey("dependency_graphs.id"), nullable=False)
    source_component = Column(String(255), nullable=False)
    target_component = Column(String(255), nullable=False)
    dependency_type = Column(String(128), nullable=False)
    strength = Column(Float)
    direction = Column(String(32))
    
    # Relationships
    dependency_graph = relationship("DependencyGraph", back_populates="dependency_relations")


class MetricMeasurement(Base):
    """Metric measurement entity - individual performance measurements."""
    
    __tablename__ = "metric_measurements"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    performance_baseline_id = Column(UUID(as_uuid=True), ForeignKey("performance_baselines.id"), nullable=False)
    metric_name = Column(String(255), nullable=False)
    metric_type = Column(String(128), nullable=False)
    metric_value = Column(Float, nullable=False)
    measurement_time = Column(DateTime(timezone=True), nullable=False)
    measurement_metadata = Column(JSONB)
    
    # Relationships
    performance_baseline = relationship("PerformanceBaseline", back_populates="metric_measurements")


class RiskFactor(Base):
    """Risk factor entity - individual risk factors within risk assessment."""
    
    __tablename__ = "risk_factors"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    risk_assessment_id = Column(UUID(as_uuid=True), ForeignKey("risk_assessments.id"), nullable=False)
    risk_category = Column(String(128), nullable=False)
    risk_name = Column(String(255), nullable=False)
    probability = Column(Float)
    impact = Column(Float)
    severity = Column(String(32))
    mitigation_plan = Column(Text)
    
    # Relationships
    risk_assessment = relationship("RiskAssessment", back_populates="risk_factors")


class ComplianceRequirement(Base):
    """Compliance requirement entity - individual compliance requirements."""
    
    __tablename__ = "compliance_requirements"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    compliance_record_id = Column(UUID(as_uuid=True), ForeignKey("compliance_records.id"), nullable=False)
    framework = Column(String(128), nullable=False)
    requirement_id = Column(String(128), nullable=False)
    requirement_name = Column(String(255), nullable=False)
    compliance_status = Column(String(32))
    finding_details = Column(Text)
    
    # Relationships
    compliance_record = relationship("ComplianceRecord", back_populates="compliance_requirements")


class BoundaryMetric(Base):
    """Boundary metric entity - metrics for service boundary recommendations."""
    
    __tablename__ = "boundary_metrics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_boundary_id = Column(UUID(as_uuid=True), ForeignKey("service_boundaries.id"), nullable=False)
    metric_name = Column(String(255), nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_description = Column(Text)
    
    # Relationships
    service_boundary = relationship("ServiceBoundary", back_populates="boundary_metrics")