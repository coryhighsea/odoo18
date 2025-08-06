#!/usr/bin/env python3
"""
Simple test script to check OpenAI connection from within Odoo container.
Run this inside the Odoo container to test the connection.
"""

import os
import sys

# Add Odoo to Python path (adjust if needed)
sys.path.append('/usr/lib/python3/dist-packages/odoo')

def test_openai_connection():
    try:
        # Test OpenAI library
        from openai import OpenAI
        print("✓ OpenAI library is installed")
        
        # Test API key (you'll need to set this)
        api_key = "sk-your-openai-api-key-here"  # Replace with your actual key
        if not api_key or api_key == "sk-your-openai-api-key-here":
            print("✗ Please set your OpenAI API key in this script")
            return
            
        # Test connection
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": "Hello, respond with just 'Connection successful'"}],
            max_tokens=10,
            temperature=0
        )
        
        print("✓ OpenAI connection successful!")
        print(f"Response: {response.choices[0].message.content}")
        
    except ImportError as e:
        print(f"✗ OpenAI library not installed: {e}")
        print("Run: pip install openai")
    except Exception as e:
        print(f"✗ Connection failed: {e}")

if __name__ == "__main__":
    test_openai_connection()
