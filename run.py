"""
Fix and update broken test files using Ollama only
No Docker dependency
"""
import sys
import ast
import subprocess
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from ai_fixer import AIFixer
from error_parser import Error, ErrorParser
from utils.logger import setup_logger
from config import Config
from git_pr_handler import GitPRHandler

logger = setup_logger(__name__)

def detect_python_errors(code: str) -> list:
    """Detect actual Python syntax and logic errors"""
    errors = []
    try:
        ast.parse(code)
    except SyntaxError as e:
        errors.append(Error(
            type='syntax',
            message=f"SyntaxError: {e.msg}",
            line_number=e.lineno
        ))
    except Exception as e:
        errors.append(Error(
            type='syntax',
            message=f"Error: {str(e)}"
        ))
    
    # Check for common runtime issues
    if "Ture" in code:
        errors.append(Error(
            type='typo',
            message="'Ture' should be 'True'"
        ))
    
    # Check for logic errors
    if "except:" in code or "except Exception:" in code:
        errors.append(Error(
            type='logic',
            message="Bare or overly broad exception handling - may hide errors"
        ))
    
    if "return" in code and code.count("return") > 1:
        # Check for paths that don't return
        if "else:" in code and code.count("if") > code.count("else"):
            errors.append(Error(
                type='logic',
                message="Not all code paths may return a value"
            ))
    
    # Check for resource management issues
    if "open(" in code and "with" not in code:
        errors.append(Error(
            type='resource',
            message="File opened without 'with' statement - may leak resources"
        ))
    
    if ".close()" in code and "finally:" not in code and "with" not in code:
        errors.append(Error(
            type='resource',
            message="Resource may not be properly closed in all paths"
        ))
    
    # Check for undefined variable issues
    lines = code.split('\n')
    if any('result[' in line for line in lines) and not any('result = ' in line for line in lines):
        errors.append(Error(
            type='logic',
            message="Variable 'result' may not be initialized before use"
        ))
    
    return errors if errors else [Error(type='info', message='No syntax errors detected')]

