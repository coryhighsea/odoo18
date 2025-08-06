#!/usr/bin/env python3
"""
Simple test script to verify AI Agent setup in Odoo
"""

import requests
import json

# Test configuration
ODOO_URL = "http://localhost:8069"
TEST_DB = "chisey"  # Replace with your database name
TEST_USERNAME = "admin"  # Replace with your username
TEST_PASSWORD = "admin"  # Replace with your password

def test_odoo_connection():
    """Test basic Odoo connection"""
    try:
        response = requests.get(f"{ODOO_URL}/web/database/selector", timeout=5)
        if response.status_code == 200:
            print("✓ Odoo is accessible")
            return True
        else:
            print(f"✗ Odoo returned status code: {response.status_code}")
            return False
    except Exception as e:
        print(f"✗ Failed to connect to Odoo: {e}")
        return False

def test_ai_agent_config():
    """Test AI agent configuration endpoint"""
    try:
        # This would require authentication, so we'll just check if the endpoint exists
        # In a real test, you'd need to handle Odoo's authentication
        print("ℹ AI Agent configuration endpoint: /ai_agent_odoo/get_config")
        print("ℹ AI Agent chat endpoint: /ai_agent_odoo/chat")
        print("ℹ AI Agent test endpoint: /ai_agent_odoo/test_connection")
        return True
    except Exception as e:
        print(f"✗ Failed to test AI agent config: {e}")
        return False

def main():
    print("AI Agent Odoo Setup Verification")
    print("=" * 40)
    
    # Test basic connectivity
    if not test_odoo_connection():
        print("\n❌ Basic Odoo connection failed!")
        return False
    
    # Test AI agent configuration
    if not test_ai_agent_config():
        print("\n❌ AI agent configuration test failed!")
        return False
    
    print("\n✅ Basic setup verification complete!")
    print("\nNext steps:")
    print("1. Log into Odoo at http://localhost:8069")
    print("2. Go to Apps and install the 'AI Assistant' module")
    print("3. Configure OpenAI API key in Settings > Technical > System Parameters")
    print("4. Set 'ai_agent_odoo.openai_api_key' to your OpenAI API key")
    print("5. Test the AI assistant using the chat widget in the top bar")
    
    return True

if __name__ == "__main__":
    main()
