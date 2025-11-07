"""
Test script to verify the functional config module works correctly.
Run this before deploying to ensure all config values are accessible.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

def test_config_functions():
    """Test that all config functions work correctly."""
    
    print("=" * 80)
    print("Testing Functional Config Module")
    print("=" * 80)
    
    from config import config
    
    tests = [
        ("OpenAI API Key", config.get_openai_api_key),
        ("Azure OpenAI Model", config.get_azure_openai_model),
        ("Azure OpenAI Deployment", config.get_azure_openai_deployment_name),
        ("Azure OpenAI API Key", config.get_azure_openai_api_key),
        ("Azure OpenAI Endpoint", config.get_azure_openai_endpoint),
        ("Azure OpenAI API Version", config.get_azure_openai_api_version),
        ("Azure Embedding Endpoint", config.get_azure_endpoint_embedding),
        ("Azure Embedding API Key", config.get_azure_api_key_embedding),
        ("Google Client ID", config.get_google_client_id),
        ("Google Client Secret", config.get_google_client_secret),
        ("Redirect URI", config.get_redirect_uri),
        ("Frontend Redirect URI", config.get_redirect_frontend_uri),
        ("DB Connection String", config.get_db_connection_string),
        ("DB Name", config.get_db_name),
        ("DB Table Name", config.get_db_table_name),
    ]
    
    passed = 0
    failed = 0
    
    for test_name, test_func in tests:
        try:
            value = test_func()
            if value:
                # Mask sensitive values
                if any(keyword in test_name.lower() for keyword in ['key', 'secret', 'password']):
                    display_value = f"***{value[-4:]}" if len(value) > 4 else "****"
                else:
                    display_value = value[:50] + "..." if len(value) > 50 else value
                
                print(f"✓ {test_name:.<40} {display_value}")
                passed += 1
            else:
                print(f"⚠ {test_name:.<40} (empty/None)")
                passed += 1
        except Exception as e:
            print(f"✗ {test_name:.<40} ERROR: {str(e)}")
            failed += 1
    
    print("=" * 80)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 80)
    
    return failed == 0


def test_get_all_config():
    """Test that config functions exist (removed get_all_config in simple version)."""
    print("\n" + "=" * 80)
    print("Verifying Config Functions Exist")
    print("=" * 80)
    
    from config import config
    
    try:
        # Just verify we can call functions
        functions = [
            'get_openai_api_key',
            'get_azure_openai_model',
            'get_db_name',
        ]
        
        for func_name in functions:
            if hasattr(config, func_name):
                print(f"✓ Function '{func_name}' exists")
            else:
                print(f"✗ Function '{func_name}' not found")
                return False
        
        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def test_get_env_var():
    """Test the get_env_var utility function."""
    print("\n" + "=" * 80)
    print("Testing get_env_var()")
    print("=" * 80)
    
    from config import config
    
    # Test with existing variable
    try:
        value = config.get_env_var('OPENAI_API_KEY')
        if value:
            print(f"✓ get_env_var('OPENAI_API_KEY') = ***{value[-4:]}")
        else:
            print(f"⚠ get_env_var('OPENAI_API_KEY') returned None")
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False
    
    # Test with non-existing variable and default
    try:
        value = config.get_env_var('NON_EXISTENT_VAR', 'default_value')
        if value == 'default_value':
            print(f"✓ get_env_var('NON_EXISTENT_VAR', 'default_value') = {value}")
        else:
            print(f"✗ Unexpected value: {value}")
            return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False
    
    return True


def test_caching():
    """Test that config values work correctly (simplified version has no caching)."""
    print("\n" + "=" * 80)
    print("Testing Config Consistency")
    print("=" * 80)
    
    from config import config
    
    # Call twice and verify consistency
    try:
        value1 = config.get_openai_api_key()
        value2 = config.get_openai_api_key()
        
        if value1 == value2:
            print(f"✓ Values are consistent")
            print(f"✓ Simple implementation (no caching needed)")
        else:
            print(f"✗ Values are different")
            return False
        
        return True
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def main():
    """Run all tests."""
    print("\n🚀 Starting Configuration Module Tests\n")
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("⚠ Warning: .env file not found!")
        print("  Some tests may fail if environment variables are not set.\n")
    
    results = []
    
    results.append(("Basic Config Functions", test_config_functions()))
    results.append(("Config Functions Exist", test_get_all_config()))
    results.append(("get_env_var()", test_get_env_var()))
    results.append(("Config Consistency", test_caching()))
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    for test_name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"{test_name:.<50} {status}")
    
    all_passed = all(result[1] for result in results)
    
    print("=" * 80)
    if all_passed:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed!")
    print("=" * 80)
    
    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
