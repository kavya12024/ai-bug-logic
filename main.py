"""
AI Bug Fixer - System Verification Script
Check if all dependencies and components are properly installed
"""
import sys
import subprocess
from pathlib import Path

def check_python_version():
    """Check if Python version is adequate"""
    version = sys.version_info
    if version.major >= 3 and version.minor >= 9:
        print(f"✅ Python Version: {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        print(f"❌ Python Version: {version.major}.{version.minor} (need >= 3.9)")
        return False

def check_module(module_name):
    """Check if a Python module is installed"""
    try:
        __import__(module_name)
        print(f"✅ {module_name}")
        return True
    except ImportError:
        print(f"❌ {module_name} - NOT INSTALLED")
        return False

def check_docker():
    """Check if Docker is installed and running"""
    try:
        result = subprocess.run(['docker', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Docker: {result.stdout.strip()}")
            
            # Try to connect to Docker daemon
            try:
                subprocess.run(['docker', 'ps'], capture_output=True, timeout=5)
                print("✅ Docker daemon is running")
                return True
            except:
                print("❌ Docker daemon is NOT running - start Docker Desktop")
                return False
        else:
            print("❌ Docker - NOT INSTALLED")
            return False
    except FileNotFoundError:
        print("❌ Docker - NOT INSTALLED or NOT in PATH")
        return False

def check_docker_images():
    """Check if required Docker images are available"""
    images = ['python:3.11-slim', 'node:18-alpine', 'gcc:latest']
    found = 0
    
    try:
        for image in images:
            result = subprocess.run(
                ['docker', 'image', 'inspect', image],
                capture_output=True,
                timeout=5
            )
            if result.returncode == 0:
                print(f"  ✅ {image}")
                found += 1
            else:
                print(f"  ⚠️ {image} - can be pulled automatically when needed")
    except:
        print("  ⚠️ Could not check Docker images")
    
    return found > 0

def check_ollama():
    """Check if Ollama is installed"""
    try:
        result = subprocess.run(['ollama', 'list'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Ollama is installed")
            
            # Check for CodeLlama model
            if 'codellama' in result.stdout:
                print("✅ CodeLlama model found")
                return True
            else:
                print("⚠️  CodeLlama model NOT found")
                print("   Run: ollama pull codellama:7b")
                return False
        else:
            print("❌ Ollama - NOT RUNNING or NOT IN PATH")
            return False
    except FileNotFoundError:
        print("⚠️  Ollama - NOT INSTALLED (optional)")
        print("   To enable AI fixing, download from: https://ollama.ai")
        return False

def check_project_files():
    """Check if project files exist"""
    files = {
        'backend/requirements.txt': 'Dependencies file',
        'test/test_samples/broken_python.py': 'Python test sample',
        'test/test_samples/broken_js.js': 'JavaScript test sample',
        'test/test_samples/broken_cpp.cpp': 'C++ test sample',
        'backend/app.py': 'Flask app',
        'backend/loop_executor.py': 'Main executor',
    }
    
    all_found = True
    for file_path, description in files.items():
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - NOT FOUND")
            all_found = False
    
    return all_found

def check_git():
    """Check if Git is available"""
    try:
        result = subprocess.run(['git', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Git: {result.stdout.strip()}")
            return True
        else:
            print("❌ Git - NOT WORKING")
            return False
    except FileNotFoundError:
        print("⚠️  Git - NOT INSTALLED (optional)")
        return False

def main():
    print("\n" + "="*70)
    print("AI BUG FIXER - SYSTEM VERIFICATION")
    print("="*70 + "\n")
    
    checks = {
        "Python Version": check_python_version(),
        "Project Files": check_project_files(),
        "Git": check_git(),
    }
    
    print("\n" + "-"*70)
    print("Python Modules")
    print("-"*70)
    modules = {
        'flask': check_module('flask'),
        'docker': check_module('docker'),
        'git': check_module('git'),
        'dotenv': check_module('dotenv'),
    }
    checks.update(modules)
    
    print("\n" + "-"*70)
    print("Docker")
    print("-"*70)
    checks["Docker Installation"] = check_docker()
    checks["Docker Images"] = check_docker_images()
    
    print("\n" + "-"*70)
    print("AI Integration (Optional)")
    print("-"*70)
    checks["Ollama"] = check_ollama()
    
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    
    passed = sum(1 for v in checks.values() if v)
    total = len(checks)
    
    print(f"\nChecks Passed: {passed}/{total}\n")
    
    # Recommendations
    print("📋 RECOMMENDATIONS:")
    print("-"*70)
    
    if not checks.get("Python Version"):
        print("❌ Install Python 3.9 or higher")
    
    if not checks.get("Project Files"):
        print("❌ Check project files are in correct location")
    
    if not check_module('flask'):
        print("❌ Run: pip install -r backend/requirements.txt")
    
    if not checks.get("Docker Installation"):
        print("⚠️  Docker not available - comprehensive tests will fail")
        print("   Download from: https://www.docker.com/products/docker-desktop")
    
    if not checks.get("Ollama"):
        print("ℹ️  Ollama optional - system will work with rule-based fixes only")
        print("   To enable AI fixing: https://ollama.ai")
    
    print("\n" + "="*70)
    
    # Ready to run?
    if passed >= 4:  # Minimum viable setup
        print("✅ System is ready to run!")
        print("\nNext Steps:")
        print("python run_tests.py   # Test python language")
        print("python fix_files_ollama.py   # Test all languages")
        print("="*70 + "\n")
        return 0
    else:
        print("❌ System needs setup before running tests")
        print("="*70 + "\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