def detect_cpp_errors(code: str) -> list:
    """Detect C++ syntax errors"""
    # Write to temp file and try to compile
    errors = []
    temp_file = Path('temp_check.cpp')
    try:
        temp_file.write_text(code)
        result = subprocess.run(
            ['g++', '-fsyntax-only', str(temp_file)],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode != 0:
            for line in result.stderr.split('\n'):
                if 'error:' in line:
                    errors.append(Error(type='syntax', message=line.strip()))
    except Exception as e:
        errors.append(Error(type='syntax', message=f"Compilation check failed: {str(e)}"))
    finally:
        temp_file.unlink(missing_ok=True)
    
    return errors if errors else [Error(type='info', message='No syntax errors detected')]

def detect_java_errors(code: str) -> list:
    """Detect Java syntax errors"""
    errors = []
    
    # Check for common Java errors
    if 'null' in code and 'NullPointerException' not in code:
        errors.append(Error(
            type='potential_issue',
            message='Potential null pointer dereference'
        ))
    
    if 'Resource' in code and 'close()' not in code:
        errors.append(Error(
            type='resource',
            message='Resource may not be properly closed'
        ))
    
    return errors if errors else [Error(type='info', message='No syntax errors detected')]

def get_detected_errors(code: str, language: str) -> list:
    """Get actual detected errors based on language"""
    if language.lower() == 'python':
        return detect_python_errors(code)
    elif language.lower() in ['cpp', 'c++']:
        return detect_cpp_errors(code)
    elif language.lower() == 'java':
        return detect_java_errors(code)
    else:
        return [Error(type='info', message='No errors detected')]


def fix_and_save_file(file_path, language, use_ollama=True, ask_confirmation=True, git_handler=None, verbose=True, push=False):
    """Fix a broken file and save the correction with user confirmation"""
    
    with open(file_path, 'r') as f:
        original_code = f.read()
    
    if verbose:
        print(f"\n[*] ORIGINAL CODE:")
        print("-" * 70)
        print(original_code[:400] + ("..." if len(original_code) > 400 else ""))
        print("-" * 70 + "\n")
    
    # Detect actual errors instead of hardcoding them
    errors = get_detected_errors(original_code, language)
    
    # Check if there are actual errors (skip 'info' type errors)
    has_real_errors = any(e.type != 'info' for e in errors)
    
    if verbose:
        print("[!] ERRORS FOUND:")
        print("-" * 70)
        for i, error in enumerate(errors, 1):
            print(f"{i}. [{error.type.upper()}] {error.message}")
        print("-" * 70 + "\n")
    
    # Skip Ollama if no real errors detected
    if not has_real_errors:
        if verbose:
            print("[-] No real errors detected - skipping Ollama processing\n")
        return False
    
    # Fix with Ollama
    if verbose:
        print("[+] Fixing with Ollama CodeLlama...\n")
    
    fixer = AIFixer(use_ollama=use_ollama, ollama_model=Config.OLLAMA_MODEL)
    fixed_code = fixer.fix_code(original_code, errors, language=language)
    
    if verbose:
        print(f"[OK] FIXED CODE:")
        print("-" * 70)
        print(fixed_code[:400] + ("..." if len(fixed_code) > 400 else ""))
        print("-" * 70 + "\n")
    
    # Check if there are actual changes
    has_changes = fixed_code != original_code
    
    # Ask for confirmation if enabled
    if ask_confirmation:
        print("[?] UPDATE CONFIRMATION:")
        print(f"    File: {file_path}")
        print(f"    Errors Fixed: {len(errors)}")
        print(f"    Changes Made: {'YES' if has_changes else 'NO'}")
        
        while True:
            choice = input("\n    Do you want to update this file? (yes/no/review): ").strip().lower()
            
            if choice == 'yes':
                print("[+] Updating file with fixes...")
                break
            elif choice == 'no':
                print("[-] Skipping file update.")
                return False
            elif choice == 'review':
                print("\n[*] DETAILED CHANGES:")
                print("-" * 70)
                print(f"Original length: {len(original_code)} bytes")
                print(f"Fixed length: {len(fixed_code)} bytes")
                print(f"Errors addressed: {len(errors)}")
                print(f"Changes detected: {has_changes}")
                print("-" * 70 + "\n")
                continue
            else:
                print("[-] Invalid choice. Please enter 'yes', 'no', or 'review'.")
    
    # Skip git operations if no changes were made
    branch_name = None
    if not has_changes:
        print("[-] No changes detected - skipping git operations")
        return False
    
    # Create git branch if git handler available and there are changes
    if git_handler:
        branch_name = git_handler.create_fix_branch(language, str(file_path))
        if branch_name:
            print(f"[*] Created git branch: {branch_name}\n")
    
    # Save to file
    with open(file_path, 'w') as f:
        f.write(fixed_code)
    
    # Commit if git handler available and branch was created
    if git_handler and branch_name:
        success = git_handler.stage_and_commit(file_path, errors, branch_name)
        if success:
            print(f"[✓] Committed changes to git\n")
            pr_info = git_handler.create_pr_info(file_path, errors, fixed_code, original_code)
            print("[+] PR INFORMATION:")
            print("-" * 70)
            print(f"File: {pr_info['file']}")
            print(f"Errors Fixed: {pr_info['errors_found']}")
            for err in pr_info['errors']:
                print(f"  - {err['type']}: {err['message']}")
            print("-" * 70 + "\n")
            
            if push:
                print(f"[*] Pushing to GitHub and preparing Pull Request for branch {branch_name}...")
                if git_handler.push_branch(branch_name):
                    pr_url = git_handler.create_github_pull_request(branch_name, str(file_path), errors)
                    if pr_url:
                        print(f"[✓] GitHub PR Created: {pr_url}\n")
                    else:
                        print("[!] GitHub PR creation failed. Validate GITHUB_TOKEN and repo permissions.\n")
                else:
                    print(f"[-] Branch push failed.\n")
        else:
            print("[!] Warning: Git commit failed, but file was updated")
    
    return has_changes


def main(batch_mode=False, verbose=True, push=False):
    """Fix all broken test files
    
    Args:
        batch_mode: Skip user confirmations for faster processing
        verbose: Show detailed output for each file
        push: Push modifications to GitHub and generate PR
    """
    
    print("\n" + "="*70)
    print("AI BUG FIXER - FIX & UPDATE BROKEN FILES")
    print("Using Ollama CodeLlama (No Docker needed)")
    if batch_mode:
        print("Mode: BATCH (auto-processing without confirmations)")
    print("="*70)
    
    # Initialize git handler
    git_handler = GitPRHandler(repo_path=Path.cwd())
    git_available = git_handler.check_git_available()
    
    if git_available:
        print("[✓] Git is available - Will create pull request branches\n")
    else:
        print("[-] Git not available - Running in offline mode\n")
        git_handler = None
    
    test_files = [
        ("test/test_samples/broken_python.py", "python"),
        ("test/test_samples/broken_python_advanced.py", "python"),
        ("test/test_samples/broken_python_async.py", "python"),
        ("test/test_samples/broken_c_advanced.c", "cpp"),
        ("test/test_samples/broken_cpp.cpp", "cpp"),
        ("test/test_samples/broken_cpp_advanced.cpp", "cpp"),
        ("test/test_samples/broken_cpp_modern.cpp", "cpp"),
        ("test/test_samples/broken_java_advanced.java", "java"),
    ]
    
    results = {}
    processed = 0
    fixed = 0
    
    for file_path_str, language in test_files:
        file_path = Path(file_path_str)
        
        print(f"\n{'='*70}")
        print(f"FIXING: {language.upper()} - {file_path_str}")
        print(f"{'='*70}")
        
        if not file_path.exists():
            print(f"[-] File not found: {file_path}")
            results[language] = False
            continue
        
        try:
            success = fix_and_save_file(
                file_path, 
                language, 
                use_ollama=True,
                ask_confirmation=not batch_mode,  # Skip confirmation in batch mode
                git_handler=git_handler,
                verbose=verbose,
                push=push
            )
            results[language] = success
            processed += 1
            
            if success:
                fixed += 1
                if verbose:
                    print(f"[✓] SUCCESS! {language.upper()} file has been FIXED and UPDATED!\n")
            else:
                if verbose:
                    print(f"[!] {language.upper()} file was skipped or no changes made.\n")
                
        except Exception as e:
            print(f"[-] Error: {e}\n")
            import traceback
            traceback.print_exc()
            results[language] = False
    
    # Reset to main branch if git available
    if git_handler and git_available:
        git_handler.reset_to_main()
    
    # Final summary
    print("\n" + "="*70)
    print("FINAL SUMMARY - ALL BROKEN FILES")
    print("="*70)
    print(f"Python:            {'[OK] FIXED & UPDATED' if results.get('python') else '[-] NOT FIXED'}")
    print(f"Python Advanced:   {'[OK] FIXED & UPDATED' if results.get('python') else '[-] NOT FIXED'}")
    print(f"C++:               {'[OK] FIXED & UPDATED' if results.get('cpp') else '[-] NOT FIXED'}")
    print(f"C++ Advanced:      {'[OK] FIXED & UPDATED' if results.get('cpp') else '[-] NOT FIXED'}")
    print(f"Java Advanced:     {'[OK] FIXED & UPDATED' if results.get('java') else '[-] NOT FIXED'}")
    print("="*70 + "\n")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='AI Bug Fixer - Fix code errors with Ollama')
    parser.add_argument('--batch', action='store_true', help='Batch mode: skip confirmations for faster processing')
    parser.add_argument('--push', action='store_true', help='Push branch to GitHub and create real Pull Request')
    parser.add_argument('--quiet', action='store_true', help='Quiet mode: minimal output')
    parser.add_argument('--no-ollama', action='store_true', help='Disable Ollama fixing, use rule-based fixes only')
    args = parser.parse_args()
    
    main(batch_mode=args.batch, verbose=not args.quiet, push=args.push)
