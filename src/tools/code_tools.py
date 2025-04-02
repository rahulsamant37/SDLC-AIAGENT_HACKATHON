"""
Custom tools for SDLC specific tasks.
"""
from typing import Dict, Any, List, Optional, Type
from langchain.tools import BaseTool
import re
import json

class CodeAnalysisTool(BaseTool):
    """Tool for analyzing code quality and suggesting improvements."""
    
    name = "code_analysis_tool"
    description = "Analyzes code quality and suggests improvements"
    
    def _run(self, code: str) -> str:
        """
        Run code analysis.
        
        Args:
            code (str): The code to analyze.
            
        Returns:
            str: Analysis results.
        """
        # This is a simplified implementation
        analysis_results = {
            "metrics": {
                "lines_of_code": len(code.split("\n")),
                "complexity": self._calculate_complexity(code),
                "function_count": len(re.findall(r"def\s+\w+\s*\(", code)),
                "class_count": len(re.findall(r"class\s+\w+\s*[:\(]", code)),
            },
            "issues": self._identify_issues(code),
            "recommendations": self._generate_recommendations(code)
        }
        
        return json.dumps(analysis_results, indent=2)
    
    def _arun(self, code: str) -> str:
        """
        Run code analysis asynchronously.
        
        Args:
            code (str): The code to analyze.
            
        Returns:
            str: Analysis results.
        """
        # For now, just call the synchronous version
        return self._run(code)
    
    def _calculate_complexity(self, code: str) -> int:
        """
        Calculate code complexity.
        
        Args:
            code (str): The code to analyze.
            
        Returns:
            int: Complexity score.
        """
        # Simple complexity metric based on control structures
        control_structures = len(re.findall(r"\b(if|for|while|elif|else)\b", code))
        functions = len(re.findall(r"def\s+\w+\s*\(", code))
        classes = len(re.findall(r"class\s+\w+\s*[:\(]", code))
        
        return control_structures + functions * 2 + classes * 3
    
    def _identify_issues(self, code: str) -> List[Dict[str, Any]]:
        """
        Identify potential issues in the code.
        
        Args:
            code (str): The code to analyze.
            
        Returns:
            List[Dict[str, Any]]: List of identified issues.
        """
        issues = []
        
        # Check for hardcoded credentials
        if re.search(r"(password|api_key|secret|token)\s*=\s*['\"][^'\"]+['\"]", code, re.IGNORECASE):
            issues.append({
                "severity": "high",
                "type": "security",
                "description": "Hardcoded credentials detected",
                "locations": []  # In a real implementation, we would include line numbers
            })
        
        # Check for overly long functions
        long_functions = []
        function_pattern = r"def\s+(\w+)\s*\([^)]*\):"
        for match in re.finditer(function_pattern, code):
            function_name = match.group(1)
            function_start = match.start()
            # Find the next function or class definition
            next_def = re.search(r"(def|class)\s+", code[function_start+1:])
            if next_def:
                function_end = function_start + 1 + next_def.start()
                function_code = code[function_start:function_end]
                function_lines = function_code.count("\n")
                if function_lines > 50:
                    long_functions.append(function_name)
        
        if long_functions:
            issues.append({
                "severity": "medium",
                "type": "maintainability",
                "description": f"Overly long functions detected: {', '.join(long_functions)}",
                "locations": []
            })
        
        # Check for unused imports
        imports = re.findall(r"import\s+(\w+)|from\s+[\w.]+\s+import\s+(\w+)(?:\s*,\s*(\w+))*", code)
        imported_modules = []
        for imp in imports:
            for module in imp:
                if module and module not in imported_modules:
                    imported_modules.append(module)
        
        unused_imports = []
        for module in imported_modules:
            # Check if the module is used anywhere else in the code
            if not re.search(rf"\b{module}\b", code[code.find(module)+len(module):]):
                unused_imports.append(module)
        
        if unused_imports:
            issues.append({
                "severity": "low",
                "type": "style",
                "description": f"Unused imports detected: {', '.join(unused_imports)}",
                "locations": []
            })
        
        return issues
    
    def _generate_recommendations(self, code: str) -> List[str]:
        """
        Generate recommendations for improving the code.
        
        Args:
            code (str): The code to analyze.
            
        Returns:
            List[str]: List of recommendations.
        """
        recommendations = []
        
        # Check for missing docstrings
        if not re.search(r'"""', code):
            recommendations.append("Add docstrings to improve code documentation")
        
        # Check for missing type hints
        if not re.search(r"def\s+\w+\s*\([^)]*\)\s*->\s*\w+\s*:", code):
            recommendations.append("Add type hints to improve code maintainability")
        
        # Check for missing error handling
        if re.search(r"def\s+\w+", code) and not re.search(r"try\s*:", code):
            recommendations.append("Add error handling to improve code robustness")
        
        # Check for missing tests
        if not re.search(r"def\s+test_", code) and not re.search(r"unittest|pytest", code):
            recommendations.append("Add unit tests to ensure code correctness")
        
        return recommendations

