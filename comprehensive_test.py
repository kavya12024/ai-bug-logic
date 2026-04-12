"""
Comprehensive test script for AI Bug Fixer
Tests all languages: Python, JavaScript, C++
Tests fixing with attempts
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from loop_executor import LoopExecutor
from utils.logger import setup_logger

logger = setup_logger(__name__)

def test_language(executor, test_file, language, max_attempts=5):
    """Test fixing a file in a specific language"""
    
    print("\n" + "="*70)
    print(f"TESTING: {language.upper()}")
    print("="*70 + "\n")
    
    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        return False
    
    print(f"📄 File: {test_file}")
    print(f"\n📝 Original content:\n")
    with open(test_file, 'r') as f:
        content = f.read()
        print(content[:500] + ("..." if len(content) > 500 else ""))
    
    print(f"\n🔧 Starting fix loop (max {max_attempts} attempts)...\n")
    
    try:
        results = executor.execute_fix_loop(
            file_path=test_file,
            language=language,
            max_attempts=max_attempts,
            timeout=30
        )
        
        summary = executor.get_summary(results)
        
        print("\n" + "-"*70)
        print("RESULTS:")
        print("-"*70)
        print(f"✓ Attempts: {summary['total_attempts']}")
        print(f"✓ Success: {summary['successful']}")
        print(f"✓ Total Errors Found: {summary['total_errors_found']}")
        
        for iter_info in summary['iterations']:
            status = "✅ PASS" if iter_info['success'] else "❌ FAIL"
            print(f"\n  Attempt {iter_info['iteration']}: {status}")
            print(f"    Errors: {iter_info['errors_count']}")
            for error in iter_info['errors'][:3]:  # Show first 3 errors
                print(f"      - {error['type']}: {error['message']}")
        
        print("\n" + "-"*70)
        
        if summary['successful']:
            print(f"✅ SUCCESS! {language.upper()} code has been fixed!\n")
            return True
        else:
            print(f"⚠️  Could not fully fix {language.upper()} code.\n")
            return False
            
    except Exception as e:
        print(f"❌ Error testing {language}: {e}\n")
        return False

def main():
    print("\n" + "="*70)
    print("AI BUG FIXER - COMPREHENSIVE TEST SUITE")
    print("="*70)
    
    # Initialize executor
    executor = LoopExecutor(use_ollama=False)
    
    results = {}
    
    # Test Python
    results['python'] = test_language(
        executor,
        Path("test/test_samples/broken_python.py"),
        'python'
    )
    
    # Test JavaScript
    results['javascript'] = test_language(
        executor,
        Path("test/test_samples/broken_js.js"),
        'nodejs'
    )
    
    # Test C++
    results['cpp'] = test_language(
        executor,
        Path("test/test_samples/broken_cpp.cpp"),
        'cpp'
    )
    
    # Summary
    print("\n" + "="*70)
    print("FINAL SUMMARY")
    print("="*70)
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for lang, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{lang.upper():12} {status}")
    
    print(f"\nTotal: {passed}/{total} passed")
    print("="*70 + "\n")
    
    if passed == total:
        print("🎉 All tests passed! Your AI Bug Fixer is working perfectly!\n")
    else:
        print(f"⚠️  {total - passed} test(s) failed. Check details above.\n")

if __name__ == '__main__':
    main()
