#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
System Configuration Verification Script for AI Agent Odoo

This script helps verify that the system parameters are properly configured
for the OpenAI API connection in Odoo.

Usage:
    python3 verify_system_config.py [API_KEY]
"""

import sys
import re
from typing import Dict, Any, List

def validate_api_key_format(api_key: str) -> Dict[str, Any]:
    """
    Validate OpenAI API key format and provide detailed feedback.
    
    Args:
        api_key: The API key to validate
        
    Returns:
        Dictionary with validation results and suggestions
    """
    if not api_key:
        return {
            "valid": False,
            "error": "API key is empty or None",
            "severity": "critical",
            "suggestions": [
                "Set the API key in Odoo System Parameters",
                "Navigate to Settings > Technical > System Parameters",
                "Create parameter: ai_agent_odoo.openai_api_key"
            ]
        }
    
    if not isinstance(api_key, str):
        return {
            "valid": False,
            "error": f"API key should be string, got {type(api_key).__name__}",
            "severity": "critical",
            "suggestions": [
                "Check API key configuration in Odoo",
                "Ensure the value is entered as text, not a number"
            ]
        }
    
    # Remove any whitespace
    api_key = api_key.strip()
    
    if not api_key.startswith('sk-'):
        return {
            "valid": False,
            "error": "API key should start with 'sk-'",
            "severity": "critical",
            "suggestions": [
                "Verify you're using the correct OpenAI API key",
                "OpenAI API keys always start with 'sk-'",
                "Generate a new API key from OpenAI dashboard if needed"
            ]
        }
    
    if len(api_key) < 20:
        return {
            "valid": False,
            "error": f"API key appears too short (length: {len(api_key)})",
            "severity": "critical",
            "suggestions": [
                "Verify the complete API key was copied",
                "OpenAI API keys are typically 51+ characters long",
                "Check for truncation during copy/paste"
            ]
        }
    
    # Check for common issues
    issues = []
    warnings = []
    
    # Check for spaces or newlines
    if ' ' in api_key or '\n' in api_key or '\t' in api_key:
        issues.append("API key contains whitespace characters")
    
    # Check for valid characters (alphanumeric, hyphens, underscores)
    if not re.match(r'^sk-[A-Za-z0-9_-]+$', api_key):
        issues.append("API key contains invalid characters")
    
    # Check length (modern OpenAI keys are typically 51 characters)
    if len(api_key) < 40:
        warnings.append(f"API key seems short (length: {len(api_key)})")
    elif len(api_key) > 100:
        warnings.append(f"API key seems long (length: {len(api_key)})")
    
    if issues:
        return {
            "valid": False,
            "error": "; ".join(issues),
            "severity": "critical",
            "suggestions": [
                "Copy the API key again from OpenAI dashboard",
                "Ensure no extra characters are included",
                "Remove any spaces or line breaks"
            ]
        }
    
    result = {
        "valid": True,
        "format": "Valid OpenAI API key format",
        "length": len(api_key),
        "preview": f"{api_key[:10]}...{api_key[-4:]}",
        "severity": "success"
    }
    
    if warnings:
        result["warnings"] = warnings
    
    return result

def check_system_parameter_requirements() -> Dict[str, Any]:
    """
    Check the requirements for system parameter configuration.
    
    Returns:
        Dictionary with configuration requirements and instructions
    """
    return {
        "required_parameters": [
            {
                "key": "ai_agent_odoo.openai_api_key",
                "description": "OpenAI API key for GPT model access",
                "required": True,
                "format": "Must start with 'sk-'",
                "example": "sk-proj-abc123..."
            },
            {
                "key": "ai_agent_odoo.service_url",
                "description": "Service URL for external AI services",
                "required": False,
                "default": "http://localhost:8001",
                "example": "http://localhost:8001"
            },
            {
                "key": "ai_agent_odoo.api_key",
                "description": "Legacy API key parameter (not used)",
                "required": False,
                "default": "",
                "example": ""
            }
        ],
        "configuration_steps": [
            "1. Log into Odoo as administrator",
            "2. Go to Settings > Technical > System Parameters",
            "3. Find or create 'ai_agent_odoo.openai_api_key' parameter",
            "4. Set the value to your OpenAI API key",
            "5. Save the configuration"
        ],
        "access_requirements": [
            "Administrator access to Odoo",
            "Developer mode enabled (for Technical menu)",
            "Valid OpenAI API key with model access",
            "Sufficient OpenAI account credits"
        ]
    }

def generate_configuration_report(api_key: str = None) -> Dict[str, Any]:
    """
    Generate a comprehensive configuration report.
    
    Args:
        api_key: Optional API key to validate
        
    Returns:
        Dictionary with complete configuration analysis
    """
    report = {
        "timestamp": str(__import__('datetime').datetime.now()),
        "system_requirements": check_system_parameter_requirements(),
        "api_key_validation": None,
        "configuration_status": "unknown",
        "recommendations": []
    }
    
    # Validate API key if provided
    if api_key:
        report["api_key_validation"] = validate_api_key_format(api_key)
        
        if report["api_key_validation"]["valid"]:
            report["configuration_status"] = "ready"
            report["recommendations"] = [
                "✅ API key format is valid",
                "Configure the key in Odoo System Parameters",
                "Test the connection using the diagnostic script"
            ]
        else:
            report["configuration_status"] = "needs_attention"
            report["recommendations"] = [
                "❌ API key format issues detected",
                "Fix the API key format first",
                "Then configure in Odoo System Parameters"
            ]
    else:
        report["configuration_status"] = "needs_api_key"
        report["recommendations"] = [
            "🔑 API key needed for validation",
            "Obtain API key from OpenAI dashboard",
            "Configure in Odoo System Parameters"
        ]
    
    return report

def print_configuration_guide():
    """Print a formatted configuration guide."""
    print("🔧 ODOO SYSTEM PARAMETERS CONFIGURATION GUIDE")
    print("=" * 60)
    
    requirements = check_system_parameter_requirements()
    
    print("\n📋 REQUIRED SYSTEM PARAMETERS:")
    for param in requirements["required_parameters"]:
        required_text = "✅ REQUIRED" if param["required"] else "⚪ OPTIONAL"
        print(f"\n{required_text}: {param['key']}")
        print(f"   Description: {param['description']}")
        if param.get("format"):
            print(f"   Format: {param['format']}")
        if param.get("default"):
            print(f"   Default: {param['default']}")
        if param.get("example"):
            print(f"   Example: {param['example']}")
    
    print(f"\n📝 CONFIGURATION STEPS:")
    for step in requirements["configuration_steps"]:
        print(f"   {step}")
    
    print(f"\n🔐 ACCESS REQUIREMENTS:")
    for req in requirements["access_requirements"]:
        print(f"   • {req}")

def main():
    """Main function."""
    print("🤖 AI Agent Odoo - System Configuration Verification")
    print("=" * 60)
    
    # Get API key if provided
    api_key = None
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
        print(f"🔑 Validating provided API key...")
    else:
        print("ℹ️  No API key provided - showing configuration guide")
    
    # Generate report
    report = generate_configuration_report(api_key)
    
    # Print configuration guide
    print_configuration_guide()
    
    # Print API key validation if provided
    if api_key:
        print(f"\n🔍 API KEY VALIDATION RESULTS:")
        print("=" * 40)
        
        validation = report["api_key_validation"]
        
        if validation["valid"]:
            print("✅ API KEY FORMAT: VALID")
            print(f"   Length: {validation['length']} characters")
            print(f"   Preview: {validation['preview']}")
            
            if validation.get("warnings"):
                print("⚠️  WARNINGS:")
                for warning in validation["warnings"]:
                    print(f"   • {warning}")
        else:
            print("❌ API KEY FORMAT: INVALID")
            print(f"   Error: {validation['error']}")
            print("💡 SUGGESTIONS:")
            for suggestion in validation["suggestions"]:
                print(f"   • {suggestion}")
    
    # Print overall status
    print(f"\n📊 CONFIGURATION STATUS: {report['configuration_status'].upper()}")
    print("💡 RECOMMENDATIONS:")
    for rec in report["recommendations"]:
        print(f"   {rec}")
    
    # Print next steps
    print(f"\n🚀 NEXT STEPS:")
    if report["configuration_status"] == "ready":
        print("   1. Configure the API key in Odoo System Parameters")
        print("   2. Run the diagnostic test: python3 diagnostic_test.py YOUR_API_KEY")
        print("   3. Test the chatbot functionality in Odoo")
    elif report["configuration_status"] == "needs_attention":
        print("   1. Fix the API key format issues")
        print("   2. Re-run this script to validate")
        print("   3. Configure the corrected key in Odoo")
    else:
        print("   1. Obtain a valid OpenAI API key")
        print("   2. Run this script again with the key for validation")
        print("   3. Configure the key in Odoo System Parameters")
    
    return 0 if report["configuration_status"] in ["ready", "needs_api_key"] else 1

if __name__ == "__main__":
    sys.exit(main())
