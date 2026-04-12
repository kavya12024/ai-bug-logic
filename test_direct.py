"""
Simple test script to test the AI Bug Fixer system directly
No API calls needed - just direct Python execution
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from loop_executor import LoopExecutor
from utils.logger import setup_logger

logger = setup_logger(__name__)

def main():
    """Test the fix loop with a broken Python file"""
    
    print("\n" + "="*70)
    print("AI BUG FIXER - DIRECT TEST")
    print("="*70 + "\n")
    
    # Initialize executor
    executor = LoopExecutor(use_ollama=False)
    
    # Test file
    test_file = Path("test/test_samples/broken_python.py")
    
    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        return
    
    print(f"📄 Testing file: {test_file}")
    print(f"📝 Original content:")
    print("-" * 70)
    with open(test_file, 'r') as f:
        print(f.read())
    print("-" * 70 + "\n")
    
    # Run fix loop
    print("🔧 Starting fix loop...\n")
    results = executor.execute_fix_loop(
        file_path=test_file,
        language='python',
        max_attempts=5,
        timeout=30
    )
    
    # Display summary
    summary = executor.get_summary(results)
    
    print("\n" + "="*70)
    print("RESULTS SUMMARY")
    print("="*70)
    print(f"✓ Total Attempts: {summary['total_attempts']}")
    print(f"✓ Success: {summary['successful']}")
    print(f"✓ Total Errors Found: {summary['total_errors_found']}")
    print(f"✓ Final Exit Code: {summary['final_exit_code']}")
    
    print("\nDetailed Iterations:")
    for iter_info in summary['iterations']:
        status = "✅ PASS" if iter_info['success'] else "❌ FAIL"
        print(f"\n  Attempt {iter_info['iteration']}: {status}")
        print(f"    Errors: {iter_info['errors_count']}")
        for error in iter_info['errors']:
            print(f"      - {error['type']}: {error['message']}")
    
    print("\n" + "="*70)
    print("FINAL FIXED CODE")
    print("="*70)
    with open(test_file, 'r') as f:
        print(f.read())
    print("="*70 + "\n")
    
    if summary['successful']:
        print("✅ SUCCESS! Code has been fixed and runs without errors!\n")
    else:
        print("⚠️  Could not fully fix all errors. Check details above.\n")

if __name__ == '__main__':
    main()
