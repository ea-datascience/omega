"""Static analysis orchestration service using Microsoft Agent Framework."""
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
import asyncio
import json
from datetime import datetime
import tempfile

from ...analysis.static import (
    JavaSourceAnalyzer, ContextMapperAnalyzer, DependencyExtractor, 
    StructurizrGenerator, CodeQLAnalyzer, AppCATAnalyzer
)

logger = logging.getLogger(__name__)


@dataclass
class AnalysisTask:
    """Represents an analysis task to be executed."""
    task_id: str
    analyzer_type: str
    source_path: Path
    output_path: Path
    config: Dict[str, Any]
    status: str = "pending"  # pending, running, completed, failed
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    error_message: Optional[str] = None
    result_path: Optional[Path] = None


@dataclass
class AnalysisResults:
    """Comprehensive analysis results from all analyzers."""
    analysis_id: str
    source_path: Path
    output_directory: Path
    
    # Individual analyzer results
    java_analysis: Optional[Dict[str, Any]] = None
    context_mapping: Optional[Dict[str, Any]] = None
    dependency_analysis: Optional[Dict[str, Any]] = None
    architecture_model: Optional[Dict[str, Any]] = None
    security_analysis: Optional[Dict[str, Any]] = None
    migration_assessment: Optional[Dict[str, Any]] = None
    
    # Orchestration metadata
    execution_metadata: Dict[str, Any] = None
    summary_metrics: Dict[str, Any] = None


