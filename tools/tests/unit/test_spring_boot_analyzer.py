"""
Unit tests for Spring Boot Analyzer module.

Tests the source code analysis capabilities without requiring real projects.
"""

import pytest
import tempfile
from pathlib import Path
from src.utils.spring_boot_analyzer import (
    SpringBootAnalyzer,
    SpringBootAnalyzerError,
    ModuleInfo,
    ModuleDependency,
    AnalysisResult
)


class TestSpringBootAnalyzer:
    """Test suite for SpringBootAnalyzer"""
    
    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance"""
        return SpringBootAnalyzer()
    
    @pytest.fixture
    def temp_project(self, tmp_path):
        """Create a minimal Spring Boot project structure"""
        # Create directory structure
        base_pkg = tmp_path / "src" / "main" / "java" / "com" / "example" / "app"
        base_pkg.mkdir(parents=True)
        
        # Create Application class
        app_file = base_pkg / "Application.java"
        app_file.write_text("""
package com.example.app;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

@SpringBootApplication
public class Application {
    public static void main(String[] args) {
        SpringApplication.run(Application.class, args);
    }
}
""")
        
        # Create order module
        order_pkg = base_pkg / "order"
        order_pkg.mkdir()
        
        order_service = order_pkg / "OrderService.java"
        order_service.write_text("""
package com.example.app.order;

import org.springframework.stereotype.Service;

@Service
public class OrderService {
}
""")
        
        order_entity = order_pkg / "Order.java"
        order_entity.write_text("""
package com.example.app.order;

import javax.persistence.Entity;

@Entity
public class Order {
}
""")
        
        # Create inventory module
        inventory_pkg = base_pkg / "inventory"
        inventory_pkg.mkdir()
        
        inventory_service = inventory_pkg / "InventoryService.java"
        inventory_service.write_text("""
package com.example.app.inventory;

import org.springframework.stereotype.Service;
import com.example.app.order.Order;

