"""
Integration tests for Spring Boot Analyzer.

Tests analyzer on real Spring Modulith example codebase.
"""

import pytest
import json
from pathlib import Path
from src.utils.spring_boot_analyzer import (
    SpringBootAnalyzer,
    SpringBootAnalyzerError
)
from src.utils.context_mapper import ContextMapper


class TestSpringBootAnalyzerIntegration:
    """Integration tests with real Spring Modulith codebase"""
    
    @pytest.fixture
    def spring_modulith_example(self):
        """Path to Spring Modulith full example"""
        path = Path("/workspace/data/codebase/spring-modulith/spring-modulith-examples/spring-modulith-example-full")
        if not path.exists():
            pytest.skip("Spring Modulith example not found")
        return path
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance"""
        return SpringBootAnalyzer()
    
    @pytest.fixture
    def output_dir(self, tmp_path):
        """Create temporary output directory"""
        return tmp_path / "output"
    
    def test_analyze_spring_modulith_example(
        self,
        analyzer,
        spring_modulith_example
    ):
        """Test analyzing real Spring Modulith example"""
        result = analyzer.analyze_project(
            project_path=spring_modulith_example,
            base_package="example"
        )
        
        # Verify application found
        assert result.application_class == "Application"
        assert result.base_package == "example"
        
        # Verify modules found
        assert len(result.modules) == 2
        module_names = [m.name for m in result.modules]
        assert "order" in module_names
        assert "inventory" in module_names
    
    def test_order_module_structure(
        self,
        analyzer,
        spring_modulith_example
    ):
        """Test order module analysis"""
        result = analyzer.analyze_project(
            project_path=spring_modulith_example,
            base_package="example"
        )
        
        order_module = next(m for m in result.modules if m.name == "order")
        
        # Order module has services
        assert len(order_module.services) > 0
        assert "OrderManagement" in order_module.services
        
        # Has all classes
        assert len(order_module.all_classes) > 0
    
    def test_inventory_module_structure(
        self,
        analyzer,
        spring_modulith_example
    ):
        """Test inventory module analysis"""
        result = analyzer.analyze_project(
            project_path=spring_modulith_example,
            base_package="example"
        )
        
        inventory_module = next(m for m in result.modules if m.name == "inventory")
        
        # Inventory module has services
        assert len(inventory_module.services) > 0
        assert "InventoryManagement" in inventory_module.services
    
    def test_dependency_detection(
        self,
        analyzer,
        spring_modulith_example
    ):
        """Test inter-module dependency detection"""
        result = analyzer.analyze_project(
            project_path=spring_modulith_example,
            base_package="example"
        )
        
        # Should detect inventory -> order dependency
        assert len(result.dependencies) > 0
        
        # Verify specific dependency
        dep = result.dependencies[0]
        assert dep.from_module == "inventory"
        assert dep.to_module == "order"
    
    def test_cml_generation(
        self,
        analyzer,
        spring_modulith_example,
        output_dir
    ):
        """Test CML file generation from real project"""
        result = analyzer.analyze_project(
            project_path=spring_modulith_example,
            base_package="example"
        )
        
        output_dir.mkdir(parents=True, exist_ok=True)
        cml_file = output_dir / "context_map.cml"
        
        cml_content = analyzer.generate_cml(result, cml_file)
        
        # Verify file created
        assert cml_file.exists()
        assert cml_file.stat().st_size > 0
        
        # Verify CML content
        assert "ContextMap" in cml_content
        assert "BoundedContext order" in cml_content
        assert "BoundedContext inventory" in cml_content
        assert "inventory [D,ACL] -> [U,OHS] order" in cml_content
    
    def test_json_generation(
        self,
        analyzer,
        spring_modulith_example,
        output_dir
    ):
        """Test JSON report generation from real project"""
        result = analyzer.analyze_project(
            project_path=spring_modulith_example,
            base_package="example"
        )
        
        output_dir.mkdir(parents=True, exist_ok=True)
        json_file = output_dir / "analysis.json"
        
        analyzer.generate_json_report(result, json_file)
        
        # Verify file created
        assert json_file.exists()
        
        # Verify JSON structure
        with open(json_file) as f:
            data = json.load(f)
        
        assert data["application"] == "Application"
        assert data["base_package"] == "example"
        assert len(data["modules"]) == 2
        assert len(data["dependencies"]) > 0
    
    def test_context_mapper_integration(
        self,
        spring_modulith_example,
        output_dir
    ):
        """Test SpringBootAnalyzer integrated with ContextMapper"""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        mapper = ContextMapper()
        
        result = mapper.analyze_spring_boot_source(
            project_path=spring_modulith_example,
            base_package="example",
            output_dir=output_dir
        )
        
        # Verify unified API result
        assert "application" in result
        assert "modules" in result
        assert "dependencies" in result
        assert "cml_file" in result
        assert "json_file" in result
        assert "raw_cml" in result
        
        # Verify files created
        assert Path(result["cml_file"]).exists()
        assert Path(result["json_file"]).exists()
        
        # Verify content
        assert result["application"] == "Application"
        assert len(result["modules"]) == 2
    
    def test_print_summary(
        self,
        analyzer,
        spring_modulith_example,
        capsys
    ):
        """Test summary printing"""
        result = analyzer.analyze_project(
            project_path=spring_modulith_example,
            base_package="example"
        )
        
        analyzer.print_summary(result)
        
        captured = capsys.readouterr()
        assert "Application" in captured.out
        assert "order" in captured.out
        assert "inventory" in captured.out


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