class SecurityScanTool(BaseTool):
    """Tool for scanning code for security vulnerabilities."""
    
    name = "security_scan_tool"
    description = "Scans code for security vulnerabilities"
    
    def _run(self, code: str) -> str:
        """
        Run security scan.
        
        Args:
            code (str): The code to scan.
            
        Returns:
            str: Security scan results.
        """
        # This is a simplified implementation
        vulnerabilities = []
        
        # Check for SQL injection vulnerabilities
        if re.search(r"execute\(\s*f?['\"].*\{.*\}.*['\"]", code) or re.search(r"execute\(\s*['\"].*\%s.*['\"].*%" , code):
            vulnerabilities.append({
                "severity": "critical",
                "type": "sql_injection",
                "description": "Potential SQL injection vulnerability detected",
                "recommendation": "Use parameterized queries instead of string formatting"
            })
        
        # Check for command injection vulnerabilities
        if re.search(r"os\.system\(|subprocess\.call\(|subprocess\.run\(|subprocess\.Popen\(", code):
            vulnerabilities.append({
                "severity": "high",
                "type": "command_injection",
                "description": "Potential command injection vulnerability detected",
                "recommendation": "Validate and sanitize user input before using it in system commands"
            })
        
        # Check for hardcoded credentials
        if re.search(r"(password|api_key|secret|token)\s*=\s*['\"][^'\"]+['\"]", code, re.IGNORECASE):
            vulnerabilities.append({
                "severity": "high",
                "type": "hardcoded_credentials",
                "description": "Hardcoded credentials detected",
                "recommendation": "Use environment variables or a secure vault for storing credentials"
            })
        
        # Check for insecure deserialization
        if re.search(r"pickle\.loads|yaml\.load\s*\((?!.*Loader=yaml\.SafeLoader)", code):
            vulnerabilities.append({
                "severity": "high",
                "type": "insecure_deserialization",
                "description": "Insecure deserialization detected",
                "recommendation": "Use secure deserialization methods (pickle.loads with trusted data only, yaml.safe_load)"
            })
        
        # Check for insecure file operations
        if re.search(r"open\(\s*.*\+\s*['\"]w['\"]", code):
            vulnerabilities.append({
                "severity": "medium",
                "type": "insecure_file_operations",
                "description": "Insecure file operations detected",
                "recommendation": "Ensure proper file permissions and validate file paths"
            })
        
        # Check for missing input validation
        if re.search(r"request\.form|request\.args|request\.json", code) and not re.search(r"validate|sanitize|clean", code):
            vulnerabilities.append({
                "severity": "medium",
                "type": "missing_input_validation",
                "description": "Missing input validation detected",
                "recommendation": "Add input validation for all user-provided data"
            })
        
        scan_results = {
            "vulnerabilities": vulnerabilities,
            "secure_coding_checklist": [
                "Use parameterized queries for database operations",
                "Validate and sanitize all user inputs",
                "Store credentials in environment variables",
                "Implement proper error handling",
                "Use HTTPS for all external communications",
                "Implement proper authentication and authorization",
                "Keep dependencies up to date"
            ]
        }
        
        return json.dumps(scan_results, indent=2)
    
    def _arun(self, code: str) -> str:
        """
        Run security scan asynchronously.
        
        Args:
            code (str): The code to scan.
            
        Returns:
            str: Security scan results.
        """
        # For now, just call the synchronous version
        return self._run(code)

