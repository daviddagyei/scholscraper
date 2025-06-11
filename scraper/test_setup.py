#!/usr/bin/env python3
"""
Test script for validating scholarship scraper setup.
"""

import sys
import subprocess
import importlib
import os
from pathlib import Path


def test_python_version():
    """Test Python version compatibility."""
    print("🐍 Testing Python version...")
    version = sys.version_info
    if version >= (3, 8):
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible")
        return True
    else:
        print(f"❌ Python {version.major}.{version.minor}.{version.micro} is too old. Need 3.8+")
        return False


def test_scrapy_installation():
    """Test if Scrapy is properly installed."""
    print("\n🕷️ Testing Scrapy installation...")
    try:
        import scrapy
        print(f"✅ Scrapy {scrapy.__version__} is installed")
        return True
    except ImportError:
        print("❌ Scrapy is not installed")
        return False


def test_required_packages():
    """Test if all required packages are installed."""
    print("\n📦 Testing required packages...")
    
    required_packages = [
        'itemloaders',
        'w3lib',
        'requests',
        'beautifulsoup4',
        'lxml',
        'dateutil',
        'schedule'
    ]
    
    all_installed = True
    for package in required_packages:
        try:
            if package == 'dateutil':
                importlib.import_module('dateutil')
            else:
                importlib.import_module(package.replace('-', '_'))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - not installed")
            all_installed = False
    
    return all_installed


def test_scrapy_project():
    """Test if Scrapy can detect the project."""
    print("\n🔧 Testing Scrapy project setup...")
    
    # Check if scrapy.cfg exists
    if not Path('scrapy.cfg').exists():
        print("❌ scrapy.cfg not found")
        return False
    
    try:
        result = subprocess.run(
            ['python', '-m', 'scrapy', 'list'],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            spiders = result.stdout.strip().split('\n')
            spiders = [s.strip() for s in spiders if s.strip()]
            print(f"✅ Found {len(spiders)} spiders:")
            for spider in spiders:
                print(f"   - {spider}")
            return True
        else:
            print(f"❌ Scrapy list failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Scrapy list command timed out")
        return False
    except Exception as e:
        print(f"❌ Error running scrapy list: {e}")
        return False


def test_spider_syntax():
    """Test if spider files have valid syntax."""
    print("\n📄 Testing spider syntax...")
    
    spider_files = [
        'spiders/base.py',
        'spiders/collegescholarships.py',
        'spiders/uncf.py',
        'spiders/hsf.py',
        'spiders/apia.py',
        'spiders/native_american.py'
    ]
    
    all_valid = True
    for spider_file in spider_files:
        if Path(spider_file).exists():
            try:
                with open(spider_file, 'r') as f:
                    compile(f.read(), spider_file, 'exec')
                print(f"✅ {spider_file}")
            except SyntaxError as e:
                print(f"❌ {spider_file} - Syntax error: {e}")
                all_valid = False
        else:
            print(f"❌ {spider_file} - File not found")
            all_valid = False
    
    return all_valid


def test_pipeline_syntax():
    """Test if pipeline files have valid syntax."""
    print("\n🔧 Testing pipeline syntax...")
    
    pipeline_files = [
        'pipelines/pipelines.py',
        'middlewares/middlewares.py',
        'items.py',
        'settings.py'
    ]
    
    all_valid = True
    for pipeline_file in pipeline_files:
        if Path(pipeline_file).exists():
            try:
                with open(pipeline_file, 'r') as f:
                    compile(f.read(), pipeline_file, 'exec')
                print(f"✅ {pipeline_file}")
            except SyntaxError as e:
                print(f"❌ {pipeline_file} - Syntax error: {e}")
                all_valid = False
        else:
            print(f"❌ {pipeline_file} - File not found")
            all_valid = False
    
    return all_valid


def test_directory_structure():
    """Test if all required directories exist."""
    print("\n📁 Testing directory structure...")
    
    required_dirs = [
        'spiders',
        'pipelines',
        'middlewares',
        'output'
    ]
    
    all_exist = True
    for directory in required_dirs:
        if Path(directory).exists():
            print(f"✅ {directory}/")
        else:
            print(f"❌ {directory}/ - Directory not found")
            all_exist = False
    
    return all_exist


def test_environment_setup():
    """Test environment configuration."""
    print("\n⚙️ Testing environment setup...")
    
    if Path('.env').exists():
        print("✅ .env file found")
        env_ok = True
    else:
        if Path('.env.example').exists():
            print("⚠️ .env file not found, but .env.example exists")
            print("   Run: cp .env.example .env")
            env_ok = False
        else:
            print("❌ No environment file found")
            env_ok = False
    
    return env_ok


def run_basic_spider_test():
    """Run a basic spider test."""
    print("\n🧪 Running basic spider test...")
    
    try:
        result = subprocess.run(
            ['python', '-m', 'scrapy', 'check'],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        if result.returncode == 0:
            print("✅ All spiders passed basic validation")
            return True
        else:
            print(f"❌ Spider validation failed: {result.stderr}")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Spider check timed out")
        return False
    except Exception as e:
        print(f"❌ Error running spider check: {e}")
        return False


def main():
    """Run all tests."""
    print("🎓 Scholarship Scraper Setup Validation")
    print("=" * 40)
    
    tests = [
        ("Python Version", test_python_version),
        ("Scrapy Installation", test_scrapy_installation),
        ("Required Packages", test_required_packages),
        ("Directory Structure", test_directory_structure),
        ("Scrapy Project", test_scrapy_project),
        ("Spider Syntax", test_spider_syntax),
        ("Pipeline Syntax", test_pipeline_syntax),
        ("Environment Setup", test_environment_setup),
        ("Basic Spider Test", run_basic_spider_test),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} - Unexpected error: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 Test Summary")
    print("=" * 40)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your scraper setup is ready.")
        print("\nNext steps:")
        print("1. Configure .env file with your credentials")
        print("2. Test a spider: python -m scrapy crawl collegescholarships")
        print("3. Run all spiders: python scheduler.py run")
    else:
        print(f"\n⚠️ {total - passed} tests failed. Please fix the issues above.")
        
    return passed == total


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
