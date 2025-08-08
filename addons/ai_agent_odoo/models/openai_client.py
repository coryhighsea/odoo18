# -*- coding: utf-8 -*-
import json
import logging
import os
import threading
import time
from typing import List, Dict, Any, Optional

try:
    from openai import OpenAI
    import httpx
except ImportError:
    OpenAI = None
    httpx = None

from odoo import api, models, fields
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class OpenAIClient(models.TransientModel):
    _name = 'ai.agent.openai.client'
    _description = 'OpenAI Client for AI Agent'

    @api.model
    def _get_openai_client(self):
        """Get OpenAI client instance."""
        if OpenAI is None:
            _logger.warning("OpenAI library not installed. Please install it with: pip install openai")
            return None
        
        api_key = self._get_openai_api_key()
        if api_key:
            if httpx is not None:
                try:
                    # Use the configuration that works in our tests
                    return OpenAI(
                        api_key=api_key,
                        timeout=httpx.Timeout(60.0, connect=60.0),
                        max_retries=3
                    )
                except Exception as e:
                    _logger.warning(f"Failed to create httpx client: {e}")
                    # Fallback to basic client
                    return OpenAI(api_key=api_key)
            else:
                # Fallback to basic client if httpx is not available
                return OpenAI(api_key=api_key)
        else:
            _logger.warning("OpenAI API key not configured")
            return None

    def _get_openai_api_key(self):
        """Get OpenAI API key from system parameters."""
        return self.env['ir.config_parameter'].sudo().get_param('ai_agent_odoo.openai_api_key')

    def _get_available_tools(self):
        """Get the list of available Odoo tools for OpenAI."""
        return [
            {
                "type": "function",
                "function": {
                    "name": "search_sales_order_by_name",
                    "description": "Get detailed information for a specific sales order, including its line items, by providing its name (e.g., 'S00004').",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "order_name": {
                                "type": "string",
                                "description": "The name or reference of the sales order, like 'S00004'."
                            }
                        },
                        "required": ["order_name"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "create_new_lead",
                    "description": "Create a new lead or opportunity in the Odoo CRM.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "name": {
                                "type": "string",
                                "description": "The title or subject of the lead."
                            },
                            "contact_name": {
                                "type": "string",
                                "description": "The name of the contact person for this lead."
                            },
                            "email": {
                                "type": "string",
                                "description": "The email address for this lead."
                            },
                            "phone": {
                                "type": "string",
                                "description": "The phone number for this lead."
                            }
                        },
                        "required": ["name"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "get_product_info",
                    "description": "Looks up a product in Odoo by its name and returns its current price and stock level.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "product_name": {
                                "type": "string",
                                "description": "The name of the product to search for, e.g., 'Office Chair' or 'Desk Lamp'."
                            }
                        },
                        "required": ["product_name"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "change_sales_order_line_quantity",
                    "description": "Change the quantity of a product in a specific sales order.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "order_name": {"type": "string", "description": "The sales order name, e.g., 'S00004'."},
                            "product_name": {"type": "string", "description": "The product name in the order."},
                            "new_qty": {"type": "number", "description": "The new quantity to set for the product in the order."}
                        },
                        "required": ["order_name", "product_name", "new_qty"],
                    },
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "fetch_all_sales_orders",
                    "description": "Fetch all sales orders with their details.",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "fetch_all_products",
                    "description": "Fetch all products with their name, price, and stock level.",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "fetch_all_leads",
                    "description": "Fetch all leads/opportunities with their details.",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                },
            },
            {
                "type": "function",
                "function": {
                    "name": "fetch_all_customers",
                    "description": "Fetch all customers/partners with their name and email.",
                    "parameters": {"type": "object", "properties": {}, "required": []},
                },
            },
        ]

    def _execute_tool(self, tool_name: str, arguments: dict) -> dict:
        """Execute a tool function with the given arguments."""
        try:
            # Get the tool executor
            tool_executor = self.env['ai.agent.tools']
            
            # Execute the tool
            if hasattr(tool_executor, tool_name):
                method = getattr(tool_executor, tool_name)
                result = method(**arguments)
                return result
            else:
                return {"error": f"Tool '{tool_name}' not found"}
                
        except Exception as e:
            _logger.error(f"Error executing tool {tool_name}: {e}")
            return {"error": str(e)}

    def chat_with_tools(self, messages: List[Dict], max_iterations: int = 5) -> Dict[str, Any]:
        """
        Chat with OpenAI using tools and return the response.
        
        Args:
            messages: List of message dictionaries
            max_iterations: Maximum number of tool call iterations
            
        Returns:
            Dictionary containing the response and any tool calls made
        """
        client = self._get_openai_client()
        if not client:
            return {
                "error": "OpenAI client not initialized. Please check your API key configuration.",
                "response": "I'm sorry, but I'm unable to connect to the AI service. Please contact your administrator."
            }

        try:
            tools = self._get_available_tools()
            tool_calls_made = []
            
            for iteration in range(max_iterations):
                # Make the API call
                response = client.chat.completions.create(
                    model="gpt-4o-mini",  # Use GPT-4o-mini for better compatibility and cost efficiency
                    messages=messages,
                    tools=tools,
                    tool_choice="auto",
                    temperature=0.1
                )
                
                message = response.choices[0].message
                
                # If no tool calls, we're done
                if not message.tool_calls:
                    return {
                        "response": message.content,
                        "tool_calls_made": tool_calls_made,
                        "success": True
                    }
                
                # Add the assistant's message to the conversation
                messages.append({
                    "role": "assistant",
                    "content": message.content,
                    "tool_calls": [
                        {
                            "id": tool_call.id,
                            "type": "function",
                            "function": {
                                "name": tool_call.function.name,
                                "arguments": tool_call.function.arguments
                            }
                        } for tool_call in message.tool_calls
                    ]
                })
                
                # Execute each tool call
                for tool_call in message.tool_calls:
                    try:
                        # Parse arguments
                        arguments = json.loads(tool_call.function.arguments)
                        
                        # Execute the tool
                        tool_result = self._execute_tool(tool_call.function.name, arguments)
                        
                        # Record the tool call
                        tool_calls_made.append({
                            "tool_name": tool_call.function.name,
                            "arguments": arguments,
                            "result": tool_result
                        })
                        
                        # Add tool result to messages
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(tool_result)
                        })
                        
                    except json.JSONDecodeError as e:
                        error_msg = f"Failed to parse tool arguments: {e}"
                        _logger.error(error_msg)
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps({"error": error_msg})
                        })
                    except Exception as e:
                        error_msg = f"Tool execution failed: {e}"
                        _logger.error(error_msg)
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps({"error": error_msg})
                        })
            
            # If we've reached max iterations, make a final call for the response
            final_response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.1
            )
            
            return {
                "response": final_response.choices[0].message.content,
                "tool_calls_made": tool_calls_made,
                "success": True,
                "max_iterations_reached": True
            }
            
        except Exception as e:
            _logger.error(f"Error in OpenAI chat: {e}")
            return {
                "error": str(e),
                "response": "I encountered an error while processing your request. Please try again or contact support.",
                "success": False
            }

    def simple_chat(self, user_message: str, conversation_history: Optional[List[Dict]] = None) -> str:
        """
        Simple chat interface that takes a user message and returns a response.
        
        Args:
            user_message: The user's message
            conversation_history: Optional previous conversation history
            
        Returns:
            The AI's response as a string
        """
        # Build messages array
        messages = conversation_history or []
        
        # Add system message if this is the start of conversation
        if not messages:
            messages.append({
                "role": "system",
                "content": """You are an AI assistant integrated into Odoo ERP system. You can help users with:
                - Sales orders: search, view, modify quantities, update states
                - Products: get information, check stock levels, update prices
                - CRM leads: create, view, update stages
                - Customers: view customer information
                
                Always be helpful, accurate, and provide clear explanations of what you're doing.
                When you use tools to retrieve or modify data, explain what you found or what changes you made."""
            })
        
        # Add the user's message
        messages.append({
            "role": "user",
            "content": user_message
        })
        
        # Get response with tools
        result = self.chat_with_tools(messages)
        
        if result.get("success"):
            return result.get("response", "I apologize, but I couldn't generate a response.")
        else:
            return result.get("response", "I encountered an error processing your request.")

    def _test_openai_threaded(self, api_key: str) -> Dict[str, Any]:
        """
        Test OpenAI connection in a separate thread to avoid web server blocking.
        """
        result = {"success": False, "error": None, "response": None}
        
        def run_test():
            try:
                client = OpenAI(
                    api_key=api_key,
                    timeout=httpx.Timeout(30.0, connect=30.0) if httpx else None,
                    max_retries=2
                )
                
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": "Say 'OK'"}],
                    max_tokens=5,
                    temperature=0
                )
                
                result.update({
                    "success": True,
                    "response": response.choices[0].message.content.strip(),
                    "config_used": "threaded"
                })
                
            except Exception as e:
                result.update({
                    "success": False,
                    "error": str(e),
                    "error_type": type(e).__name__
                })
        
        # Run in thread with timeout
        thread = threading.Thread(target=run_test)
        thread.daemon = True
        thread.start()
        thread.join(timeout=45)  # 45 second timeout
        
        if thread.is_alive():
            result.update({
                "success": False,
                "error": "Connection timeout",
                "error_type": "TimeoutError"
            })
        
        return result

    def test_openai_connection(self) -> Dict[str, Any]:
        """
        Test the OpenAI API connection with a simple ping.
        
        Returns:
            Dictionary with connection test results
        """
        # Debug: Check API key
        api_key = self._get_openai_api_key()
        if not api_key:
            return {
                "success": False,
                "error": "No API key configured",
                "message": "API key not configured in system parameters"
            }
        
        # Debug: Check OpenAI library
        if OpenAI is None:
            return {
                "success": False,
                "error": "OpenAI library not available",
                "message": "OpenAI library not installed"
            }
        
        # First try the threaded approach (might work better in Odoo web context)
        _logger.info("Trying threaded OpenAI connection test")
        threaded_result = self._test_openai_threaded(api_key)
        
        if threaded_result.get("success"):
            return {
                "success": True,
                "message": "OpenAI connection successful (threaded)",
                "response": threaded_result.get("response"),
                "model_used": "gpt-4o-mini",
                "api_key_preview": f"{api_key[:10]}..." if api_key else "None",
                "config_used": "threaded"
            }
        
        # If threaded approach failed, try the regular configurations
        clients_to_try = []
        
        # Configuration 1: Basic httpx timeout (simplified)
        if httpx is not None:
            try:
                clients_to_try.append((
                    "simple_httpx",
                    OpenAI(
                        api_key=api_key,
                        timeout=httpx.Timeout(30.0, connect=30.0),
                        max_retries=1
                    )
                ))
            except Exception as e:
                _logger.warning(f"Failed to create simple httpx client: {e}")
        
        # Configuration 2: Most basic client
        try:
            clients_to_try.append((
                "basic",
                OpenAI(api_key=api_key, max_retries=1)
            ))
        except Exception as e:
            _logger.warning(f"Failed to create basic client: {e}")
        
        if not clients_to_try:
            return {
                "success": False,
                "error": "Could not create any OpenAI client",
                "message": f"Failed to initialize OpenAI client. Threaded error: {threaded_result.get('error', 'Unknown')}"
            }

        # Try each client configuration
        last_error = None
        for config_name, client in clients_to_try:
            try:
                _logger.info(f"Trying OpenAI connection with {config_name} configuration")
                
                # Make a simple API call to test connection
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[{"role": "user", "content": "Say 'OK'"}],
                    max_tokens=5,
                    temperature=0
                )
                
                return {
                    "success": True,
                    "message": f"OpenAI connection successful with {config_name}",
                    "response": response.choices[0].message.content.strip(),
                    "model_used": "gpt-4o-mini",
                    "api_key_preview": f"{api_key[:10]}..." if api_key else "None",
                    "config_used": config_name
                }
                
            except Exception as e:
                last_error = e
                _logger.warning(f"OpenAI connection failed with {config_name}: {e}")
                continue
        
        # If we get here, all configurations failed
        _logger.error(f"All OpenAI client configurations failed. Last error: {last_error}")
        return {
            "success": False,
            "error": str(last_error),
            "message": f"All OpenAI configurations failed. Threaded: {threaded_result.get('error')}, Last: {str(last_error)}",
            "api_key_preview": f"{api_key[:10]}..." if api_key else "None",
            "error_type": type(last_error).__name__ if last_error else "Unknown",
            "configs_tried": [name for name, _ in clients_to_try],
            "threaded_error": threaded_result.get("error")
        }