class TestGenerationTool(BaseTool):
    """Tool for generating unit tests for code."""
    
    name = "test_generation_tool"
    description = "Generates unit tests for code"
    
    def _run(self, code: str, framework: str = "pytest") -> str:
        """
        Generate unit tests for the given code.
        
        Args:
            code (str): The code to generate tests for.
            framework (str): The testing framework to use.
            
        Returns:
            str: Generated test code.
        """
        # This is a simplified implementation
        function_matches = re.finditer(r"def\s+(\w+)\s*\(([^)]*)\)(?:\s*->\s*([^:]+))?:", code)
        
        class_matches = re.finditer(r"class\s+(\w+)(?:\([^)]*\))?:", code)
        
        test_code = f"# Generated test code using {framework}\n"
        
        if framework == "pytest":
            test_code += "import pytest\n"
        elif framework == "unittest":
            test_code += "import unittest\n"
        
        # Add imports from the original code
        imports = re.findall(r"(import\s+.*|from\s+.*import\s+.*)", code)
        for imp in imports:
            test_code += imp + "\n"
        
        test_code += "\n\n"
        
        # Generate tests for functions
        for match in function_matches:
            function_name = match.group(1)
            
            # Skip if it's already a test function
            if function_name.startswith("test_"):
                continue
            
            parameters = match.group(2)
            return_type = match.group(3) if match.group(3) else "Any"
            
            param_list = [p.strip() for p in parameters.split(",") if p.strip()]
            
            if framework == "pytest":
                test_code += f"def test_{function_name}():\n"
                test_code += f"    # Arrange\n"
                
                # Generate test parameter values
                for param in param_list:
                    param_name = param.split(":")[0].strip()
                    param_type = param.split(":")[-1].strip() if ":" in param else "Any"
                    
                    if "int" in param_type:
                        test_code += f"    {param_name} = 0\n"
                    elif "float" in param_type:
                        test_code += f"    {param_name} = 0.0\n"
                    elif "str" in param_type:
                        test_code += f"    {param_name} = \"\"\n"
                    elif "bool" in param_type:
                        test_code += f"    {param_name} = False\n"
                    elif "list" in param_type or "List" in param_type:
                        test_code += f"    {param_name} = []\n"
                    elif "dict" in param_type or "Dict" in param_type:
                        test_code += f"    {param_name} = {{}}\n"
                    else:
                        test_code += f"    {param_name} = None\n"
                
                # Call the function
                param_names = [p.split(":")[0].strip() for p in param_list]
                param_str = ", ".join(param_names)
                
                test_code += f"    \n    # Act\n"
                test_code += f"    result = {function_name}({param_str})\n"
                test_code += f"    \n    # Assert\n"
                
                if "None" not in return_type:
                    test_code += f"    assert result is not None\n"
                else:
                    test_code += f"    assert result is None\n"
            
            elif framework == "unittest":
                test_code += f"class Test{function_name.capitalize()}(unittest.TestCase):\n"
                test_code += f"    def test_{function_name}(self):\n"
                test_code += f"        # Arrange\n"
                
                # Generate test parameter values
                for param in param_list:
                    param_name = param.split(":")[0].strip()
                    param_type = param.split(":")[-1].strip() if ":" in param else "Any"
                    
                    if "int" in param_type:
                        test_code += f"        {param_name} = 0\n"
                    elif "float" in param_type:
                        test_code += f"        {param_name} = 0.0\n"
                    elif "str" in param_type:
                        test_code += f"        {param_name} = \"\"\n"
                    elif "bool" in param_type:
                        test_code += f"        {param_name} = False\n"
                    elif "list" in param_type or "List" in param_type:
                        test_code += f"        {param_name} = []\n"
                    elif "dict" in param_type or "Dict" in param_type:
                        test_code += f"        {param_name} = {{}}\n"
                    else:
                        test_code += f"        {param_name} = None\n"
                
                # Call the function
                param_names = [p.split(":")[0].strip() for p in param_list]
                param_str = ", ".join(param_names)
                
                test_code += f"        \n        # Act\n"
                test_code += f"        result = {function_name}({param_str})\n"
                test_code += f"        \n        # Assert\n"
                
                if "None" not in return_type:
                    test_code += f"        self.assertIsNotNone(result)\n"
                else:
                    test_code += f"        self.assertIsNone(result)\n"
            
            test_code += "\n\n"
        
        # Generate tests for classes
        for match in class_matches:
            class_name = match.group(1)
            
            # Skip if it's already a test class
            if class_name.startswith("Test"):
                continue
            
            if framework == "pytest":
                test_code += f"class TestClass{class_name}:\n"
                test_code += f"    def test_init(self):\n"
                test_code += f"        # Arrange & Act\n"
                test_code += f"        instance = {class_name}()\n"
                test_code += f"        \n        # Assert\n"
                test_code += f"        assert instance is not None\n"
                
            elif framework == "unittest":
                test_code += f"class Test{class_name}(unittest.TestCase):\n"
                test_code += f"    def test_init(self):\n"
                test_code += f"        # Arrange & Act\n"
                test_code += f"        instance = {class_name}()\n"
                test_code += f"        \n        # Assert\n"
                test_code += f"        self.assertIsNotNone(instance)\n"
            
            test_code += "\n\n"
        
        if framework == "unittest":
            test_code += "if __name__ == '__main__':\n"
            test_code += "    unittest.main()\n"
        
        return test_code
    
    def _arun(self, code: str, framework: str = "pytest") -> str:
        """
        Generate unit tests asynchronously.
        
        Args:
            code (str): The code to generate tests for.
            framework (str): The testing framework to use.
            
        Returns:
            str: Generated test code.
        """
        # For now, just call the synchronous version
        return self._run(code, framework)