@Service
public class InventoryService {
    // Depends on order module
}
""")
        
        return tmp_path
    
    def test_analyzer_initialization(self, analyzer):
        """Test analyzer can be created"""
        assert analyzer is not None
        assert isinstance(analyzer, SpringBootAnalyzer)
    
    def test_analyze_valid_project(self, analyzer, temp_project):
        """Test analyzing a valid Spring Boot project"""
        result = analyzer.analyze_project(
            project_path=temp_project,
            base_package="com.example.app"
        )
        
        assert isinstance(result, AnalysisResult)
        assert result.application_class == "Application"
        assert result.base_package == "com.example.app"
        assert len(result.modules) == 2
    
    def test_project_not_found(self, analyzer):
        """Test error when project path doesn't exist"""
        with pytest.raises(SpringBootAnalyzerError) as exc:
            analyzer.analyze_project(
                project_path=Path("/nonexistent/path"),
                base_package="com.example"
            )
        assert "does not exist" in str(exc.value)
    
    def test_no_src_directory(self, analyzer, tmp_path):
        """Test error when src/main/java doesn't exist"""
        with pytest.raises(SpringBootAnalyzerError) as exc:
            analyzer.analyze_project(
                project_path=tmp_path,
                base_package="com.example"
            )
        assert "Source directory not found" in str(exc.value)
    
    def test_invalid_base_package(self, analyzer, temp_project):
        """Test error when base package is wrong"""
        with pytest.raises(SpringBootAnalyzerError) as exc:
            analyzer.analyze_project(
                project_path=temp_project,
                base_package="com.wrong.package"
            )
        assert "Package path not found" in str(exc.value)
    
    def test_no_spring_boot_application(self, analyzer, tmp_path):
        """Test error when no @SpringBootApplication found"""
        # Create structure without @SpringBootApplication
        src_dir = tmp_path / "src" / "main" / "java" / "com" / "example"
        src_dir.mkdir(parents=True)
        
        regular_class = src_dir / "RegularClass.java"
        regular_class.write_text("""
package com.example;

public class RegularClass {
}
""")
        
        with pytest.raises(SpringBootAnalyzerError) as exc:
            analyzer.analyze_project(
                project_path=tmp_path,
                base_package="com.example"
            )
        assert "@SpringBootApplication" in str(exc.value)
    
    def test_module_detection(self, analyzer, temp_project):
        """Test module detection"""
        result = analyzer.analyze_project(
            project_path=temp_project,
            base_package="com.example.app"
        )
        
        module_names = [m.name for m in result.modules]
        assert "order" in module_names
        assert "inventory" in module_names
    
    def test_service_classification(self, analyzer, temp_project):
        """Test service class classification"""
        result = analyzer.analyze_project(
            project_path=temp_project,
            base_package="com.example.app"
        )
        
        order_module = next(m for m in result.modules if m.name == "order")
        assert "OrderService" in order_module.services
    
    def test_entity_classification(self, analyzer, temp_project):
        """Test entity class classification"""
        result = analyzer.analyze_project(
            project_path=temp_project,
            base_package="com.example.app"
        )
        
        order_module = next(m for m in result.modules if m.name == "order")
        assert "Order" in order_module.entities
    
    def test_dependency_detection(self, analyzer, temp_project):
        """Test inter-module dependency detection"""
        result = analyzer.analyze_project(
            project_path=temp_project,
            base_package="com.example.app"
        )
        
        # inventory module imports from order module
        assert len(result.dependencies) > 0
        dep = result.dependencies[0]
        assert dep.from_module == "inventory"
        assert dep.to_module == "order"
    
    def test_generate_cml(self, analyzer, temp_project, tmp_path):
        """Test CML file generation"""
        result = analyzer.analyze_project(
            project_path=temp_project,
            base_package="com.example.app"
        )
        
        cml_file = tmp_path / "output.cml"
        cml_content = analyzer.generate_cml(result, cml_file)
        
        assert cml_file.exists()
        assert "ContextMap" in cml_content
        assert "BoundedContext order" in cml_content
        assert "BoundedContext inventory" in cml_content
    
    def test_generate_json_report(self, analyzer, temp_project, tmp_path):
        """Test JSON report generation"""
        result = analyzer.analyze_project(
            project_path=temp_project,
            base_package="com.example.app"
        )
        
        json_file = tmp_path / "output.json"
        analyzer.generate_json_report(result, json_file)
        
        assert json_file.exists()
        
        import json
        with open(json_file) as f:
            data = json.load(f)
        
        assert data["application"] == "Application"
        assert len(data["modules"]) == 2
    
    def test_module_info_to_dict(self):
        """Test ModuleInfo serialization"""
        module = ModuleInfo(
            name="order",
            package="com.example.order",
            entities=["Order"],
            services=["OrderService"],
            events=["OrderCreated"],
            repositories=["OrderRepository"],
            controllers=["OrderController"],
            all_classes=["Order", "OrderService"]
        )
        
        result = module.to_dict()
        assert result["name"] == "order"
        assert "Order" in result["entities"]
        assert "OrderService" in result["services"]
    
    def test_module_dependency_to_dict(self):
        """Test ModuleDependency serialization"""
        dep = ModuleDependency(
            from_module="inventory",
            to_module="order",
            dependency_type="imports"
        )
        
        result = dep.to_dict()
        assert result["from"] == "inventory"
        assert result["to"] == "order"
        assert result["type"] == "imports"
    
    def test_analysis_result_to_dict(self):
        """Test AnalysisResult serialization"""
        module = ModuleInfo(
            name="order",
            package="com.example.order",
            entities=[],
            services=["OrderService"],
            events=[],
            repositories=[],
            controllers=[],
            all_classes=["OrderService"]
        )
        
        dep = ModuleDependency("inventory", "order")
        
        result = AnalysisResult(
            application_class="Application",
            base_package="com.example",
            modules=[module],
            dependencies=[dep]
        )
        
        data = result.to_dict()
        assert data["application"] == "Application"
        assert len(data["modules"]) == 1
        assert len(data["dependencies"]) == 1
    
    def test_annotation_detection(self, analyzer):
        """Test annotation pattern matching"""
        content_with_entity = "@Entity public class Order {}"
        content_with_service = "@Service public class OrderService {}"
        content_without = "public class RegularClass {}"
        
        assert analyzer._has_annotation(content_with_entity, "entity")
        assert analyzer._has_annotation(content_with_service, "service")
        assert not analyzer._has_annotation(content_without, "entity")
        assert not analyzer._has_annotation(content_without, "service")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
