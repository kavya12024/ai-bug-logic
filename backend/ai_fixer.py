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
                # Missing colons
                code = re.sub(r'(if|elif|else|for|while|def|class) (.+)\n', r'\1 \2:\n', code)
                
                # Fix common typos
                code = code.replace('pritn(', 'print(')
                code = code.replace('Ture', 'True')
                code = code.replace('Flase', 'False')
                code = code.replace('None', 'None')
        
        return code
    
    def _fix_javascript(self, code: str, errors: List[Error]) -> str:
        """Fix common JavaScript errors"""
        
        for error in errors:
            if 'undefined' in error.message.lower():
                # Try to add var/const declarations
                pass
            elif 'syntax' in error.message.lower():
                # Fix missing semicolons (optional in JS, but common issue)
                pass
        
        return code
    
    def _fix_cpp(self, code: str, errors: List[Error]) -> str:
        """Fix common C++ errors"""
        
        for error in errors:
            if "error: 'cout'" in error.message or "'cout' was not declared" in error.message:
                if '#include <iostream>' not in code:
                    code = '#include <iostream>\nusing namespace std;\n\n' + code
                    logger.info("Added missing C++ includes")
        
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
        Use Ollama to fix code
        
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
            
            response = self.ollama_client.generate(
                model=self.ollama_model,
                prompt=prompt,
                stream=False
            )
            
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
