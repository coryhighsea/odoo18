#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OpenAI Connection Test Script for AI Agent Odoo

This script tests the OpenAI API connection independently to help diagnose
connection issues with the Odoo AI Agent chatbot.

Usage:
    python3 test_openai_connection.py [API_KEY]

If no API key is provided, the script will prompt for one.
"""

import sys
import os
import json
from typing import Dict, Any

try:
    from openai import OpenAI
    import httpx
    DEPENDENCIES_AVAILABLE = True
except ImportError as e:
    print(f"❌ Missing dependencies: {e}")
    print("Please install required packages:")
    print("pip install openai>=1.99.0 httpx>=0.25.0")
    DEPENDENCIES_AVAILABLE = False


def test_openai_connection(api_key: str) -> Dict[str, Any]:
    """
    Test OpenAI API connection with the provided API key.
    
    Args:
        api_key: OpenAI API key to test
        
    Returns:
        Dictionary with test results
    """
    if not DEPENDENCIES_AVAILABLE:
        return {
            "success": False,
            "error": "Dependencies not available",
            "message": "OpenAI and httpx libraries are required"
        }
    
    if not api_key:
        return {
            "success": False,
            "error": "No API key provided",
            "message": "API key is required for testing"
        }
    
    if not api_key.startswith('sk-'):
        return {
            "success": False,
            "error": "Invalid API key format",
            "message": "OpenAI API keys should start with 'sk-'"
        }
    
    print(f"🔑 Testing API key: {api_key[:10]}...")
    
    # Test configurations to try
    configs_to_test = [
        ("basic", lambda: OpenAI(api_key=api_key)),
        ("with_timeout", lambda: OpenAI(
            api_key=api_key,
            timeout=httpx.Timeout(30.0, connect=30.0),
            max_retries=2
        )),
        ("minimal_timeout", lambda: OpenAI(
            api_key=api_key,
            timeout=10.0,
            max_retries=1
        ))
    ]
    
    for config_name, client_factory in configs_to_test:
        try:
            print(f"🧪 Testing {config_name} configuration...")
            
            client = client_factory()
            
            # Make a simple API call
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": "Say 'Connection test successful'"}],
                max_tokens=10,
                temperature=0
            )
            
            result = {
                "success": True,
                "message": f"OpenAI connection successful with {config_name} configuration",
                "response": response.choices[0].message.content.strip(),
                "model_used": "gpt-4o-mini",
                "api_key_preview": f"{api_key[:10]}...",
                "config_used": config_name
            }
            
            print(f"✅ Success with {config_name} configuration!")
            print(f"📝 Response: {result['response']}")
            return result
            
        except Exception as e:
            print(f"❌ Failed with {config_name} configuration: {e}")
            continue
    
    return {
        "success": False,
        "error": "All configurations failed",
        "message": "Could not establish connection with any configuration",
        "api_key_preview": f"{api_key[:10]}..."
    }


def main():
    """Main function to run the connection test."""
    print("🤖 OpenAI Connection Test for AI Agent Odoo")
    print("=" * 50)
    
    # Get API key from command line or prompt
    api_key = None
    if len(sys.argv) > 1:
        api_key = sys.argv[1]
    else:
        api_key = input("Enter your OpenAI API key: ").strip()
    
    if not api_key:
        print("❌ No API key provided. Exiting.")
        sys.exit(1)
    
    # Run the test
    result = test_openai_connection(api_key)
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS:")
    print("=" * 50)
    
    if result["success"]:
        print("✅ CONNECTION SUCCESSFUL!")
        print(f"Configuration used: {result.get('config_used', 'unknown')}")
        print(f"Model: {result.get('model_used', 'unknown')}")
        print(f"Response: {result.get('response', 'No response')}")
    else:
        print("❌ CONNECTION FAILED!")
        print(f"Error: {result.get('error', 'Unknown error')}")
        print(f"Message: {result.get('message', 'No message')}")
        
        # Provide troubleshooting suggestions
        print("\n🔧 TROUBLESHOOTING SUGGESTIONS:")
        print("1. Verify your API key is correct and active")
        print("2. Check your OpenAI account has sufficient credits")
        print("3. Ensure your API key has access to gpt-4o-mini model")
        print("4. Check your network connection and firewall settings")
        print("5. Try generating a new API key from OpenAI dashboard")
    
    print(f"\nAPI Key Preview: {result.get('api_key_preview', 'N/A')}")
    
    # Output JSON result for programmatic use
    print(f"\n📄 JSON Result:\n{json.dumps(result, indent=2)}")
    
    return 0 if result["success"] else 1


if __name__ == "__main__":
    sys.exit(main())
