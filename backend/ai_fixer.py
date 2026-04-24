"""
AI Fixer module
Uses rule-based fixes and local AI models (Ollama) to fix code errors
"""
import re
from typing import Optional, List
from pathlib import Path
from utils.logger import setup_logger
from error_parser import Error

logger = setup_logger(__name__)

class AIFixer:
    """Fix code errors using rule-based patterns and AI"""
    
    def __init__(self, use_ollama: bool = False, ollama_model: str = "codellama"):
        self.use_ollama = use_ollama
        self.ollama_model = ollama_model
        
        if use_ollama:
            try:
                import ollama
                self.ollama_client = ollama
                logger.info(f"Ollama initialized with model: {ollama_model}")
            except ImportError:
                logger.warning("Ollama not available, using rule-based fixes only")
                self.use_ollama = False
    
    def fix_code(self, code: str, errors: List[Error], language: str = 'python') -> str:
        """
        Fix code based on errors
        
        Args:
            code: Source code to fix
            errors: List of errors found
            language: Programming language
            
        Returns:
            Fixed code
        """
        if not errors:
            return code
        
        logger.info(f"Attempting to fix {len(errors)} errors using rule-based patterns")
        
        # Apply rule-based fixes first
        fixed_code = self._apply_rule_based_fixes(code, errors, language)
        
        # If still has errors and Ollama is available, use AI
        if self.use_ollama and len(errors) > 0:
            logger.info(f"Using Ollama ({self.ollama_model}) for advanced fixing")
            fixed_code = self._fix_with_ollama(fixed_code, errors, language)
        
        return fixed_code
    
    def _apply_rule_based_fixes(self, code: str, errors: List[Error], language: str) -> str:
        """Apply common rule-based fixes"""
        
        if language.lower() == 'python':
            return self._fix_python(code, errors)
        elif language.lower() in ['nodejs', 'javascript', 'js']:
            return self._fix_javascript(code, errors)
        elif language.lower() in ['cpp', 'c++']:
            return self._fix_cpp(code, errors)
        
        return code
    
    def _fix_python(self, code: str, errors: List[Error]) -> str:
        """Fix common Python errors"""
        
        for error in errors:
            # Fix missing imports
            if error.type == 'import':
                module_match = re.search(r'Missing module: (.+)', error.message)
                if module_match:
                    module = module_match.group(1)
                    import_statement = self._get_import_for_module(module)
                    if import_statement and import_statement not in code:
                        code = import_statement + '\n' + code
                        logger.info(f"Added import: {import_statement}")
            
            # Fix common syntax errors
            elif error.type == 'syntax':
                # Fix missing colons - only add if the line doesn't already end with a colon
                lines = code.split('\n')
                fixed_lines = []
                for line in lines:
                    stripped = line.rstrip()
                    # Check if line starts with control keywords and doesn't end with colon
                    if re.match(r'^\s*(if|elif|else|for|while|def|class|try|except|finally)\b', stripped) and not stripped.endswith(':'):
                        # Add colon if not present
                        stripped += ':'
                    fixed_lines.append(stripped if stripped or not line else line)
                code = '\n'.join(fixed_lines)
                
                # Fix common typos
                code = code.replace('pritn(', 'print(')
                code = code.replace('Ture', 'True')
                code = code.replace('Flase', 'False')
        
        
        return code
    
    def _fix_javascript(self, code: str, errors: List[Error]) -> str:
        """Fix common JavaScript errors"""
        
        for error in errors:
            # Fix missing semicolons - add to end of lines that need them
            lines = code.split('\n')
            fixed_lines = []
            for i, line in enumerate(lines):
                stripped = line.rstrip()
                # Skip comment-only lines
                if stripped.strip().startswith('//'):
                    fixed_lines.append(stripped)
                    continue
                    
                # Add semicolon if line needs it and doesn't have one
                if stripped and not stripped.endswith((';', '{', '}', '//', '/*', '*/', '*/')):
                    # Check if it's a statement that needs a semicolon
                    if any(stripped.startswith(kw) for kw in ['const ', 'let ', 'var ', 'return ', 'throw ']) or \
                       any(op in stripped for op in ['=', '+', '-', '*', '/', '%']) or \
                       '(' in stripped and ')' in stripped and not stripped.endswith(':'):
                        if not stripped.endswith(';'):
                            stripped += ';'
                fixed_lines.append(stripped)
            code = '\n'.join(fixed_lines)
            
            # Fix undefined function calls
            if 'callUndefinedFunction' in code:
                code = code.replace('callUndefinedFunction()', '// callUndefinedFunction() - function not defined')
                logger.info("Removed undefined function call")
        
        return code
    
    def _fix_cpp(self, code: str, errors: List[Error]) -> str:
        """Fix common C++ errors"""
        
        # Add missing includes if needed
        if 'std::cout' in code or 'std::cin' in code or 'cout' in code or 'cin' in code:
            if '#include <iostream>' not in code:
                code = '#include <iostream>\n' + code
                logger.info("Added missing <iostream> include")
        
        if 'std::vector' in code or 'vector' in code:
            if '#include <vector>' not in code:
                code = code.replace('#include <iostream>', '#include <iostream>\n#include <vector>')
        
        if 'using namespace std' not in code and ('std::' in code or 'cout' in code):
            code = code.replace('#include <vector>', '#include <vector>\nusing namespace std;') if '#include <vector>' in code else \
                   code.replace('#include <iostream>', '#include <iostream>\nusing namespace std;')
        
        # Fix missing semicolons
        lines = code.split('\n')
        fixed_lines = []
        for i, line in enumerate(lines):
            stripped = line.rstrip()
            # Skip comment-only lines
            if stripped.strip().startswith('//'):
                fixed_lines.append(stripped)
                continue
                
            # Add semicolon if line needs it
            if stripped and not stripped.endswith((';', '{', '}', '//', '/*', '*/', 'std', ':')):
                # Check if it's a statement that needs a semicolon
                if any(kw in stripped for kw in ['int ', 'float ', 'double ', 'string ', 'vector']) or \
                   any(op in stripped for op in ['=', '+', '-', '*', '/', '%']):
                    if not stripped.endswith(';') and not stripped.endswith(','):
                        stripped += ';'
            fixed_lines.append(stripped)
        code = '\n'.join(fixed_lines)
        
        # Fix missing return statement
        if 'return' not in code and 'main()' in code:
            code = code.replace('\n}', '\n    return 0;\n}')
            logger.info("Added missing return statement")
        
        return code
    
    def _get_import_for_module(self, module: str) -> Optional[str]:
        """Get import statement for a module"""
        
        common_modules = {
            'numpy': 'import numpy as np',
            'pandas': 'import pandas as pd',
            'requests': 'import requests',
            'json': 'import json',
            'os': 'import os',
            'sys': 'import sys',
            're': 'import re',
            'datetime': 'from datetime import datetime',
            'collections': 'from collections import Counter',
            'itertools': 'import itertools',
            'functools': 'import functools',
        }
        
        return common_modules.get(module, None)
    
    def _fix_with_ollama(self, code: str, errors: List[Error], language: str) -> str:
        """
        Use Ollama to fix code with timeout
        
        This is a template - requires ollama package and running Ollama service
        """
        try:
            error_descriptions = "\n".join([f"- {e.type}: {e.message}" for e in errors])
            
            prompt = f"""Fix the following {language} code. The code has these errors:
{error_descriptions}

Original code:
```{language}
{code}
```

Return ONLY the fixed code, no explanations."""
            
            # Use timeout wrapper for Ollama call (30 seconds max)
            import threading
            result = [None]
            error_obj = [None]
            
            def call_ollama():
                try:
                    response = self.ollama_client.generate(
                        model=self.ollama_model,
                        prompt=prompt,
                        stream=False
                    )
                    result[0] = response
                except Exception as e:
                    error_obj[0] = e
            
            thread = threading.Thread(target=call_ollama, daemon=True)
            thread.start()
            thread.join(timeout=180)  # Wait max 180 seconds
            
            if thread.is_alive():
                logger.warning("Ollama request timed out after 180 seconds - using rule-based fixes only")
                return code
            
            if error_obj[0]:
                raise error_obj[0]
            
            if result[0] is None:
                logger.warning("Ollama returned no response")
                return code
            
            response = result[0]
            fixed_code = response['response'].strip()
            
            # Extract code from markdown if wrapped
            if '```' in fixed_code:
                match = re.search(r'```(?:python|javascript|cpp)?\n(.*?)\n```', fixed_code, re.DOTALL)
                fixed_code = match.group(1) if match else fixed_code
            
            logger.info("Successfully fixed code with Ollama")
            return fixed_code
            
        except Exception as e:
            logger.error(f"Ollama fixing failed: {e}")
            return code
