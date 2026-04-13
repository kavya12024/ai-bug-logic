"""
Fix and update broken test files using Ollama only
No Docker dependency
"""
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / 'backend'))

from ai_fixer import AIFixer
from error_parser import Error, ErrorParser
from utils.logger import setup_logger

logger = setup_logger(__name__)

def fix_and_save_file(file_path, language, use_ollama=True):
    """Fix a broken file and save the correction"""
    
    print(f"\n📝 ORIGINAL CODE:")
    print("-" * 70)
    with open(file_path, 'r') as f:
        original_code = f.read()
        print(original_code[:400] + ("..." if len(original_code) > 400 else ""))
    print("-" * 70 + "\n")
    
    # Create sample errors based on language
    if language == 'python':
        errors = [
            Error(type='syntax', message="SyntaxError: expected ':'"),
            Error(type='typo', message="'Ture' should be 'True'")
        ]
    elif language == 'javascript':
        errors = [
            Error(type='syntax', message="SyntaxError: Missing semicolon"),
        ]
    elif language == 'cpp':
        errors = [
            Error(type='syntax', message="error: expected ';'"),
        ]
    else:
        errors = []
    
    # Fix with Ollama
    print("🔧 Fixing with Ollama CodeLlama...\n")
    
    fixer = AIFixer(use_ollama=use_ollama, ollama_model="codellama:7b")
    fixed_code = fixer.fix_code(original_code, errors, language=language)
    
    # Save to file
    with open(file_path, 'w') as f:
        f.write(fixed_code)
    
    print(f"✅ UPDATED CODE:")
    print("-" * 70)
    print(fixed_code[:400] + ("..." if len(fixed_code) > 400 else ""))
    print("-" * 70 + "\n")
    
    return fixed_code != original_code

def main():
    """Fix all broken test files"""
    
    print("\n" + "="*70)
    print("AI BUG FIXER - FIX & UPDATE BROKEN FILES")
    print("Using Ollama CodeLlama (No Docker needed)")
    print("="*70)
    
    test_files = [
        ("test/test_samples/broken_python.py", "python"),
        ("test/test_samples/broken_js.js", "javascript"),
        ("test/test_samples/broken_cpp.cpp", "cpp"),
    ]
    
    results = {}
    
    for file_path_str, language in test_files:
        file_path = Path(file_path_str)
        
        print(f"\n{'='*70}")
        print(f"FIXING: {language.upper()} - {file_path_str}")
        print(f"{'='*70}")
        
        if not file_path.exists():
            print(f"❌ File not found: {file_path}")
            results[language] = False
            continue
        
        try:
            success = fix_and_save_file(file_path, language, use_ollama=True)
            results[language] = success
            
            if success:
                print(f"✅ SUCCESS! {language.upper()} file has been FIXED and UPDATED!\n")
            else:
                print(f"⚠️  {language.upper()} file could not be fixed.\n")
                
        except Exception as e:
            print(f"❌ Error: {e}\n")
            import traceback
            traceback.print_exc()
            results[language] = False
    
    # Final summary
    print("\n" + "="*70)
    print("FINAL SUMMARY - FILES UPDATED")
    print("="*70)
    print(f"Python:     {'✅ FIXED & UPDATED' if results.get('python') else '❌ FAILED'}")
    print(f"JavaScript: {'✅ FIXED & UPDATED' if results.get('javascript') else '❌ FAILED'}")
    print(f"C++:        {'✅ FIXED & UPDATED' if results.get('cpp') else '❌ FAILED'}")
    print("="*70 + "\n")

if __name__ == '__main__':
    main()
