"""
Error parser module
Extracts and categorizes errors from code output
"""
import re
from typing import List, Dict, Optional
from dataclasses import dataclass
from utils.logger import setup_logger

logger = setup_logger(__name__)

@dataclass
class Error:
    """Represents a code error"""
    type: str  # 'syntax', 'runtime', 'import', 'type', 'unknown'
    message: str
    line_number: Optional[int] = None
    file_name: Optional[str] = None
    raw_output: str = ""

class ErrorParser:
    """Parse and extract errors from execution output"""
    
    # Regex patterns for common errors
    PYTHON_SYNTAX_PATTERN = r'SyntaxError: .+ \(line (\d+)\)|File "(.+?)", line (\d+)'
    PYTHON_IMPORT_PATTERN = r'ModuleNotFoundError: No module named [\'"](.+?)[\'"]'
    PYTHON_RUNTIME_PATTERN = r'(\w+Error): (.+)'
    
    NODEJS_SYNTAX_PATTERN = r'SyntaxError: (.+)'
    NODEJS_ERROR_PATTERN = r'Error: (.+)'
    
    CPP_ERROR_PATTERN = r'error: (.+)'
    
    def __init__(self):
        logger.info("ErrorParser initialized")
    
    def parse(self, stderr: str, stdout: str, language: str = 'python') -> List[Error]:
        """
        Parse errors from output
        
        Args:
            stderr: Standard error output
            stdout: Standard output
            language: Programming language ('python', 'nodejs', 'cpp')
            
        Returns:
            List of Error objects
        """
        combined_output = stderr + "\n" + stdout
        errors = []
        
        if language.lower() == 'python':
            errors = self._parse_python_errors(combined_output)
        elif language.lower() in ['nodejs', 'javascript', 'js']:
            errors = self._parse_nodejs_errors(combined_output)
        elif language.lower() in ['cpp', 'c++']:
            errors = self._parse_cpp_errors(combined_output)
        
        logger.info(f"Parsed {len(errors)} errors from {language} output")
        return errors
    
    def _parse_python_errors(self, output: str) -> List[Error]:
        """Parse Python errors"""
        errors = []
        lines = output.split('\n')
        
        for i, line in enumerate(lines):
            # Check for syntax errors
            if 'SyntaxError' in line:
                error = Error(
                    type='syntax',
                    message=line.strip(),
                    raw_output=output
                )
                errors.append(error)
            
            # Check for import errors
            elif 'ModuleNotFoundError' in line or 'ImportError' in line:
                match = re.search(r"No module named ['\"](.+?)['\"]", line)
                module_name = match.group(1) if match else 'unknown'
                error = Error(
                    type='import',
                    message=f"Missing module: {module_name}",
                    raw_output=output
                )
                errors.append(error)
            
            # Check for runtime errors
            elif re.search(r'\w+Error:', line):
                error = Error(
                    type='runtime',
                    message=line.strip(),
                    raw_output=output
                )
                errors.append(error)
        
        return errors if errors else self._parse_generic_errors(output)
    
    def _parse_nodejs_errors(self, output: str) -> List[Error]:
        """Parse Node.js errors"""
        errors = []
        
        if 'SyntaxError' in output:
            error = Error(
                type='syntax',
                message=output.strip(),
                raw_output=output
            )
            errors.append(error)
        elif 'Error' in output:
            error = Error(
                type='runtime',
                message=output.strip(),
                raw_output=output
            )
            errors.append(error)
        
        return errors if errors else self._parse_generic_errors(output)
    
    def _parse_cpp_errors(self, output: str) -> List[Error]:
        """Parse C++ compilation and runtime errors"""
        errors = []
        
        for line in output.split('\n'):
            if 'error:' in line.lower():
                error = Error(
                    type='syntax' if 'error:' in line else 'runtime',
                    message=line.strip(),
                    raw_output=output
                )
                errors.append(error)
        
        return errors if errors else self._parse_generic_errors(output)
    
    def _parse_generic_errors(self, output: str) -> List[Error]:
        """Fallback: Create a generic error if output contains issues"""
        if output.strip():
            return [Error(
                type='unknown',
                message=output.strip(),
                raw_output=output
            )]
        return []
    
    def has_errors(self, stderr: str, stdout: str) -> bool:
        """Check if output contains errors"""
        return bool(stderr.strip()) or 'error' in stdout.lower() or 'traceback' in stdout.lower()
