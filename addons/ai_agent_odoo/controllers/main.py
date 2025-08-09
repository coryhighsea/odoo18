# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
import json
import logging

_logger = logging.getLogger(__name__)


class AIAgentController(http.Controller):

    @http.route('/ai_agent_odoo/get_config', type='json', auth='user')
    def get_config(self):
        """
        Securely provides the AI Agent service URL to the frontend.
        The URL is stored in Odoo's System Parameters for easy configuration.
        """
        get_param = request.env['ir.config_parameter'].sudo().get_param
        openai_api_key = get_param('ai_agent_odoo.openai_api_key')
        service_url = get_param('ai_agent_odoo.service_url', 'http://localhost:8001')
        legacy_api_key = get_param('ai_agent_odoo.api_key')
        
        # Get AI agent configuration
        ai_agent = request.env['ai.agent'].search([], limit=1)
        if ai_agent:
            config = ai_agent.get_configuration()
        else:
            config = {'active': False}
        
        db = request.session.db
        login = request.session.login
        return {
            'openai_configured': bool(openai_api_key),
            'legacy_service_configured': bool(service_url and service_url != 'http://localhost:8001'),
            'legacy_api_key_configured': bool(legacy_api_key),
            'service_url': service_url,
            'ai_config': config,
            'db': db,
            'login': login,
        }

    @http.route('/ai_agent_odoo/chat', type='json', auth='user')
    def chat(self, message, conversation_history=None):
        """
        Handle chat requests from the frontend.
        
        Args:
            message (str): User's message
            conversation_history (list): Previous conversation messages
            
        Returns:
            dict: AI response
        """
        try:
            # Validate input
            if not message or not isinstance(message, str):
                return {
                    'success': False,
                    'error': 'Invalid message format',
                    'message': 'Please provide a valid message.'
                }
            
            # Get AI agent
            ai_agent = request.env['ai.agent'].search([('active', '=', True)], limit=1)
            if not ai_agent:
                return {
                    'success': False,
                    'error': 'No active AI agent found',
                    'message': 'AI Assistant is not configured. Please contact your administrator.'
                }
            
            # Process the message
            response = ai_agent.process_user_message(message, conversation_history)
            
            return response
            
        except Exception as e:
            _logger.error(f"Error in AI chat endpoint: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': 'An error occurred while processing your request. Please try again.'
            }

    @http.route('/ai_agent_odoo/test_connection', type='json', auth='user')
    def test_connection(self):
        """Test the AI service connections (OpenAI and legacy service)."""
        try:
            # Test both OpenAI and legacy service connections
            openai_client = request.env['ai.agent.openai.client']
            test_result = openai_client.test_openai_connection()
            
            return {
                'success': test_result.get('success', False),
                'message': test_result.get('message', 'Connection test completed'),
                'details': test_result,
                'available_methods': test_result.get('available_methods', []),
                'openai': test_result.get('openai', {}),
                'legacy_service': test_result.get('legacy_service', {})
            }
            
        except Exception as e:
            _logger.error(f"Error testing AI connection: {e}")
            return {
                'success': False,
                'message': f'Connection test failed: {str(e)}'
            }