class DocumentationGeneratorTool(BaseTool):
    """Tool for generating documentation for code."""
    
    name = "documentation_generator_tool"
    description = "Generates documentation for code"
    
    def _run(self, code: str, format: str = "markdown") -> str:
        """
        Generate documentation for the given code.
        
        Args:
            code (str): The code to generate documentation for.
            format (str): The documentation format (markdown or rst).
            
        Returns:
            str: Generated documentation.
        """
        # This is a simplified implementation
        docs = ""
        
        if format == "markdown":
            docs += "# Code Documentation\n\n"
        elif format == "rst":
            docs += "Code Documentation\n=================\n\n"
        
        # Extract module docstring
        module_docstring = re.search(r'^"""(.*?)"""', code, re.DOTALL)
        if module_docstring:
            if format == "markdown":
                docs += "## Module Description\n\n"
                docs += module_docstring.group(1).strip() + "\n\n"
            elif format == "rst":
                docs += "Module Description\n-----------------\n\n"
                docs += module_docstring.group(1).strip() + "\n\n"
        
        # Extract classes
        class_matches = re.finditer(r"class\s+(\w+)(?:\([^)]*\))?:(.*?)(?=\n\S|\Z)", code, re.DOTALL)
        
        if format == "markdown":
            docs += "## Classes\n\n"
        elif format == "rst":
            docs += "Classes\n-------\n\n"
        
        for match in class_matches:
            class_name = match.group(1)
            class_body = match.group(2)
            
            if format == "markdown":
                docs += f"### {class_name}\n\n"
            elif format == "rst":
                docs += f"{class_name}\n{'~' * len(class_name)}\n\n"
            
            # Extract class docstring
            class_docstring = re.search(r'"""(.*?)"""', class_body, re.DOTALL)
            if class_docstring:
                docs += class_docstring.group(1).strip() + "\n\n"
            
            # Extract methods
            method_matches = re.finditer(r"def\s+(\w+)\s*\(([^)]*)\)(?:\s*->\s*([^:]+))?:(.*?)(?=\n\s*def|\n\S|\Z)", class_body, re.DOTALL)
            
            if format == "markdown":
                docs += "#### Methods\n\n"
            elif format == "rst":
                docs += "Methods\n\"\"\"\"\"\"\n\n"
            
            for method_match in method_matches:
                method_name = method_match.group(1)
                parameters = method_match.group(2)
                return_type = method_match.group(3) if method_match.group(3) else "None"
                method_body = method_match.group(4)
                
                if format == "markdown":
                    docs += f"##### `{method_name}({parameters}) -> {return_type}`\n\n"
                elif format == "rst":
                    docs += f"**{method_name}({parameters}) -> {return_type}**\n\n"
                
                # Extract method docstring
                method_docstring = re.search(r'"""(.*?)"""', method_body, re.DOTALL)
                if method_docstring:
                    docs += method_docstring.group(1).strip() + "\n\n"
        
        # Extract standalone functions
        function_matches = re.finditer(r"^def\s+(\w+)\s*\(([^)]*)\)(?:\s*->\s*([^:]+))?:(.*?)(?=^def|\Z)", code, re.DOTALL | re.MULTILINE)
        
        if format == "markdown":
            docs += "## Functions\n\n"
        elif format == "rst":
            docs += "Functions\n---------\n\n"
        
        for match in function_matches:
            function_name = match.group(1)
            parameters = match.group(2)
            return_type = match.group(3) if match.group(3) else "None"
            function_body = match.group(4)
            
            if format == "markdown":
                docs += f"### `{function_name}({parameters}) -> {return_type}`\n\n"
            elif format == "rst":
                docs += f"**{function_name}({parameters}) -> {return_type}**\n\n"
            
            # Extract function docstring
            function_docstring = re.search(r'"""(.*?)"""', function_body, re.DOTALL)
            if function_docstring:
                docs += function_docstring.group(1).strip() + "\n\n"
        
        return docs
    
    def _arun(self, code: str, format: str = "markdown") -> str:
        """
        Generate documentation asynchronously.
        
        Args:
            code (str): The code to generate documentation for.
            format (str): The documentation format (markdown or rst).
            
        Returns:
            str: Generated documentation.
        """
        # For now, just call the synchronous version
        return self._run(code, format)

def get_sdlc_tools() -> List[BaseTool]:
    """
    Get a list of all SDLC tools.
    
    Returns:
        List[BaseTool]: List of SDLC tools.
    """
    return [
        CodeAnalysisTool(),
        SecurityScanTool(),
        TestGenerationTool(),
        DocumentationGeneratorTool()
    ]