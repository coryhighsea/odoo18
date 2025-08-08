# -*- coding: utf-8 -*-
import json
import logging
import requests
from typing import List, Dict, Any, Optional

from odoo import api, models, fields
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class MicroserviceClient(models.TransientModel):
    _name = 'ai.agent.microservice.client'
    _description = 'Microservice Client for AI Agent Legacy Connection'

    @api.model
    def _get_service_url(self):
        """Get microservice URL from system parameters."""
        return self.env['ir.config_parameter'].sudo().get_param('ai_agent_odoo.service_url', 'http://localhost:8001')

    @api.model
    def _get_api_key(self):
        """Get API key from system parameters."""
        return self.env['ir.config_parameter'].sudo().get_param('ai_agent_odoo.api_key', '')

    @api.model
    def _is_microservice_configured(self):
        """Check if microservice is properly configured."""
        service_url = self._get_service_url()
        api_key = self._get_api_key()
        
        # Consider microservice configured if:
        # 1. API key is set (not empty)
        # 2. Service URL is not the default localhost:8001
        return bool(api_key) and service_url != 'http://localhost:8001'

    @api.model
    def send_chat_request(self, message: str, conversation_history: Optional[List[Dict]] = None):
        """
        Send a chat request to the external microservice.
        
        Args:
            message (str): The user's message
            conversation_history (list): Previous conversation history
            
        Returns:
            dict: Response from the microservice
        """
        try:
            service_url = self._get_service_url()
            api_key = self._get_api_key()
            
            if not service_url:
                raise ValidationError("Microservice URL not configured")
            
            if not api_key:
                raise ValidationError("API key not configured for microservice")
            
            # Prepare the request payload
            payload = {
                'message': message,
                'conversation_history': conversation_history or [],
                'db_name': self.env.cr.dbname,
                'user_id': self.env.user.id,
                'user_login': self.env.user.login
            }
            
            # Prepare headers with authentication
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {api_key}',
                'X-API-Key': api_key,  # Alternative auth header for compatibility
                'User-Agent': 'Odoo-AI-Agent/1.0'
            }
            
            # Construct the endpoint URL
            endpoint_url = f"{service_url.rstrip('/')}/chat"
            
            _logger.info(f"Sending request to microservice: {endpoint_url}")
            
            # Make the HTTP request
            response = requests.post(
                endpoint_url,
                json=payload,
                headers=headers,
                timeout=60,  # 60 second timeout
                verify=True  # Verify SSL certificates
            )
            
            # Check if request was successful
            response.raise_for_status()
            
            # Parse JSON response
            response_data = response.json()
            
            _logger.info(f"Microservice response received: {response.status_code}")
            
            return {
                'success': True,
                'message': response_data.get('message', 'No response message'),
                'data': response_data,
                'provider': 'microservice'
            }
            
        except requests.exceptions.Timeout:
            _logger.error("Microservice request timed out")
            return {
                'success': False,
                'error': 'Request timeout',
                'message': 'The microservice request timed out. Please try again.',
                'provider': 'microservice'
            }
            
        except requests.exceptions.ConnectionError as e:
            _logger.error(f"Connection error to microservice: {e}")
            return {
                'success': False,
                'error': 'Connection error',
                'message': f'Could not connect to microservice at {service_url}. Please check the service URL and network connectivity.',
                'provider': 'microservice'
            }
            
        except requests.exceptions.HTTPError as e:
            _logger.error(f"HTTP error from microservice: {e}")
            status_code = e.response.status_code if e.response else 'Unknown'
            
            if status_code == 401:
                error_msg = 'Authentication failed. Please check your API key.'
            elif status_code == 403:
                error_msg = 'Access forbidden. Please verify your API key permissions.'
            elif status_code == 404:
                error_msg = 'Microservice endpoint not found. Please check the service URL.'
            elif status_code >= 500:
                error_msg = 'Microservice internal error. Please try again later.'
            else:
                error_msg = f'HTTP error {status_code} from microservice.'
            
            return {
                'success': False,
                'error': f'HTTP {status_code}',
                'message': error_msg,
                'provider': 'microservice'
            }
            
        except json.JSONDecodeError as e:
            _logger.error(f"Invalid JSON response from microservice: {e}")
            return {
                'success': False,
                'error': 'Invalid response format',
                'message': 'Microservice returned invalid JSON response.',
                'provider': 'microservice'
            }
            
        except Exception as e:
            _logger.error(f"Unexpected error in microservice request: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'An unexpected error occurred while communicating with the microservice.',
                'provider': 'microservice'
            }

    @api.model
    def test_microservice_connection(self):
        """
        Test the connection to the microservice.
        
        Returns:
            dict: Test result with success status and details
        """
        try:
            service_url = self._get_service_url()
            api_key = self._get_api_key()
            
            if not service_url:
                return {
                    'success': False,
                    'error': 'Service URL not configured',
                    'message': 'Please configure ai_agent_odoo.service_url system parameter'
                }
            
            if not api_key:
                return {
                    'success': False,
                    'error': 'API key not configured',
                    'message': 'Please configure ai_agent_odoo.api_key system parameter'
                }
            
            # Send a simple test message
            test_response = self.send_chat_request("Hello, this is a connection test.")
            
            if test_response['success']:
                return {
                    'success': True,
                    'message': 'Microservice connection successful',
                    'service_url': service_url,
                    'api_key_preview': f"{api_key[:8]}..." if len(api_key) > 8 else "***",
                    'response_preview': test_response.get('message', '')[:100]
                }
            else:
                return {
                    'success': False,
                    'error': test_response.get('error', 'Unknown error'),
                    'message': f"Microservice connection failed: {test_response.get('message', 'Unknown error')}",
                    'service_url': service_url,
                    'api_key_preview': f"{api_key[:8]}..." if len(api_key) > 8 else "***"
                }
                
        except Exception as e:
            _logger.error(f"Error testing microservice connection: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f'Connection test failed: {str(e)}'
            }
