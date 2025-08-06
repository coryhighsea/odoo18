# -*- coding: utf-8 -*-
import logging
from odoo import api, models, fields
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class AIAgentTools(models.TransientModel):
    _name = 'ai.agent.tools'
    _description = 'AI Agent Tools for Odoo Operations'

    def search_sales_order_by_name(self, order_name: str) -> dict:
        """
        Searches for a specific sales order by its name (e.g., S00004) and returns its details including order lines.
        """
        try:
            # Search for the sales order
            order = self.env['sale.order'].search([('name', '=', order_name)], limit=1)
            
            if not order:
                return {"error": f"Sales order '{order_name}' not found."}
            
            # Prepare order data
            order_data = {
                'id': order.id,
                'name': order.name,
                'partner_id': [order.partner_id.id, order.partner_id.name] if order.partner_id else False,
                'amount_total': order.amount_total,
                'state': order.state,
                'date_order': order.date_order.isoformat() if order.date_order else False,
                'order_line_details': []
            }
            
            # Get order line details
            for line in order.order_line:
                line_data = {
                    'id': line.id,
                    'product_id': [line.product_id.id, line.product_id.name] if line.product_id else False,
                    'product_uom_qty': line.product_uom_qty,
                    'price_unit': line.price_unit,
                    'price_total': line.price_total,
                }
                order_data['order_line_details'].append(line_data)
            
            return order_data
            
        except Exception as e:
            _logger.error(f"Error in search_sales_order_by_name: {e}")
            return {"error": str(e)}

    def create_new_lead(self, name: str, contact_name: str = None, email: str = None, phone: str = None) -> dict:
        """
        Creates a new lead/opportunity in the CRM module.
        """
        try:
            lead_data = {
                'name': name,
                'contact_name': contact_name,
                'email_from': email,
                'phone': phone,
            }
            
            # Filter out None values
            lead_data = {k: v for k, v in lead_data.items() if v is not None}
            
            # Create the lead
            new_lead = self.env['crm.lead'].create(lead_data)
            
            return {
                "success": True, 
                "lead_id": new_lead.id, 
                "message": f"Successfully created lead '{name}' with ID {new_lead.id}."
            }
            
        except Exception as e:
            _logger.error(f"Error in create_new_lead: {e}")
            return {"error": str(e)}

    def get_product_info(self, product_name: str) -> dict:
        """
        Searches for a product by its name and returns its id, price, and quantity on hand.
        """
        try:
            # Search for the product
            product = self.env['product.product'].search([('name', 'ilike', product_name)], limit=1)
            
            if not product:
                return {"error": f"Product '{product_name}' not found."}
            
            product_data = {
                'id': product.id,
                'name': product.name,
                'list_price': product.list_price,
                'qty_available': product.qty_available,
                'uom_name': product.uom_id.name if product.uom_id else '',
            }
            
            return product_data
            
        except Exception as e:
            _logger.error(f"Error in get_product_info: {e}")
            return {"error": str(e)}

    def change_sales_order_line_quantity(self, order_name: str, product_name: str, new_qty: float) -> dict:
        """
        Changes the quantity of a product in a specific sales order.
        """
        try:
            # Find the sales order
            order = self.env['sale.order'].search([('name', '=', order_name)], limit=1)
            
            if not order:
                return {"error": f"Sales order '{order_name}' not found."}
            
            # Find the order line for the product
            order_line = order.order_line.filtered(
                lambda line: line.product_id and product_name.lower() in line.product_id.name.lower()
            )
            
            if not order_line:
                return {"error": f"Product '{product_name}' not found in sales order '{order_name}'."}
            
            # Take the first matching line
            order_line = order_line[0]
            
            # Update the quantity
            order_line.write({'product_uom_qty': new_qty})
            
            return {
                "success": True, 
                "message": f"Updated quantity for '{product_name}' in order '{order_name}' to {new_qty}."
            }
            
        except Exception as e:
            _logger.error(f"Error in change_sales_order_line_quantity: {e}")
            return {"error": str(e)}

    def fetch_all_sales_orders(self) -> list:
        """
        Fetches all sales orders with basic details.
        """
        try:
            orders = self.env['sale.order'].search([])
            result = []
            
            for order in orders:
                order_data = {
                    'id': order.id,
                    'name': order.name,
                    'partner_id': [order.partner_id.id, order.partner_id.name] if order.partner_id else False,
                    'amount_total': order.amount_total,
                    'state': order.state,
                    'date_order': order.date_order.isoformat() if order.date_order else False,
                }
                result.append(order_data)
            
            return result
            
        except Exception as e:
            _logger.error(f"Error in fetch_all_sales_orders: {e}")
            return [{"error": str(e)}]

    def fetch_all_products(self) -> list:
        """
        Fetches all products with their name, price, and quantity on hand.
        """
        try:
            products = self.env['product.product'].search([])
            result = []
            
            for product in products:
                product_data = {
                    'id': product.id,
                    'name': product.name,
                    'list_price': product.list_price,
                    'qty_available': product.qty_available,
                    'uom_name': product.uom_id.name if product.uom_id else '',
                }
                result.append(product_data)
            
            return result
            
        except Exception as e:
            _logger.error(f"Error in fetch_all_products: {e}")
            return [{"error": str(e)}]

    def fetch_all_leads(self) -> list:
        """
        Fetches all leads/opportunities with basic details.
        """
        try:
            leads = self.env['crm.lead'].search([])
            result = []
            
            for lead in leads:
                lead_data = {
                    'id': lead.id,
                    'name': lead.name,
                    'contact_name': lead.contact_name,
                    'email_from': lead.email_from,
                    'phone': lead.phone,
                    'stage_id': [lead.stage_id.id, lead.stage_id.name] if lead.stage_id else False,
                    'user_id': [lead.user_id.id, lead.user_id.name] if lead.user_id else False,
                }
                result.append(lead_data)
            
            return result
            
        except Exception as e:
            _logger.error(f"Error in fetch_all_leads: {e}")
            return [{"error": str(e)}]

    def fetch_all_customers(self) -> list:
        """
        Fetches all customers/partners with their name and email.
        """
        try:
            partners = self.env['res.partner'].search([('customer_rank', '>', 0)])
            result = []
            
            for partner in partners:
                partner_data = {
                    'id': partner.id,
                    'name': partner.name,
                    'email': partner.email,
                    'phone': partner.phone,
                    'city': partner.city,
                    'country_id': [partner.country_id.id, partner.country_id.name] if partner.country_id else False,
                }
                result.append(partner_data)
            
            return result
            
        except Exception as e:
            _logger.error(f"Error in fetch_all_customers: {e}")
            return [{"error": str(e)}]

    def update_sales_order_state(self, order_name: str, new_state: str) -> dict:
        """
        Updates the state of a sales order (e.g., 'draft', 'sent', 'sale', 'done', 'cancel').
        """
        try:
            order = self.env['sale.order'].search([('name', '=', order_name)], limit=1)
            
            if not order:
                return {"error": f"Sales order '{order_name}' not found."}
            
            # Validate state
            valid_states = ['draft', 'sent', 'sale', 'done', 'cancel']
            if new_state not in valid_states:
                return {"error": f"Invalid state '{new_state}'. Valid states are: {', '.join(valid_states)}"}
            
            # Update the state
            order.write({'state': new_state})
            
            return {
                "success": True, 
                "message": f"Sales order '{order_name}' state updated to '{new_state}'."
            }
            
        except Exception as e:
            _logger.error(f"Error in update_sales_order_state: {e}")
            return {"error": str(e)}

    def update_product_price(self, product_name: str, new_price: float) -> dict:
        """
        Updates the price of a product.
        """
        try:
            product = self.env['product.product'].search([('name', 'ilike', product_name)], limit=1)
            
            if not product:
                return {"error": f"Product '{product_name}' not found."}
            
            # Update the price
            product.write({'list_price': new_price})
            
            return {
                "success": True, 
                "message": f"Updated price for '{product_name}' to {new_price}."
            }
            
        except Exception as e:
            _logger.error(f"Error in update_product_price: {e}")
            return {"error": str(e)}

    def update_lead_stage(self, lead_id: int, new_stage_id: int) -> dict:
        """
        Updates the stage of a lead/opportunity.
        """
        try:
            lead = self.env['crm.lead'].browse(lead_id)
            
            if not lead.exists():
                return {"error": f"Lead with ID {lead_id} not found."}
            
            stage = self.env['crm.stage'].browse(new_stage_id)
            if not stage.exists():
                return {"error": f"Stage with ID {new_stage_id} not found."}
            
            # Update the stage
            lead.write({'stage_id': new_stage_id})
            
            return {
                "success": True, 
                "message": f"Lead {lead_id} moved to stage {stage.name}."
            }
            
        except Exception as e:
            _logger.error(f"Error in update_lead_stage: {e}")
            return {"error": str(e)}
