"""
Loop executor module
Main loop that executes code, captures errors, fixes them, and iterates
"""
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, field
from git_handler import GitHandler
from docker_runner import DockerRunner
from error_parser import ErrorParser, Error
from ai_fixer import AIFixer
from utils.logger import setup_logger
from config import Config

logger = setup_logger(__name__)

@dataclass
class ExecutionResult:
    """Result of a code fix iteration"""
    iteration: int
    success: bool
    exit_code: int
    stdout: str
    stderr: str
    errors: List[Error] = field(default_factory=list)
    fixed_code: Optional[str] = None
    error_message: str = ""

class LoopExecutor:
    """Execute code fixing loop"""
    
    def __init__(self, use_ollama: bool = False):
        self.git_handler = GitHandler()
        self.docker_runner = DockerRunner()
        self.error_parser = ErrorParser()
        self.ai_fixer = AIFixer(use_ollama=use_ollama)
        logger.info("LoopExecutor initialized")
    
    def execute_fix_loop(
        self,
        file_path: Path,
        language: str,
        max_attempts: int = None,
        timeout: int = None
    ) -> List[ExecutionResult]:
        """
        Execute the fix loop for a file
        
        Args:
            file_path: Path to the code file
            language: Programming language
            max_attempts: Maximum fix attempts (defaults to Config.MAX_FIX_ATTEMPTS)
            timeout: Timeout for each execution
            
        Returns:
            List of ExecutionResult for each iteration
        """
        if max_attempts is None:
            max_attempts = Config.MAX_FIX_ATTEMPTS
        
        if timeout is None:
            timeout = Config.TIMEOUT_SECONDS
        
        results = []
        
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            current_code = f.read()
        
        logger.info(f"Starting fix loop for {file_path} (max {max_attempts} attempts)")
        
        for attempt in range(1, max_attempts + 1):
            logger.info(f"Attempt {attempt}/{max_attempts}")
            
            # Run the code
            exit_code, stdout, stderr = self.docker_runner.run_file(
                file_path, language, timeout
            )
            
            result = ExecutionResult(
                iteration=attempt,
                success=exit_code == 0,
                exit_code=exit_code,
                stdout=stdout,
                stderr=stderr
            )
            
            # Check for errors
            errors = self.error_parser.parse(stderr, stdout, language)
            result.errors = errors
            
            if not errors:
                logger.info(f"✓ Code executed successfully on attempt {attempt}")
                results.append(result)
                break
            
            logger.info(f"✗ Found {len(errors)} errors on attempt {attempt}")
            
            # Print errors
            for error in errors:
                logger.info(f"  - {error.type}: {error.message}")
            
            # Try to fix
            fixed_code = self.ai_fixer.fix_code(current_code, errors, language)
            result.fixed_code = fixed_code
            
            # Check if fix is different
            if fixed_code == current_code:
                logger.warning(f"No changes made on attempt {attempt}, stopping loop")
                result.error_message = "No fix available"
                results.append(result)
                break
            
            # Update file with fixed code
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(fixed_code)
            
            current_code = fixed_code
            results.append(result)
            
            logger.info(f"Updated file with fixed code")
        
        return results
    
    def get_summary(self, results: List[ExecutionResult]) -> Dict:
        """Get summary of fix loop results"""
        
        total_errors = sum(len(r.errors) for r in results)
        successful = any(r.success for r in results)
        final_attempt = len(results)
        
        return {
            'total_attempts': final_attempt,
            'successful': successful,
            'total_errors_found': total_errors,
            'final_exit_code': results[-1].exit_code if results else None,
            'iterations': [
                {
                    'iteration': r.iteration,
                    'success': r.success,
                    'errors_count': len(r.errors),
                    'errors': [
                        {'type': e.type, 'message': e.message}
                        for e in r.errors
                    ]
                }
                for r in results
            ]
        }
