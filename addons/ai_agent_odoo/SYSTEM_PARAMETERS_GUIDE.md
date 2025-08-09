# System Param### 2. Service URL (Legacy Integration)
- **Parameter Key**: `ai_agent_odoo.service_url`
- **Description**: URL for external AI service endpoint. The system will send POST requests to `{service_url}/ai/chat` with Odoo credentials and user messages.
- **Default**: `http://localhost:8001`
- **Example**: `https://your-ai-service.com` or `http://192.168.1.100:8080`

### 3. API Key (Legacy Authentication)
- **Parameter Key**: `ai_agent_odoo.api_key`
- **Description**: API key for authenticating with external legacy service. Sent as `Authorization: Bearer {api_key}` header.
- **Default**: Empty string
- **Example**: `your-service-api-key-12345`figuration Guide

This guide explains how to properly configure the OpenAI API key and other system parameters for the AI Agent Odoo chatbot.

## Required System Parameters

The AI Agent requires the following system parameters to be configured in Odoo:

### 1. OpenAI API Key (Required)
- **Parameter Key**: `ai_agent_odoo.openai_api_key`
- **Description**: Your OpenAI API key for accessing GPT models
- **Format**: Must start with `sk-` followed by the key string
- **Example**: `sk-proj-abc123...` or `sk-abc123...`

### 2. Service URL (Optional)
- **Parameter Key**: `ai_agent_odoo.service_url`
- **Description**: Service URL for external AI services (if used)
- **Default**: `http://localhost:8001`

### 3. API Key (Legacy)
- **Parameter Key**: `ai_agent_odoo.api_key`
- **Description**: Legacy API key parameter (not currently used)
- **Default**: Empty string

## How to Configure System Parameters

### Step 1: Access System Parameters
1. Log into Odoo as an administrator
2. Go to **Settings** → **Technical** → **System Parameters**
3. If you don't see the Technical menu, enable Developer Mode:
   - Go to **Settings** → **General Settings**
   - Scroll down and click **Activate the developer mode**

### Step 2: Configure OpenAI API Key
1. In System Parameters, look for the parameter `ai_agent_odoo.openai_api_key`
2. If it doesn't exist, click **Create** to add it:
   - **Key**: `ai_agent_odoo.openai_api_key`
   - **Value**: Your OpenAI API key (starts with `sk-`)
3. If it exists but is empty, click on it and set the **Value** field

### Step 3: Verify Configuration
1. Ensure the API key starts with `sk-`
2. Verify there are no extra spaces or characters
3. Save the parameter

## API Key Validation

The system automatically validates the API key format:

### ✅ Valid API Key Format
- Starts with `sk-`
- Contains alphanumeric characters and hyphens
- Minimum length of 20 characters
- Example: `sk-proj-abc123def456ghi789jkl012mno345pqr678stu901vwx234yz`

### ❌ Invalid API Key Formats
- Empty or null value
- Doesn't start with `sk-`
- Too short (less than 20 characters)
- Contains invalid characters

## Testing Your Configuration

### Method 1: Use the Diagnostic Script
Run the diagnostic script to test your configuration:
```bash
cd /path/to/odoo/addons/ai_agent_odoo
python3 diagnostic_test.py YOUR_API_KEY
```

### Method 2: Use the Test Connection Endpoint
1. Open your browser's developer tools
2. Go to your Odoo instance
3. Execute in the browser console:
```javascript
// Test the connection endpoint
fetch('/ai_agent_odoo/test_connection', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({})
}).then(response => response.json())
  .then(data => console.log('Test result:', data));
```

### Method 3: Check Odoo Logs
1. Enable debug mode in Odoo
2. Try using the chatbot
3. Check the Odoo server logs for connection errors

## Common Issues and Solutions

### Issue 1: "API key not configured"
**Solution**: Set the `ai_agent_odoo.openai_api_key` parameter in System Parameters

### Issue 2: "Invalid API key format"
**Solution**: Ensure the API key starts with `sk-` and is complete

### Issue 3: "Authentication failed"
**Solutions**:
- Verify the API key is correct and active
- Check your OpenAI account status and billing
- Ensure the API key has access to the required models

### Issue 4: "Model access denied"
**Solutions**:
- Verify your OpenAI account has access to `gpt-4o-mini` model
- Check if your API key has the necessary permissions
- Ensure your account has sufficient credits

### Issue 5: "Connection timeout"
**Solutions**:
- Check your network connectivity
- Verify firewall settings allow access to `api.openai.com`
- Try using a different network or VPN

## Security Best Practices

1. **Protect Your API Key**:
   - Never share your API key publicly
   - Don't commit API keys to version control
   - Use environment variables in production

2. **Monitor Usage**:
   - Regularly check your OpenAI usage dashboard
   - Set up billing alerts
   - Monitor for unexpected usage patterns

3. **Access Control**:
   - Limit access to System Parameters to administrators only
   - Use Odoo's user permissions to control chatbot access

## Troubleshooting Checklist

- [ ] API key is set in `ai_agent_odoo.openai_api_key`
- [ ] API key starts with `sk-`
- [ ] API key is complete (no truncation)
- [ ] OpenAI account is active and has credits
- [ ] Network connectivity to `api.openai.com` works
- [ ] Odoo user has appropriate permissions
- [ ] AI Agent is active in configuration
- [ ] Required Odoo modules are installed

## Getting Help

If you continue to experience issues:

1. Run the diagnostic script for detailed analysis
2. Check Odoo server logs for specific error messages
3. Verify your OpenAI account status and billing
4. Test the API key with OpenAI's official tools
5. Contact your system administrator for network/firewall issues

## System Parameter Auto-Initialization

The system automatically creates the required parameters with default values when the AI Agent is first accessed. However, you still need to set the actual OpenAI API key value manually.

The auto-initialization happens in the `_ensure_system_parameters()` method of the `ai.agent` model, which creates:
- `ai_agent_odoo.openai_api_key` (empty by default)
- `ai_agent_odoo.service_url` (http://localhost:8001)
- `ai_agent_odoo.api_key` (empty, legacy parameter)
