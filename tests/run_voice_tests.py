#!/usr/bin/env python3
"""
Voice Test Runner - Run all voice model tests
"""

import sys
import os
import subprocess
import webbrowser
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

def print_banner(text):
    """Print a formatted banner"""
    print("\n" + "="*80)
    print(f"  {text}")
    print("="*80 + "\n")

def run_pytest_tests():
    """Run pytest tests"""
    print_banner("Running Automated Tests (pytest)")
    
    test_file = Path(__file__).parent / "test_voice_all_languages.py"
    
    if not test_file.exists():
        print(f"❌ Test file not found: {test_file}")
        return False
    
    try:
        result = subprocess.run(
            ["pytest", str(test_file), "-v", "--tb=short"],
            capture_output=False,
            text=True
        )
        return result.returncode == 0
    except FileNotFoundError:
        print("❌ pytest not found. Install with: pip install pytest pytest-asyncio")
        return False

def run_configuration_check():
    """Run configuration check"""
    print_banner("Voice Configuration Check")
    
    test_file = Path(__file__).parent / "test_voice_all_languages.py"
    
    try:
        result = subprocess.run(
            ["python", str(test_file)],
            capture_output=False,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Configuration check failed: {e}")
        return False

def run_manual_tests():
    """Run manual tests with actual OpenAI API"""
    print_banner("Running Manual Tests (OpenAI API)")
    
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key:
        print("⚠️  OPENAI_API_KEY not set")
        print("   Set it to run manual tests with actual OpenAI API")
        print("   Example: export OPENAI_API_KEY='your-key-here'")
        return False
    
    test_file = Path(__file__).parent / "test_voice_all_languages.py"
    
    try:
        result = subprocess.run(
            ["python", str(test_file), "--manual"],
            capture_output=False,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Manual tests failed: {e}")
        return False

def open_browser_test():
    """Open browser test page"""
    print_banner("Opening Browser Test Page")
    
    test_file = Path(__file__).parent / "test_voice_browser.html"
    
    if not test_file.exists():
        print(f"❌ Browser test file not found: {test_file}")
        return False
    
    try:
        # Open in default browser
        webbrowser.open(f"file://{test_file.absolute()}")
        print("✅ Browser test page opened")
        print(f"   Location: {test_file.absolute()}")
        print("\n📋 Instructions:")
        print("   1. Click 'Test All Languages' to test all at once")
        print("   2. Or click individual language buttons to test one by one")
        print("   3. For STT (Speech Recognition), speak when prompted")
        print("   4. For TTS (Text-to-Speech), listen to the audio")
        return True
    except Exception as e:
        print(f"❌ Failed to open browser: {e}")
        print(f"   Manually open: {test_file.absolute()}")
        return False

def main():
    """Main test runner"""
    print("\n" + "🎤"*40)
    print("  VOICE MODEL TEST SUITE - ALL LANGUAGES")
    print("🎤"*40 + "\n")
    
    print("This test suite will verify voice models for:")
    print("  • English (en)")
    print("  • Hindi (hi)")
    print("  • French (fr)")
    print("  • Spanish (es)")
    print("  • Punjabi (pa) ⭐")
    print("  • Chinese (zh)")
    print()
    
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        
        if mode == "pytest":
            run_pytest_tests()
        elif mode == "config":
            run_configuration_check()
        elif mode == "manual":
            run_manual_tests()
        elif mode == "browser":
            open_browser_test()
        else:
            print(f"❌ Unknown mode: {mode}")
            print_usage()
    else:
        # Run all tests
        print("Running all tests...\n")
        
        # 1. Configuration check
        config_ok = run_configuration_check()
        
        # 2. Automated tests
        if config_ok:
            pytest_ok = run_pytest_tests()
        
        # 3. Browser test
        print_banner("Browser Test")
        print("Opening browser test for manual verification...")
        open_browser_test()
        
        # Summary
        print_banner("Test Summary")
        print("✅ Configuration check: PASSED" if config_ok else "❌ Configuration check: FAILED")
        print("\n📝 Next Steps:")
        print("   1. Use the browser test to verify voice in real-time")
        print("   2. Test Punjabi specifically (reported issue)")
        print("   3. Run manual tests with OpenAI API if needed:")
        print("      python run_voice_tests.py manual")

def print_usage():
    """Print usage instructions"""
    print("\nUsage:")
    print("  python run_voice_tests.py [mode]")
    print("\nModes:")
    print("  (none)   - Run all tests")
    print("  config   - Check voice configuration only")
    print("  pytest   - Run automated pytest tests")
    print("  manual   - Run manual tests with OpenAI API")
    print("  browser  - Open browser test page only")
    print("\nExamples:")
    print("  python run_voice_tests.py")
    print("  python run_voice_tests.py browser")
    print("  python run_voice_tests.py manual")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