class StaticAnalysisOrchestrator:
    """Orchestrates static analysis using Microsoft Agent Framework patterns."""
    
    def __init__(self, base_output_dir: Optional[Path] = None):
        self.base_output_dir = base_output_dir or Path(tempfile.gettempdir()) / "omega_analysis"
        self.base_output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize analyzers
        self.java_analyzer = JavaSourceAnalyzer()
        self.context_mapper = ContextMapperAnalyzer()
        self.dependency_extractor = DependencyExtractor()
        self.structurizr_generator = StructurizrGenerator()
        self.codeql_analyzer = CodeQLAnalyzer()
        self.appcat_analyzer = AppCATAnalyzer()
        
        # Task tracking
        self.active_tasks: Dict[str, AnalysisTask] = {}
        self.completed_analyses: Dict[str, AnalysisResults] = {}
    
    async def orchestrate_full_analysis(self, 
                                      source_path: Path, 
                                      analysis_id: Optional[str] = None,
                                      config: Optional[Dict[str, Any]] = None) -> AnalysisResults:
        """Orchestrate a complete static analysis workflow."""
        logger.info(f"Starting full static analysis orchestration for: {source_path}")
        
        if analysis_id is None:
            analysis_id = f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        if config is None:
            config = self._get_default_config()
        
        # Create output directory
        output_dir = self.base_output_dir / analysis_id
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize results container
        results = AnalysisResults(
            analysis_id=analysis_id,
            source_path=source_path,
            output_directory=output_dir,
            execution_metadata={
                "start_time": datetime.now().isoformat(),
                "config": config,
                "orchestrator_version": "1.0.0"
            }
        )
        
        try:
            # Phase 1: Core Analysis (can run in parallel)
            logger.info("Phase 1: Running core analysis tasks")
            core_tasks = await self._execute_core_analysis_phase(
                source_path, output_dir, config
            )
            
            # Phase 2: Dependent Analysis (requires core analysis results)
            logger.info("Phase 2: Running dependent analysis tasks")
            dependent_tasks = await self._execute_dependent_analysis_phase(
                core_tasks, output_dir, config
            )
            
            # Phase 3: Integration and Reporting
            logger.info("Phase 3: Integrating results and generating reports")
            await self._integrate_and_report(
                results, core_tasks, dependent_tasks, output_dir
            )
            
            # Update execution metadata
            results.execution_metadata.update({
                "end_time": datetime.now().isoformat(),
                "status": "completed",
                "total_tasks": len(core_tasks) + len(dependent_tasks)
            })
            
            # Generate summary metrics
            results.summary_metrics = self._calculate_summary_metrics(results)
            
            # Store completed analysis
            self.completed_analyses[analysis_id] = results
            
            logger.info(f"Static analysis orchestration completed: {analysis_id}")
            return results
            
        except Exception as e:
            logger.error(f"Static analysis orchestration failed: {e}")
            results.execution_metadata.update({
                "end_time": datetime.now().isoformat(),
                "status": "failed",
                "error": str(e)
            })
            raise
    
    async def _execute_core_analysis_phase(self, 
                                         source_path: Path, 
                                         output_dir: Path,
                                         config: Dict[str, Any]) -> Dict[str, AnalysisTask]:
        """Execute core analysis tasks that can run independently."""
        
        core_tasks = {
            "java_analysis": AnalysisTask(
                task_id="java_analysis",
                analyzer_type="JavaSourceAnalyzer", 
                source_path=source_path,
                output_path=output_dir / "java_analysis.json",
                config=config.get("java_analysis", {})
            ),
            "dependency_analysis": AnalysisTask(
                task_id="dependency_analysis",
                analyzer_type="DependencyExtractor",
                source_path=source_path,
                output_path=output_dir / "dependencies.json", 
                config=config.get("dependency_analysis", {})
            ),
            "security_analysis": AnalysisTask(
                task_id="security_analysis",
                analyzer_type="CodeQLAnalyzer",
                source_path=source_path,
                output_path=output_dir / "security_analysis.json",
                config=config.get("security_analysis", {})
            ),
            "migration_assessment": AnalysisTask(
                task_id="migration_assessment",
                analyzer_type="AppCATAnalyzer",
                source_path=source_path,
                output_path=output_dir / "migration_assessment.json",
                config=config.get("migration_assessment", {})
            )
        }
        
        # Execute core tasks in parallel using Agent Framework patterns
        tasks_coroutines = []
        for task_id, task in core_tasks.items():
            tasks_coroutines.append(self._execute_analysis_task(task))
        
        # Wait for all core tasks to complete
        await asyncio.gather(*tasks_coroutines, return_exceptions=True)
        
        return core_tasks
    
    async def _execute_dependent_analysis_phase(self,
                                              core_tasks: Dict[str, AnalysisTask],
                                              output_dir: Path,
                                              config: Dict[str, Any]) -> Dict[str, AnalysisTask]:
        """Execute analysis tasks that depend on core analysis results."""
        
        # Ensure java_analysis completed successfully
        java_task = core_tasks.get("java_analysis")
        if not java_task or java_task.status != "completed":
            logger.warning("Java analysis not completed, skipping dependent tasks")
            return {}
        
        dependent_tasks = {
            "context_mapping": AnalysisTask(
                task_id="context_mapping",
                analyzer_type="ContextMapperAnalyzer",
                source_path=java_task.source_path,
                output_path=output_dir / "context_mapping.json",
                config=config.get("context_mapping", {})
            ),
            "architecture_model": AnalysisTask(
                task_id="architecture_model", 
                analyzer_type="StructurizrGenerator",
                source_path=java_task.source_path,
                output_path=output_dir / "architecture_model.json",
                config=config.get("architecture_model", {})
            )
        }
        
        # Execute dependent tasks in sequence (context mapping first, then architecture)
        for task_id, task in dependent_tasks.items():
            await self._execute_analysis_task(task)
            
            # If context mapping fails, skip architecture model
            if task_id == "context_mapping" and task.status != "completed":
                logger.warning("Context mapping failed, skipping architecture model")
                dependent_tasks.pop("architecture_model", None)
                break
        
        return dependent_tasks
    
    async def _execute_analysis_task(self, task: AnalysisTask) -> None:
        """Execute a single analysis task using appropriate analyzer."""
        logger.info(f"Starting task: {task.task_id}")
        
        task.status = "running"
        task.start_time = datetime.now()
        self.active_tasks[task.task_id] = task
        
        try:
            if task.analyzer_type == "JavaSourceAnalyzer":
                result = self.java_analyzer.analyze_directory(task.source_path)
                self._save_task_result(task, result, "java_source_analysis")
                
            elif task.analyzer_type == "DependencyExtractor":
                result = self.dependency_extractor.analyze_dependencies(task.source_path)
                self._save_task_result(task, result, "dependency_analysis")
                
            elif task.analyzer_type == "ContextMapperAnalyzer":
                result = self.context_mapper.analyze_project(task.source_path)
                self._save_task_result(task, result, "context_mapping")
                
            elif task.analyzer_type == "StructurizrGenerator":
                result = self.structurizr_generator.generate_c4_model(task.source_path)
                self._save_task_result(task, result, "architecture_model")
                
            elif task.analyzer_type == "CodeQLAnalyzer":
                result = self.codeql_analyzer.analyze_project(task.source_path)
                self._save_task_result(task, result, "security_analysis")
                
            elif task.analyzer_type == "AppCATAnalyzer":
                result = self.appcat_analyzer.analyze_application(task.source_path)
                self._save_task_result(task, result, "migration_assessment")
                
            else:
                raise ValueError(f"Unknown analyzer type: {task.analyzer_type}")
            
            task.status = "completed"
            task.end_time = datetime.now()
            task.result_path = task.output_path
            
            logger.info(f"Task completed: {task.task_id}")
            
        except Exception as e:
            task.status = "failed"
            task.end_time = datetime.now()
            task.error_message = str(e)
            logger.error(f"Task failed {task.task_id}: {e}")
        
        finally:
            # Remove from active tasks
            self.active_tasks.pop(task.task_id, None)
    
    def _save_task_result(self, task: AnalysisTask, result: Any, result_type: str) -> None:
        """Save task result to file."""
        try:
            # Convert result to dictionary if it's a dataclass
            if hasattr(result, '__dataclass_fields__'):
                result_dict = asdict(result)
            elif hasattr(result, '__dict__'):
                result_dict = result.__dict__
            else:
                result_dict = result
            
            # Add metadata
            output_data = {
                "result_type": result_type,
                "task_id": task.task_id,
                "analyzer_type": task.analyzer_type,
                "generated_at": datetime.now().isoformat(),
                "source_path": str(task.source_path),
                "result": result_dict
            }
            
            with open(task.output_path, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False, default=str)
                
        except Exception as e:
            logger.error(f"Failed to save task result for {task.task_id}: {e}")
            raise
    
    def _load_java_analysis_results(self, base_dir: Path) -> Optional[Dict[str, Any]]:
        """Load Java analysis results for dependent tasks."""
        try:
            java_results_path = base_dir / "java_analysis.json"
            if java_results_path.exists():
                with open(java_results_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load Java analysis results: {e}")
        return None
    
    def _load_context_mapping_results(self, base_dir: Path) -> Optional[Dict[str, Any]]:
        """Load context mapping results for dependent tasks."""
        try:
            context_results_path = base_dir / "context_mapping.json"
            if context_results_path.exists():
                with open(context_results_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load context mapping results: {e}")
        return None
    
    async def _integrate_and_report(self, 
                                  results: AnalysisResults,
                                  core_tasks: Dict[str, AnalysisTask],
                                  dependent_tasks: Dict[str, AnalysisTask],
                                  output_dir: Path) -> None:
        """Integrate all analysis results and generate comprehensive reports."""
        
        # Load and integrate results from completed tasks
        all_tasks = {**core_tasks, **dependent_tasks}
        
        for task_id, task in all_tasks.items():
            if task.status == "completed" and task.result_path and task.result_path.exists():
                try:
                    with open(task.result_path, 'r', encoding='utf-8') as f:
                        task_data = json.load(f)
                    
                    # Store in results object
                    if task_id == "java_analysis":
                        results.java_analysis = task_data
                    elif task_id == "context_mapping":
                        results.context_mapping = task_data
                    elif task_id == "dependency_analysis":
                        results.dependency_analysis = task_data
                    elif task_id == "architecture_model":
                        results.architecture_model = task_data
                    elif task_id == "security_analysis":
                        results.security_analysis = task_data
                    elif task_id == "migration_assessment":
                        results.migration_assessment = task_data
                        
                except Exception as e:
                    logger.error(f"Failed to load results for {task_id}: {e}")
        
        # Generate integrated reports
        await self._generate_comprehensive_report(results, output_dir)
        await self._generate_executive_summary(results, output_dir)
        
        # Export consolidated results
        consolidated_path = output_dir / "consolidated_results.json"
        with open(consolidated_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(results), f, indent=2, ensure_ascii=False, default=str)
    
    async def _generate_comprehensive_report(self, results: AnalysisResults, output_dir: Path) -> None:
        """Generate a comprehensive analysis report."""
        report_path = output_dir / "comprehensive_report.md"
        
        report_lines = [
            "# Comprehensive Static Analysis Report",
            f"**Analysis ID**: {results.analysis_id}",
            f"**Source Path**: {results.source_path}",
            f"**Generated**: {datetime.now().isoformat()}",
            "",
            "## Executive Summary"
        ]
        
        # Add summary metrics if available
        if results.summary_metrics:
            report_lines.extend([
                f"- **Total Classes Analyzed**: {results.summary_metrics.get('total_classes', 'N/A')}",
                f"- **Dependencies Found**: {results.summary_metrics.get('total_dependencies', 'N/A')}",
                f"- **Security Issues**: {results.summary_metrics.get('security_issues', 'N/A')}",
                f"- **Cloud Readiness Score**: {results.summary_metrics.get('cloud_readiness_score', 'N/A')}",
                ""
            ])
        
        # Java Analysis Section
        if results.java_analysis:
            report_lines.extend([
                "## Java Source Analysis",
                f"- Analysis completed successfully",
                f"- Detailed results: `java_analysis.json`",
                ""
            ])
        
        # Context Mapping Section
        if results.context_mapping:
            report_lines.extend([
                "## Context Mapping",
                f"- Bounded contexts identified",
                f"- Detailed results: `context_mapping.json`",
                ""
            ])
        
        # Dependency Analysis Section
        if results.dependency_analysis:
            report_lines.extend([
                "## Dependency Analysis", 
                f"- Dependency graph generated",
                f"- Detailed results: `dependencies.json`",
                ""
            ])
        
        # Architecture Model Section
        if results.architecture_model:
            report_lines.extend([
                "## Architecture Model",
                f"- C4 model generated",
                f"- Detailed results: `architecture_model.json`",
                ""
            ])
        
        # Security Analysis Section
        if results.security_analysis:
            report_lines.extend([
                "## Security Analysis",
                f"- CodeQL analysis completed",
                f"- Detailed results: `security_analysis.json`",
                ""
            ])
        
        # Migration Assessment Section
        if results.migration_assessment:
            report_lines.extend([
                "## Migration Assessment",
                f"- AppCAT assessment completed",
                f"- Detailed results: `migration_assessment.json`",
                ""
            ])
        
        report_lines.extend([
            "## Next Steps",
            "1. Review individual analysis results",
            "2. Address security findings",
            "3. Plan migration strategy based on assessment",
            "4. Implement recommended architectural improvements"
        ])
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))
        
        logger.info(f"Comprehensive report generated: {report_path}")
    
    async def _generate_executive_summary(self, results: AnalysisResults, output_dir: Path) -> None:
        """Generate an executive summary report."""
        summary_path = output_dir / "executive_summary.md"
        
        summary_lines = [
            "# Executive Summary - Static Analysis",
            f"**Analysis ID**: {results.analysis_id}",
            f"**Date**: {datetime.now().strftime('%Y-%m-%d')}",
            "",
            "## Key Findings"
        ]
        
        # Extract key metrics from results
        if results.summary_metrics:
            metrics = results.summary_metrics
            
            summary_lines.extend([
                f"- **Code Complexity**: {metrics.get('complexity_assessment', 'Medium')}",
                f"- **Security Posture**: {metrics.get('security_score', 'Unknown')}/100",
                f"- **Cloud Readiness**: {metrics.get('cloud_readiness_score', 'Unknown')}/100",
                f"- **Migration Effort**: {metrics.get('estimated_migration_weeks', 'TBD')} weeks",
                ""
            ])
        
        summary_lines.extend([
            "## Recommendations",
            "1. **Immediate Actions**",
            "   - Address high-severity security findings",
            "   - Review dependency vulnerabilities",
            "",
            "2. **Short-term (1-3 months)**", 
            "   - Implement architectural improvements",
            "   - Prepare for cloud migration",
            "",
            "3. **Long-term (3-12 months)**",
            "   - Execute microservices decomposition",
            "   - Complete cloud migration",
            "",
            "## Risk Assessment",
            "- **Technical Risk**: Medium",
            "- **Timeline Risk**: Low",
            "- **Resource Risk**: Medium"
        ])
        
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(summary_lines))
        
        logger.info(f"Executive summary generated: {summary_path}")
    
    def _calculate_summary_metrics(self, results: AnalysisResults) -> Dict[str, Any]:
        """Calculate summary metrics from all analysis results."""
        metrics = {}
        
        # Java analysis metrics
        if results.java_analysis:
            java_result = results.java_analysis.get("result", {})
            metrics["total_classes"] = java_result.get("total_classes", 0)
            metrics["total_methods"] = java_result.get("total_methods", 0)
        
        # Dependency metrics
        if results.dependency_analysis:
            dep_result = results.dependency_analysis.get("result", {})
            metrics["total_dependencies"] = len(dep_result.get("internal_dependencies", []))
        
        # Security metrics
        if results.security_analysis:
            sec_result = results.security_analysis.get("result", {})
            sec_metrics = sec_result.get("metrics", {})
            security_findings = sec_metrics.get("security_findings", {})
            metrics["security_issues"] = security_findings.get("total", 0)
            metrics["security_score"] = security_findings.get("security_score", 0)
        
        # Migration assessment metrics
        if results.migration_assessment:
            mig_result = results.migration_assessment.get("result", {})
            cloud_readiness = mig_result.get("cloud_readiness", {})
            metrics["cloud_readiness_score"] = cloud_readiness.get("overall_readiness_score", 0)
            metrics["estimated_migration_weeks"] = cloud_readiness.get("estimated_effort_weeks", 0)
        
        # Overall complexity assessment
        complexity_factors = []
        if results.java_analysis:
            complexity_factors.append("Java")
        if results.dependency_analysis:
            complexity_factors.append("Dependencies")
        
        if len(complexity_factors) >= 3:
            metrics["complexity_assessment"] = "High"
        elif len(complexity_factors) >= 2:
            metrics["complexity_assessment"] = "Medium"
        else:
            metrics["complexity_assessment"] = "Low"
        
        return metrics
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration for analysis."""
        return {
            "java_analysis": {
                "include_test_classes": True,
                "analyze_dependencies": True,
                "calculate_metrics": True
            },
            "dependency_analysis": {
                "include_transitive": True,
                "detect_circular": True,
                "calculate_coupling": True
            },
            "context_mapping": {
                "ddd_analysis": True,
                "generate_context_map": True
            },
            "architecture_model": {
                "generate_c4_model": True,
                "export_plantuml": True,
                "create_workspace": True
            },
            "security_analysis": {
                "run_security_queries": True,
                "run_quality_queries": True,
                "generate_report": True
            },
            "migration_assessment": {
                "assess_cloud_readiness": True,
                "technology_assessment": True,
                "generate_recommendations": True
            }
        }
    
    def get_analysis_status(self, analysis_id: str) -> Optional[Dict[str, Any]]:
        """Get status of an analysis."""
        if analysis_id in self.completed_analyses:
            results = self.completed_analyses[analysis_id]
            return {
                "analysis_id": analysis_id,
                "status": "completed",
                "source_path": str(results.source_path),
                "output_directory": str(results.output_directory),
                "execution_metadata": results.execution_metadata,
                "summary_metrics": results.summary_metrics
            }
        
        # Check active tasks
        active_task_ids = list(self.active_tasks.keys())
        if any(analysis_id in task_id for task_id in active_task_ids):
            return {
                "analysis_id": analysis_id,
                "status": "running",
                "active_tasks": active_task_ids
            }
        
        return None
    
    def list_completed_analyses(self) -> List[Dict[str, Any]]:
        """List all completed analyses."""
        return [
            {
                "analysis_id": analysis_id,
                "source_path": str(results.source_path),
                "completed_at": results.execution_metadata.get("end_time"),
                "summary_metrics": results.summary_metrics
            }
            for analysis_id, results in self.completed_analyses.items()
        ]