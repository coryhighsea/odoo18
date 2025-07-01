{
    'name': "AI Assistant",
    'version': '18.0.1.0.0',
    'category': 'Tools',
    'summary': "Integrates a powerful AI assistant into the Odoo interface.",
    'description': """
        This module provides a floating chat widget to interact with a backend AI service,
        allowing users to ask questions and trigger actions within Odoo.
    """,
    'license': 'LGPL-3',
    'author': 'Cory Hisey',
    'website': 'https://coryhisey.com',
    'depends': ['base', 'web', 'mail'],  # 'base' is included with 'web', so it's not strictly needed here

    'assets': {
        'web.assets_backend': [
            # Corrected paths relative to the addon root directory
            'ai_agent/static/src/css/ai_agent.css',
            'ai_agent/static/src/js/ai_agent.js',
            'ai_agent/static/src/xml/ai_agent.xml',
        ],
    },
    'images': ['static/images/changing-sales-order.png'],
    'installable': True,
    'application': True,
    'auto_install': False,
}