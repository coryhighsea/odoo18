#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Comprehensive Diagnostic Test for AI Agent Odoo OpenAI Connection

This script performs a comprehensive diagnosis of the OpenAI connection setup
to help identify and resolve connection issues.
"""

import sys
import os
import json
import importlib.util
from typing import Dict, Any, List

def check_dependencies() -> Dict[str, Any]:
    """Check if required dependencies are installed."""
    results = {
        "openai": {"installed": False, "version": None, "error": None},
        "httpx": {"installed": False, "version": None, "error": None}
    }
    
    # Check OpenAI
    try:
        import openai
        results["openai"]["installed"] = True
        results["openai"]["version"] = openai.__version__
    except ImportError as e:
        results["openai"]["error"] = str(e)
    
    # Check httpx
    try:
        import httpx
        results["httpx"]["installed"] = True
        results["httpx"]["version"] = httpx.__version__
    except ImportError as e:
        results["httpx"]["error"] = str(e)
    
    return results

def check_network_connectivity() -> Dict[str, Any]:
    """Check network connectivity to OpenAI API."""
    import subprocess
    
    try:
        # Test basic connectivity to OpenAI API
        result = subprocess.run(
            ["curl", "-I", "https://api.openai.com", "--connect-timeout", "10"],
            capture_output=True,
            text=True,
            timeout=15
        )
        
        return {
            "success": result.returncode == 0,
            "status_code": "Available" if result.returncode == 0 else "Failed",
            "response": result.stdout[:200] if result.stdout else result.stderr[:200]
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Network connectivity test failed"
        }

def test_openai_client_creation() -> Dict[str, Any]:
    """Test OpenAI client creation with different configurations."""
    try:
        from openai import OpenAI
        import httpx
    except ImportError as e:
        return {
            "success": False,
            "error": f"Import error: {e}",
            "message": "Required libraries not available"
        }
    
    test_api_key = "sk-test-key-for-client-creation-only"
    configs_tested = []
    
    # Test basic client creation
    try:
        client = OpenAI(api_key=test_api_key)
        configs_tested.append({"name": "basic", "success": True})
    except Exception as e:
        configs_tested.append({"name": "basic", "success": False, "error": str(e)})
    
    # Test client with httpx timeout
    try:
        client = OpenAI(
            api_key=test_api_key,
            timeout=httpx.Timeout(30.0, connect=30.0),
            max_retries=2
        )
        configs_tested.append({"name": "httpx_timeout", "success": True})
    except Exception as e:
        configs_tested.append({"name": "httpx_timeout", "success": False, "error": str(e)})
    
    # Test minimal client
    try:
        client = OpenAI(api_key=test_api_key, timeout=10.0)
        configs_tested.append({"name": "minimal", "success": True})
    except Exception as e:
        configs_tested.append({"name": "minimal", "success": False, "error": str(e)})
    
    successful_configs = [c for c in configs_tested if c["success"]]
    
    return {
        "success": len(successful_configs) > 0,
        "configs_tested": configs_tested,
        "successful_configs": len(successful_configs),
        "total_configs": len(configs_tested)
    }

def validate_api_key_format(api_key: str) -> Dict[str, Any]:
    """Validate API key format."""
    if not api_key:
        return {
            "valid": False,
            "error": "API key is empty or None",
            "suggestions": ["Set the API key in Odoo System Parameters"]
        }
    
    if not isinstance(api_key, str):
        return {
            "valid": False,
            "error": f"API key should be string, got {type(api_key)}",
            "suggestions": ["Check API key configuration in Odoo"]
        }
    
    if not api_key.startswith('sk-'):
        return {
            "valid": False,
            "error": "API key should start with 'sk-'",
            "suggestions": [
                "Verify you're using the correct OpenAI API key",
                "Generate a new API key from OpenAI dashboard"
            ]
        }
    
    if len(api_key) < 20:
        return {
            "valid": False,
            "error": "API key appears too short",
            "suggestions": ["Verify the complete API key was copied"]
        }
    
    return {
        "valid": True,
        "format": "Valid OpenAI API key format",
        "preview": f"{api_key[:10]}...{api_key[-4:]}"
    }

def test_model_access(api_key: str) -> Dict[str, Any]:
    """Test access to specific OpenAI models."""
    if not api_key or not api_key.startswith('sk-'):
        return {
            "success": False,
            "error": "Invalid API key for model testing",
            "message": "Cannot test model access without valid API key"
        }
    
    try:
        from openai import OpenAI
        import httpx
        
        client = OpenAI(
            api_key=api_key,
            timeout=httpx.Timeout(30.0, connect=30.0),
            max_retries=1
        )
        
        # Test gpt-4o-mini model (used in the application)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Test"}],
            max_tokens=5,
            temperature=0
        )
        
        return {
            "success": True,
            "model": "gpt-4o-mini",
            "response": response.choices[0].message.content.strip(),
            "message": "Model access successful"
        }
        
    except Exception as e:
        error_msg = str(e).lower()
        suggestions = []
        
        if "authentication" in error_msg or "unauthorized" in error_msg:
            suggestions.extend([
                "Verify API key is correct and active",
                "Check OpenAI account status and billing"
            ])
        elif "quota" in error_msg or "billing" in error_msg:
            suggestions.extend([
                "Check OpenAI account has sufficient credits",
                "Verify billing information is up to date"
            ])
        elif "model" in error_msg:
            suggestions.extend([
                "Verify API key has access to gpt-4o-mini model",
                "Try using a different model like gpt-3.5-turbo"
            ])
        else:
            suggestions.extend([
                "Check network connectivity",
                "Verify firewall settings allow OpenAI API access"
            ])
        
        return {
            "success": False,
            "error": str(e),
            "suggestions": suggestions,
            "message": "Model access test failed"
        }

def run_comprehensive_diagnosis(api_key: str = None) -> Dict[str, Any]:
    """Run comprehensive diagnosis of OpenAI connection setup."""
    print("🔍 Running Comprehensive OpenAI Connection Diagnosis")
    print("=" * 60)
    
    results = {
        "timestamp": str(__import__('datetime').datetime.now()),
        "dependencies": None,
        "network": None,
        "client_creation": None,
        "api_key_validation": None,
        "model_access": None,
        "overall_status": "unknown"
    }
    
    # 1. Check dependencies
    print("1️⃣ Checking dependencies...")
    results["dependencies"] = check_dependencies()
    deps_ok = all(dep["installed"] for dep in results["dependencies"].values())
    print(f"   Dependencies: {'✅ OK' if deps_ok else '❌ MISSING'}")
    
    # 2. Check network connectivity
    print("2️⃣ Checking network connectivity...")
    results["network"] = check_network_connectivity()
    network_ok = results["network"]["success"]
    print(f"   Network: {'✅ OK' if network_ok else '❌ FAILED'}")
    
    # 3. Test client creation
    print("3️⃣ Testing OpenAI client creation...")
    results["client_creation"] = test_openai_client_creation()
    client_ok = results["client_creation"]["success"]
    print(f"   Client Creation: {'✅ OK' if client_ok else '❌ FAILED'}")
    
    # 4. Validate API key
    print("4️⃣ Validating API key format...")
    results["api_key_validation"] = validate_api_key_format(api_key)
    key_format_ok = results["api_key_validation"]["valid"]
    print(f"   API Key Format: {'✅ OK' if key_format_ok else '❌ INVALID'}")
    
    # 5. Test model access (only if we have a valid API key)
    if api_key and key_format_ok:
        print("5️⃣ Testing model access...")
        results["model_access"] = test_model_access(api_key)
        model_ok = results["model_access"]["success"]
        print(f"   Model Access: {'✅ OK' if model_ok else '❌ FAILED'}")
    else:
        print("5️⃣ Skipping model access test (no valid API key)")
        results["model_access"] = {
            "success": False,
            "message": "Skipped - no valid API key provided"
        }
        model_ok = False
    
    # Determine overall status
    if deps_ok and network_ok and client_ok and key_format_ok and model_ok:
        results["overall_status"] = "healthy"
    elif deps_ok and network_ok and client_ok:
        results["overall_status"] = "setup_ok_need_api_key"
    else:
        results["overall_status"] = "issues_detected"
    
    return results

def print_diagnosis_report(results: Dict[str, Any]):
    """Print a formatted diagnosis report."""
    print("\n" + "=" * 60)
    print("📊 DIAGNOSIS REPORT")
    print("=" * 60)
    
    status = results["overall_status"]
    if status == "healthy":
        print("✅ OVERALL STATUS: HEALTHY - Connection should work")
    elif status == "setup_ok_need_api_key":
        print("⚠️  OVERALL STATUS: SETUP OK - Need valid API key")
    else:
        print("❌ OVERALL STATUS: ISSUES DETECTED - Needs attention")
    
    print(f"\n🕐 Diagnosis Time: {results['timestamp']}")
    
    # Dependencies
    print(f"\n📦 DEPENDENCIES:")
    for name, info in results["dependencies"].items():
        status = "✅" if info["installed"] else "❌"
        version = f" (v{info['version']})" if info["version"] else ""
        print(f"   {status} {name}{version}")
    
    # Network
    print(f"\n🌐 NETWORK CONNECTIVITY:")
    net = results["network"]
    status = "✅" if net["success"] else "❌"
    print(f"   {status} OpenAI API reachable: {net.get('status_code', 'Unknown')}")
    
    # Client Creation
    print(f"\n🔧 CLIENT CREATION:")
    client = results["client_creation"]
    print(f"   Successful configs: {client['successful_configs']}/{client['total_configs']}")
    for config in client["configs_tested"]:
        status = "✅" if config["success"] else "❌"
        print(f"   {status} {config['name']}")
    
    # API Key
    print(f"\n🔑 API KEY VALIDATION:")
    key_val = results["api_key_validation"]
    status = "✅" if key_val["valid"] else "❌"
    print(f"   {status} Format validation")
    if key_val["valid"]:
        print(f"   Preview: {key_val.get('preview', 'N/A')}")
    
    # Model Access
    print(f"\n🤖 MODEL ACCESS:")
    model = results["model_access"]
    status = "✅" if model["success"] else "❌"
    print(f"   {status} gpt-4o-mini access")
    if model["success"]:
        print(f"   Response: {model.get('response', 'N/A')}")
    
    # Recommendations
    print(f"\n💡 RECOMMENDATIONS:")
    if status == "healthy":
        print("   🎉 Everything looks good! The connection should work.")
        print("   If you're still having issues, check Odoo logs for specific errors.")
    elif status == "setup_ok_need_api_key":
        print("   1. Set a valid OpenAI API key in Odoo System Parameters")
        print("   2. Key should be: ai_agent_odoo.openai_api_key")
        print("   3. Ensure the API key has sufficient credits and model access")
    else:
        print("   1. Install missing dependencies if any")
        print("   2. Check network connectivity and firewall settings")
        print("   3. Verify OpenAI client can be created")
        print("   4. Set valid API key in Odoo System Parameters")

def main():
    """Main function."""
    print("🤖 AI Agent Odoo - OpenAI Connection Diagnostics")
    
    # Get API key if provided
    api_key = None
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
        if api_key == "":
            api_key = None
    else:
        # Non-interactive mode - skip API key input
        print("Running in non-interactive mode - skipping API key input")
        api_key = None
    
    # Run diagnosis
    results = run_comprehensive_diagnosis(api_key)
    
    # Print report
    print_diagnosis_report(results)
    
    # Save results to file
    output_file = "openai_diagnosis_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n💾 Detailed results saved to: {output_file}")
    
    return 0 if results["overall_status"] in ["healthy", "setup_ok_need_api_key"] else 1

if __name__ == "__main__":
    sys.exit(main())

