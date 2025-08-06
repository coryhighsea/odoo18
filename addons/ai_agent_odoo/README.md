# AI Agent Odoo

An Odoo addon that integrates OpenAI's GPT with Odoo ERP system, allowing users to interact with their Odoo data through a conversational AI interface.

## Features

- **Conversational AI Interface**: Chat widget integrated into Odoo's interface
- **Sales Order Management**: Search, view, and modify sales orders
- **Product Information**: Get product details, pricing, and stock levels
- **CRM Integration**: Create and manage leads/opportunities
- **Customer Management**: View customer information
- **Stock Operations**: Monitor and update inventory levels

## Installation

### 1. Install Dependencies

First, install the required Python packages:

```bash
pip install openai>=1.0.0
```

### 2. Install the Addon

1. Copy the `ai_agent_odoo` folder to your Odoo addons directory
2. Update the addon list in Odoo
3. Install the "AI Assistant" addon

### 3. Configuration

#### OpenAI API Key

1. Go to **Settings > Technical > System Parameters**
2. Create or update the parameter `ai_agent_odoo.openai_api_key` with your OpenAI API key

#### AI Agent Configuration

1. Go to **AI Assistant > Configuration**
2. Ensure the default AI Agent is active
3. Configure the model provider (currently supports OpenAI)

## Usage

### Chat Interface

- Click the AI Assistant icon in the top navigation bar
- Type your questions or requests in natural language
- The AI can help you with:
  - "Show me sales order S00001"
  - "What's the stock level for Office Chair?"
  - "Create a new lead for John Doe"
  - "Update the quantity of keyboards in order S00002 to 5"

### Available Tools

The AI agent has access to the following Odoo operations:

- **search_sales_order_by_name**: Find and display sales order details
- **create_new_lead**: Create new CRM leads
- **get_product_info**: Get product information and stock levels
- **change_sales_order_line_quantity**: Modify quantities in sales orders
- **fetch_all_sales_orders**: List all sales orders
- **fetch_all_products**: List all products
- **fetch_all_leads**: List all CRM leads
- **fetch_all_customers**: List all customers
- **update_sales_order_state**: Change sales order status
- **update_product_price**: Modify product prices
- **update_lead_stage**: Move leads through CRM stages

## Security

- The addon uses Odoo's built-in authentication system
- OpenAI API calls are made server-side to protect API keys
- All database operations respect Odoo's access rights and security rules

## Requirements

- Odoo 18.0+
- Python 3.8+
- OpenAI Python library (>= 1.0.0)
- Valid OpenAI API key

## Dependencies

- web
- mail  
- sale
- crm
- stock
- product

## Troubleshooting

### OpenAI Connection Issues

1. Verify your OpenAI API key is correctly set in System Parameters
2. Check that the OpenAI Python library is installed
3. Ensure your server has internet access to reach OpenAI's API

### Permission Issues

1. Verify users have appropriate access rights to the modules they're trying to access
2. Check that the AI Agent is active in the configuration

### Tool Execution Errors

1. Check Odoo logs for detailed error messages
2. Ensure all required modules (sale, crm, stock, product) are installed
3. Verify data exists for the operations being performed

## Support

For issues and feature requests, please check the Odoo logs and ensure all dependencies are properly installed.
