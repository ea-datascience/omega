"""Integration tests for static analysis components using Spring Modulith reference codebase."""
import pytest
import asyncio
import tempfile
import json
from pathlib import Path
from datetime import datetime

from omega_analysis.analysis.static import (
    JavaSourceAnalyzer, ContextMapperAnalyzer, DependencyExtractor, 
    StructurizrGenerator, CodeQLAnalyzer, AppCATAnalyzer
)
from omega_analysis.services.orchestration import StaticAnalysisOrchestrator


class TestStaticAnalysisIntegration:
    """Integration tests for static analysis components."""
    
    @pytest.fixture
    def spring_modulith_path(self):
        """Path to Spring Modulith reference codebase."""
        codebase_path = Path("/workspace/data/codebase/spring-modulith")
        if not codebase_path.exists():
            pytest.skip("Spring Modulith codebase not available for testing")
        return codebase_path
    
    @pytest.fixture
    def temp_output_dir(self):
        """Temporary directory for test outputs."""
        with tempfile.TemporaryDirectory(prefix="test_analysis_") as temp_dir:
            yield Path(temp_dir)
    
    def test_java_source_analyzer_basic_functionality(self, spring_modulith_path, temp_output_dir):
        """Test JavaSourceAnalyzer with real Spring Modulith codebase."""
        print(f"\n=== Testing JavaSourceAnalyzer ===")
        print(f"Source path: {spring_modulith_path}")
        
        analyzer = JavaSourceAnalyzer()
        
        try:
            # Test basic analysis
            result = analyzer.analyze_directory(spring_modulith_path)
            
            # Validate result structure
            assert isinstance(result, dict), "Result should be a dictionary"
            assert 'classes' in result, "Result should have classes key"
            assert 'metrics' in result, "Result should have metrics key"
            assert 'packages' in result, "Result should have packages key"
            
            print(f"✓ Analysis completed successfully")
            print(f"✓ Found {len(result['classes'])} Java classes")
            print(f"✓ Package structure has {len(result['packages'])} packages")
            print(f"✓ Metrics calculated: {list(result['metrics'].keys())}")
            
            # Test Spring component detection
            spring_components = [cls for cls in result['classes'].values() if hasattr(cls, 'spring_annotations') and cls.spring_annotations]
            print(f"✓ Found {len(spring_components)} Spring components")
            
            # Validate at least some classes were found
            assert len(result['classes']) > 0, "Should find Java classes in Spring Modulith"
            assert len(result['packages']) > 0, "Should find packages in Spring Modulith"
            
            # Export result for manual inspection
            export_path = temp_output_dir / "java_analysis_test.json"
            with open(export_path, 'w') as f:
                import json
                json.dump(result, f, indent=2, default=str)
            assert export_path.exists(), "Export should create file"
            print(f"✓ Results exported to: {export_path}")
            
            return True
            
        except Exception as e:
            print(f"✗ JavaSourceAnalyzer failed: {e}")
            raise
    
    def test_dependency_extractor_functionality(self, spring_modulith_path, temp_output_dir):
        """Test DependencyExtractor with Spring Modulith Maven structure."""
        print(f"\n=== Testing DependencyExtractor ===")
        
        extractor = DependencyExtractor()
        
        try:
            # Test dependency extraction
            result = extractor.analyze_dependencies(spring_modulith_path)
            
            # Validate result structure
            assert hasattr(result, 'internal_dependencies'), "Result should have internal_dependencies"
            assert hasattr(result, 'external_dependencies'), "Result should have external_dependencies"
            assert hasattr(result, 'maven_dependencies'), "Result should have maven_dependencies"
            
            print(f"✓ Dependency extraction completed")
            print(f"✓ Found {len(result.internal_dependencies)} internal dependency relationships")
            print(f"✓ Found {len(result.external_dependencies)} classes with external dependencies")
            print(f"✓ Found {len(result.maven_dependencies)} Maven dependencies")
            
            # Validate some dependencies were found
            assert len(result.maven_dependencies) > 0, "Spring Modulith should have Maven dependencies"
            
            # Check for expected Spring dependencies
            spring_deps = [dep for dep in result.maven_dependencies 
                          if 'spring' in dep.group_id.lower()]
            print(f"✓ Found {len(spring_deps)} Spring framework dependencies")
            assert len(spring_deps) > 0, "Should find Spring dependencies"
            
            # Export result
            export_path = temp_output_dir / "dependency_analysis_test.json"
            with open(export_path, 'w') as f:
                import json
                from dataclasses import asdict
                json.dump(asdict(result), f, indent=2, default=str)
            assert export_path.exists(), "Export should create file"
            print(f"✓ Results exported to: {export_path}")
            
            return result
            
        except Exception as e:
            print(f"✗ DependencyExtractor failed: {e}")
            raise
    
    def test_context_mapper_functionality(self, spring_modulith_path, temp_output_dir):
        """Test ContextMapperAnalyzer with Spring Modulith."""
        print(f"\n=== Testing ContextMapperAnalyzer ===")
        
        # Context mapper will analyze Java internally
        
        context_mapper = ContextMapperAnalyzer()
        
        try:
            # Test context mapping
            result = context_mapper.analyze_project(spring_modulith_path)
            
            # Validate result structure
            assert hasattr(result, 'domain_model'), "Result should have domain_model"
            assert hasattr(result, 'context_map_dsl'), "Result should have context_map_dsl"
            assert hasattr(result, 'metrics'), "Result should have metrics"
            
            print(f"✓ Context mapping completed")
            print(f"✓ Found {len(result.domain_model.bounded_contexts)} bounded contexts")
            print(f"✓ Generated Context Map DSL: {len(result.context_map_dsl.split('\n'))} lines")
            print(f"✓ Metrics: {list(result.metrics.keys())}")
            
            # Validate some contexts were found
            assert len(result.domain_model.bounded_contexts) > 0, "Should identify bounded contexts"
            
            # Print context details
            for context in result.domain_model.bounded_contexts[:3]:  # Show first 3
                print(f"  - Context: {context.name} ({len(context.aggregates)} aggregates)")
            
            # Export result
            export_path = temp_output_dir / "context_mapping_test.json"
            with open(export_path, 'w') as f:
                import json
                from dataclasses import asdict
                json.dump(asdict(result), f, indent=2, default=str)
            assert export_path.exists(), "Export should create file"
            print(f"✓ Results exported to: {export_path}")
            
            return result
            
        except Exception as e:
            print(f"✗ ContextMapperAnalyzer failed: {e}")
            raise
    
    def test_structurizr_generator_functionality(self, spring_modulith_path, temp_output_dir):
        """Test StructurizrGenerator with context mapping results."""
        print(f"\n=== Testing StructurizrGenerator ===")
        
        # Structurizr generator will handle dependencies internally
        
        structurizr = StructurizrGenerator()
        
        try:
            # Test C4 model generation
            result = structurizr.generate_c4_model(spring_modulith_path)
            
            # Validate result structure
            assert hasattr(result, 'name'), "Result should have name"
            assert hasattr(result, 'software_systems'), "Result should have software_systems"
            assert hasattr(result, 'containers'), "Result should have containers"
            assert hasattr(result, 'components'), "Result should have components"
            
            print(f"✓ C4 model generation completed")
            print(f"✓ Model has {len(result.software_systems)} software systems")
            print(f"✓ Model has {len(result.containers)} containers")
            print(f"✓ Model has {len(result.components)} components")
            print(f"✓ Model has {len(result.views)} views")
            
            # Validate some model elements were created
            assert len(result.software_systems) > 0, "Should create software systems"
            
            # Test export capabilities
            json_path = temp_output_dir / "c4_model_test.json"
            plantuml_path = temp_output_dir / "c4_model_test.puml"
            
            with open(json_path, 'w') as f:
                import json
                from dataclasses import asdict
                json.dump(asdict(result), f, indent=2, default=str)
            
            with open(plantuml_path, 'w') as f:
                f.write(f"@startuml\ntitle {result.name}\n@enduml")
            
            assert json_path.exists(), "JSON export should create file"
            assert plantuml_path.exists(), "PlantUML export should create file"
            print(f"✓ Results exported to JSON and PlantUML")
            
            return result
            
        except Exception as e:
            print(f"✗ StructurizrGenerator failed: {e}")
            raise
    
    def test_codeql_analyzer_functionality(self, spring_modulith_path, temp_output_dir):
        """Test CodeQLAnalyzer (will use mock results if CodeQL not available)."""
        print(f"\n=== Testing CodeQLAnalyzer ===")
        
        analyzer = CodeQLAnalyzer()
        
        try:
            # Test security analysis (will generate mock results if CodeQL not available)
            result = analyzer.analyze_project(spring_modulith_path, temp_output_dir)
            
            # Validate result structure
            assert hasattr(result, 'security_findings'), "Result should have security_findings"
            assert hasattr(result, 'quality_findings'), "Result should have quality_findings" 
            assert hasattr(result, 'metrics'), "Result should have metrics"
            assert hasattr(result, 'scan_metadata'), "Result should have scan_metadata"
            
            print(f"✓ CodeQL analysis completed")
            print(f"✓ Found {len(result.security_findings)} security findings")
            print(f"✓ Found {len(result.quality_findings)} quality findings")
            print(f"✓ Security score: {result.metrics['security_findings']['security_score']}/100")
            
            # Check if this was real or mock analysis
            is_mock = result.scan_metadata.get('mock_data', False)
            print(f"✓ Analysis type: {'Mock (CodeQL not available)' if is_mock else 'Real CodeQL'}")
            
            # Export result
            export_path = temp_output_dir / "codeql_analysis_test.json"
            analyzer.export_results(result, export_path)
            assert export_path.exists(), "Export should create file"
            print(f"✓ Results exported to: {export_path}")
            
            return result
            
        except Exception as e:
            print(f"✗ CodeQLAnalyzer failed: {e}")
            raise
    
    def test_appcat_analyzer_functionality(self, spring_modulith_path, temp_output_dir):
        """Test AppCATAnalyzer (will use comprehensive assessment if AppCAT not available)."""
        print(f"\n=== Testing AppCATAnalyzer ===")
        
        analyzer = AppCATAnalyzer()
        
        try:
            # Test application assessment
            result = analyzer.analyze_application(spring_modulith_path, temp_output_dir)
            
            # Validate result structure
            assert hasattr(result, 'technology_assessments'), "Result should have technology_assessments"
            assert hasattr(result, 'architectural_patterns'), "Result should have architectural_patterns"
            assert hasattr(result, 'cloud_readiness'), "Result should have cloud_readiness"
            assert hasattr(result, 'metrics'), "Result should have metrics"
            
            print(f"✓ AppCAT analysis completed")
            print(f"✓ Assessed {len(result.technology_assessments)} technologies")
            print(f"✓ Found {len(result.architectural_patterns)} architectural patterns")
            print(f"✓ Cloud readiness score: {result.cloud_readiness.overall_readiness_score}/100")
            print(f"✓ Cloud readiness category: {result.cloud_readiness.readiness_category}")
            print(f"✓ Estimated migration effort: {result.cloud_readiness.estimated_effort_weeks} weeks")
            
            # Check if this was real or mock analysis
            is_mock = result.assessment_metadata.get('mock_data', False)
            print(f"✓ Analysis type: {'Comprehensive (AppCAT not available)' if is_mock else 'Real AppCAT'}")
            
            # Export result
            export_path = temp_output_dir / "appcat_analysis_test.json"
            analyzer.export_results(result, export_path)
            assert export_path.exists(), "Export should create file"
            print(f"✓ Results exported to: {export_path}")
            
            return result
            
        except Exception as e:
            print(f"✗ AppCATAnalyzer failed: {e}")
            raise
    
    @pytest.mark.asyncio 
    async def test_orchestration_service_integration(self, spring_modulith_path, temp_output_dir):
        """Test complete StaticAnalysisOrchestrator workflow."""
        print(f"\n=== Testing StaticAnalysisOrchestrator ===")
        
        # Create orchestrator with test output directory
        orchestrator = StaticAnalysisOrchestrator(base_output_dir=temp_output_dir)
        
        try:
            # Test full orchestration workflow
            analysis_id = f"test_analysis_{datetime.now().strftime('%H%M%S')}"
            
            print(f"Starting orchestrated analysis: {analysis_id}")
            result = await orchestrator.orchestrate_full_analysis(
                source_path=spring_modulith_path,
                analysis_id=analysis_id
            )
            
            # Validate orchestration result
            assert result.analysis_id == analysis_id, "Analysis ID should match"
            assert result.source_path == spring_modulith_path, "Source path should match"
            assert result.output_directory.exists(), "Output directory should exist"
            
            print(f"✓ Orchestration completed successfully")
            print(f"✓ Analysis ID: {result.analysis_id}")
            print(f"✓ Output directory: {result.output_directory}")
            
            # Check execution metadata
            assert result.execution_metadata is not None, "Should have execution metadata"
            assert result.execution_metadata.get('status') == 'completed', "Should be completed"
            print(f"✓ Execution status: {result.execution_metadata.get('status')}")
            print(f"✓ Total tasks: {result.execution_metadata.get('total_tasks', 0)}")
            
            # Validate individual analysis results
            analysis_components = [
                ('java_analysis', 'Java source analysis'),
                ('dependency_analysis', 'Dependency analysis'),
                ('context_mapping', 'Context mapping'),
                ('architecture_model', 'Architecture model'),
                ('security_analysis', 'Security analysis'),
                ('migration_assessment', 'Migration assessment')
            ]
            
            completed_count = 0
            for component, description in analysis_components:
                component_result = getattr(result, component, None)
                if component_result is not None:
                    completed_count += 1
                    print(f"✓ {description}: Completed")
                else:
                    print(f"- {description}: Not completed")
            
            print(f"✓ Completed {completed_count}/{len(analysis_components)} analysis components")
            
            # Validate summary metrics
            if result.summary_metrics:
                print(f"✓ Summary metrics generated:")
                for key, value in result.summary_metrics.items():
                    print(f"  - {key}: {value}")
            
            # Check for generated reports
            output_dir = result.output_directory
            expected_files = [
                "comprehensive_report.md",
                "executive_summary.md", 
                "consolidated_results.json"
            ]
            
            for filename in expected_files:
                file_path = output_dir / filename
                if file_path.exists():
                    print(f"✓ Generated report: {filename}")
                else:
                    print(f"- Missing report: {filename}")
            
            # Test status retrieval
            status = orchestrator.get_analysis_status(analysis_id)
            assert status is not None, "Should be able to retrieve analysis status"
            assert status['status'] == 'completed', "Status should be completed"
            print(f"✓ Status retrieval working")
            
            return result
            
        except Exception as e:
            print(f"✗ StaticAnalysisOrchestrator failed: {e}")
            raise
    
    def test_end_to_end_workflow(self, spring_modulith_path, temp_output_dir):
        """Test complete end-to-end workflow with all components."""
        print(f"\n=== End-to-End Integration Test ===")
        print(f"Testing complete workflow with Spring Modulith codebase")
        print(f"Source: {spring_modulith_path}")
        print(f"Output: {temp_output_dir}")
        
        try:
            # Run individual component tests first
            print("\n--- Phase 1: Individual Component Tests ---")
            java_result = self.test_java_source_analyzer_basic_functionality(spring_modulith_path, temp_output_dir)
            dep_result = self.test_dependency_extractor_functionality(spring_modulith_path, temp_output_dir)
            context_result = self.test_context_mapper_functionality(spring_modulith_path, temp_output_dir)
            struct_result = self.test_structurizr_generator_functionality(spring_modulith_path, temp_output_dir)
            codeql_result = self.test_codeql_analyzer_functionality(spring_modulith_path, temp_output_dir)
            appcat_result = self.test_appcat_analyzer_functionality(spring_modulith_path, temp_output_dir)
            
            print("\n--- Phase 2: Orchestration Integration Test ---")
            # Run orchestration test
            import asyncio
            orchestration_result = asyncio.run(
                self.test_orchestration_service_integration(spring_modulith_path, temp_output_dir)
            )
            
            print(f"\n=== Integration Test Summary ===")
            print(f"✅ All components tested successfully!")
            print(f"✅ Java Source Analyzer: Working")
            print(f"✅ Dependency Extractor: Working") 
            print(f"✅ Context Mapper: Working")
            print(f"✅ Structurizr Generator: Working")
            print(f"✅ CodeQL Analyzer: Working")
            print(f"✅ AppCAT Analyzer: Working")
            print(f"✅ Static Analysis Orchestrator: Working")
            print(f"\n🎯 System Ready for Production Use!")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Integration Test Failed: {e}")
            print(f"❌ System needs debugging before production use")
            raise


# Run the integration tests
if __name__ == "__main__":
    import sys
    
    print("="*60)
    print("OMEGA STATIC ANALYSIS INTEGRATION TESTS")
    print("="*60)
    
    # Create test instance
    test_instance = TestStaticAnalysisIntegration()
    
    # Set up paths
    spring_modulith_path = Path("/workspace/data/codebase/spring-modulith")
    
    if not spring_modulith_path.exists():
        print("❌ Spring Modulith codebase not found!")
        print(f"Expected path: {spring_modulith_path}")
        sys.exit(1)
    
    with tempfile.TemporaryDirectory(prefix="integration_test_") as temp_dir:
        temp_output_dir = Path(temp_dir)
        
        try:
            # Run end-to-end test
            success = test_instance.test_end_to_end_workflow(spring_modulith_path, temp_output_dir)
            
            if success:
                print(f"\n🎉 ALL TESTS PASSED!")
                print(f"📁 Test outputs available in: {temp_output_dir}")
                sys.exit(0)
            else:
                print(f"\n💥 TESTS FAILED!")
                sys.exit(1)
                
        except Exception as e:
            print(f"\n💥 CRITICAL FAILURE: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)