# -*- coding: utf-8 -*-
from odoo import models, fields, api
import json
import logging

_logger = logging.getLogger(__name__)


class AIAgent(models.Model):
    _name = 'ai.agent'
    _description = 'AI Assistant Configuration'

    name = fields.Char('Name', required=True, default='AI Assistant')
    active = fields.Boolean('Active', default=True)
    model_provider = fields.Selection([
        ('openai', 'OpenAI'),
    ], string='AI Model Provider', default='openai', required=True)
    
    @api.model
    def process_user_message(self, message, conversation_history=None):
        """
        Process a user message and return an AI response using the configured provider.
        
        Args:
            message (str): The user's message
            conversation_history (list): Previous conversation history
            
        Returns:
            dict: Response containing the AI's message and any metadata
        """
        try:
            if self.model_provider == 'openai':
                return self._process_with_openai(message, conversation_history)
            else:
                return {
                    'success': False,
                    'message': 'Unsupported AI provider configured.',
                    'error': 'Invalid provider'
                }
        except Exception as e:
            _logger.error(f"Error processing user message: {e}")
            return {
                'success': False,
                'message': 'I encountered an error while processing your request. Please try again.',
                'error': str(e)
            }
    
    def _process_with_openai(self, message, conversation_history=None):
        """Process message using OpenAI with tool integration."""
        try:
            # Get OpenAI client
            openai_client = self.env['ai.agent.openai.client']
            
            # Process the message
            response = openai_client.simple_chat(message, conversation_history)
            
            return {
                'success': True,
                'message': response,
                'provider': 'openai'
            }
            
        except Exception as e:
            _logger.error(f"OpenAI processing error: {e}")
            return {
                'success': False,
                'message': 'I encountered an error while processing your request with OpenAI.',
                'error': str(e)
            }
    
    @api.model
    def get_configuration(self):
        """Get AI agent configuration for frontend."""
        # Initialize system parameters if they don't exist
        self._ensure_system_parameters()
        
        return {
            'active': True,
            'provider': 'openai',
            'capabilities': [
                'Sales Order Management',
                'Product Information',
                'CRM Lead Management', 
                'Customer Information',
                'Inventory Operations'
            ]
        }

    @api.model
    def _ensure_system_parameters(self):
        """Ensure required system parameters exist."""
        params_to_check = [
            ('ai_agent_odoo.openai_api_key', ''),
            ('ai_agent_odoo.service_url', 'http://localhost:8001'),
            ('ai_agent_odoo.api_key', ''),
        ]
        
        for key, default_value in params_to_check:
            existing = self.env['ir.config_parameter'].search([('key', '=', key)])
            if not existing:
                self.env['ir.config_parameter'].sudo().create({
                    'key': key,
                    'value': default_value
                })