import os
import xmlrpc.client
import logging

logger = logging.getLogger(__name__)

def get_dynamic_odoo_proxy(url, db, username, password):
    """
    Establishes a connection to a specific Odoo instance using provided credentials.
    This is used for multi-tenant API calls.
    """
    try:
        common = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/common')
        uid = common.authenticate(db, username, password, {})
        if not uid:
            raise PermissionError("Odoo authentication failed for the provided credentials.")
        models = xmlrpc.client.ServerProxy(f'{url}/xmlrpc/2/object')
        # Return all necessary components to make calls later
        return {'uid': uid, 'models': models, 'db': db, 'password': password}
    except Exception as e:
        logger.error(f"Error connecting to dynamic Odoo instance at {url}: {e}")
        raise

# --- Odoo Connection Settings ---
ODOO_URL = os.getenv("ODOO_URL")
ODOO_DB = os.getenv("ODOO_DB")
ODOO_USERNAME = os.getenv("ODOO_USERNAME")
ODOO_PASSWORD = os.getenv("ODOO_PASSWORD")

def get_odoo_models_proxy():
    """Establishes connection to Odoo and returns a models proxy."""
    try:
        common = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/common')
        uid = common.authenticate(ODOO_DB, ODOO_USERNAME, ODOO_PASSWORD, {})
        if not uid:
            raise PermissionError("Odoo authentication failed.")
        models = xmlrpc.client.ServerProxy(f'{ODOO_URL}/xmlrpc/2/object')
        return uid, models
    except Exception as e:
        logger.error(f"Error connecting to Odoo: {e}")
        raise

# --- TOOL DEFINITION 1: Reading Data ---
def search_sales_order_by_name(order_name: str, odoo_conn: dict = None) -> dict:
    """
    Searches for a specific sales order by its name (e.g., S00004) and returns its details including order lines.
    """
    logger.info(f"Executing tool: search_sales_order_by_name with name='{order_name}'")
    try:
        if odoo_conn:
            uid = odoo_conn['uid']
            models = odoo_conn['models']
            db = odoo_conn['db']
            password = odoo_conn['password']
        else:
            uid, models = get_odoo_models_proxy()
            db = ODOO_DB
            password = ODOO_PASSWORD
        # Search for the sales order
        order_ids = models.execute_kw(
            db, uid, password, 'sale.order', 'search',
            [[['name', '=', order_name]]]
        )
        if not order_ids:
            return {"error": f"Sales order '{order_name}' not found."}
        # Read the sales order data including its order lines
        order_data = models.execute_kw(
            db, uid, password, 'sale.order', 'read',
            [order_ids],
            {'fields': ['name', 'partner_id', 'amount_total', 'state', 'order_line']}
        )
        if not order_data:
            return {"error": f"Could not read data for sales order '{order_name}'."}
        # Read the details of the order lines
        order_line_ids = order_data[0]['order_line']
        line_data = models.execute_kw(
            db, uid, password, 'sale.order.line', 'read',
            [order_line_ids],
            {'fields': ['product_id', 'product_uom_qty', 'price_unit']}
        )
        order_data[0]['order_line_details'] = line_data
        return order_data[0]
    except Exception as e:
        logger.error(f"Error in search_sales_order_by_name: {e}")
        return {"error": str(e)}

# --- TOOL DEFINITION 2: Writing Data ---
def create_new_lead(name: str, contact_name: str = None, email: str = None, phone: str = None, odoo_conn: dict = None) -> dict:
    """
    Creates a new lead/opportunity in the CRM module.
    """
    logger.info(f"Executing tool: create_new_lead with name='{name}'")
    try:
        if odoo_conn:
            uid = odoo_conn['uid']
            models = odoo_conn['models']
            db = odoo_conn['db']
            password = odoo_conn['password']
        else:
            uid, models = get_odoo_models_proxy()
            db = ODOO_DB
            password = ODOO_PASSWORD
        lead_data = {
            'name': name,
            'contact_name': contact_name,
            'email_from': email,
            'phone': phone,
        }
        # Filter out None values
        lead_data = {k: v for k, v in lead_data.items() if v is not None}
        new_lead_id = models.execute_kw(
            db, uid, password, 'crm.lead', 'create',
            [lead_data]
        )
        return {"success": True, "lead_id": new_lead_id, "message": f"Successfully created lead '{name}' with ID {new_lead_id}."}
    except Exception as e:
        logger.error(f"Error in create_new_lead: {e}")
        return {"error": str(e)}

def get_product_info(product_name: str, odoo_conn: dict = None) -> dict:
    """
    Searches for a product by its name and returns its id, price, and quantity on hand.
    """
    logger.info(f"Executing tool: get_product_info with name='{product_name}'")
    try:
        if odoo_conn:
            uid = odoo_conn['uid']
            models = odoo_conn['models']
            db = odoo_conn['db']
            password = odoo_conn['password']
        else:
            uid, models = get_odoo_models_proxy()
            db = ODOO_DB
            password = ODOO_PASSWORD
        product_ids = models.execute_kw(
            db, uid, password, 'product.product', 'search',
            [[['name', 'ilike', product_name]]]
        )
        if not product_ids:
            return {"error": f"Product '{product_name}' not found."}
        product_data = models.execute_kw(
            db, uid, password, 'product.product', 'read',
            [product_ids[0]], # Read the first match
            {'fields': ['id', 'name', 'list_price', 'qty_available']}
        )
        return product_data[0] if product_data else {}
    except Exception as e:
        logger.error(f"Error in get_product_info: {e}")
        return {"error": str(e)}

# --- TOOL DEFINITION 3: Change Sales Order Line Quantity ---
def change_sales_order_line_quantity(order_name: str, product_name: str, new_qty: float, odoo_conn: dict = None) -> dict:
    """
    Changes the quantity of a product in a specific sales order.
    """
    logger.info(f"Executing tool: change_sales_order_line_quantity for order='{order_name}', product='{product_name}', new_qty={new_qty}")
    try:
        if odoo_conn:
            uid = odoo_conn['uid']
            models = odoo_conn['models']
            db = odoo_conn['db']
            password = odoo_conn['password']
        else:
            uid, models = get_odoo_models_proxy()
            db = ODOO_DB
            password = ODOO_PASSWORD
        # Find the sales order
        order_ids = models.execute_kw(
            db, uid, password, 'sale.order', 'search',
            [[['name', '=', order_name]]]
        )
        if not order_ids:
            return {"error": f"Sales order '{order_name}' not found."}
        # Get order lines
        order_data = models.execute_kw(
            db, uid, password, 'sale.order', 'read',
            [order_ids], {'fields': ['order_line']}
        )
        order_line_ids = order_data[0]['order_line']
        # Find the order line for the product
        line_data = models.execute_kw(
            db, uid, password, 'sale.order.line', 'read',
            [order_line_ids], {'fields': ['id', 'product_id', 'product_uom_qty']}
        )
        target_line_id = None
        for line in line_data:
            product = line['product_id']
            if isinstance(product, list) and product_name.lower() in product[1].lower():
                target_line_id = line['id']
                break
        if not target_line_id:
            return {"error": f"Product '{product_name}' not found in sales order '{order_name}'."}
        # Update the quantity
        models.execute_kw(
            db, uid, password, 'sale.order.line', 'write',
            [[target_line_id], {'product_uom_qty': new_qty}]
        )
        return {"success": True, "message": f"Updated quantity for '{product_name}' in order '{order_name}' to {new_qty}."}
    except Exception as e:
        logger.error(f"Error in change_sales_order_line_quantity: {e}")
        return {"error": str(e)}

# --- TOOL DEFINITION 4: Change Product Stock Level ---
def change_product_stock_level(product_name: str, new_qty: float, odoo_conn: dict = None) -> dict:
    """
    Changes the stock level for a product by creating an inventory adjustment.
    """
    logger.info(f"Executing tool: change_product_stock_level for product='{product_name}', new_qty={new_qty}")
    try:
        if odoo_conn:
            uid = odoo_conn['uid']
            models = odoo_conn['models']
            db = odoo_conn['db']
            password = odoo_conn['password']
        else:
            uid, models = get_odoo_models_proxy()
            db = ODOO_DB
            password = ODOO_PASSWORD
        # Find the product
        product_ids = models.execute_kw(
            db, uid, password, 'product.product', 'search',
            [[['name', 'ilike', product_name]]]
        )
        if not product_ids:
            return {"error": f"Product '{product_name}' not found."}
        product_id = product_ids[0]
        # Create inventory adjustment
        inventory_id = models.execute_kw(
            db, uid, password, 'stock.inventory', 'create',
            [{
                'name': f'AI Adjustment for {product_name}',
                'product_ids': [(6, 0, [product_id])],
                'filter': 'product',
            }]
        )
        # Set the new quantity
        line_ids = models.execute_kw(
            db, uid, password, 'stock.inventory.line', 'search',
            [[['inventory_id', '=', inventory_id], ['product_id', '=', product_id]]]
        )
        if not line_ids:
            return {"error": f"Inventory line for '{product_name}' not found."}
        models.execute_kw(
            db, uid, password, 'stock.inventory.line', 'write',
            [[line_ids[0]], {'product_qty': new_qty}]
        )
        # Validate the inventory adjustment
        models.execute_kw(
            db, uid, password, 'stock.inventory', 'action_validate',
            [inventory_id]
        )
        return {"success": True, "message": f"Stock level for '{product_name}' set to {new_qty}."}
    except Exception as e:
        logger.error(f"Error in change_product_stock_level: {e}")
        return {"error": str(e)}

# --- TOOL DEFINITION 5: Fetch All Sales Orders ---
def fetch_all_sales_orders(odoo_conn: dict = None) -> list:
    """
    Fetches all sales orders with basic details.
    """
    logger.info("Executing tool: fetch_all_sales_orders")
    try:
        if odoo_conn:
            uid = odoo_conn['uid']
            models = odoo_conn['models']
            db = odoo_conn['db']
            password = odoo_conn['password']
        else:
            uid, models = get_odoo_models_proxy()
            db = ODOO_DB
            password = ODOO_PASSWORD
        order_ids = models.execute_kw(
            db, uid, password, 'sale.order', 'search',
            [[]]
        )
        orders = models.execute_kw(
            db, uid, password, 'sale.order', 'read',
            [order_ids], {'fields': ['name', 'partner_id', 'amount_total', 'state', 'order_line']}
        )
        return orders
    except Exception as e:
        logger.error(f"Error in fetch_all_sales_orders: {e}")
        return [{"error": str(e)}]

# --- TOOL DEFINITION 6: Update Sales Order State ---
def update_sales_order_state(order_name: str, new_state: str, odoo_conn: dict = None) -> dict:
    """
    Updates the state of a sales order (e.g., 'draft', 'sent', 'sale', 'done', 'cancel').
    """
    logger.info(f"Executing tool: update_sales_order_state for order='{order_name}', new_state='{new_state}'")
    try:
        if odoo_conn:
            uid = odoo_conn['uid']
            models = odoo_conn['models']
            db = odoo_conn['db']
            password = odoo_conn['password']
        else:
            uid, models = get_odoo_models_proxy()
            db = ODOO_DB
            password = ODOO_PASSWORD
        order_ids = models.execute_kw(
            db, uid, password, 'sale.order', 'search',
            [[['name', '=', order_name]]]
        )
        if not order_ids:
            return {"error": f"Sales order '{order_name}' not found."}
        models.execute_kw(
            db, uid, password, 'sale.order', 'write',
            [order_ids, {'state': new_state}]
        )
        return {"success": True, "message": f"Sales order '{order_name}' state updated to '{new_state}'."}
    except Exception as e:
        logger.error(f"Error in update_sales_order_state: {e}")
        return {"error": str(e)}

# --- TOOL DEFINITION 7: Create New Sales Order ---
def create_new_sales_order(partner_id: int, order_lines: list, odoo_conn: dict = None) -> dict:
    """
    Creates a new sales order for a given partner with specified order lines.
    order_lines: list of dicts with keys 'product_id', 'product_uom_qty', 'price_unit'
    """
    logger.info(f"Executing tool: create_new_sales_order for partner_id={partner_id}")
    try:
        if odoo_conn:
            uid = odoo_conn['uid']
            models = odoo_conn['models']
            db = odoo_conn['db']
            password = odoo_conn['password']
        else:
            uid, models = get_odoo_models_proxy()
            db = ODOO_DB
            password = ODOO_PASSWORD
        order_id = models.execute_kw(
            db, uid, password, 'sale.order', 'create',
            [{
                'partner_id': partner_id,
                'order_line': [
                    (0, 0, line) for line in order_lines
                ]
            }]
        )
        return {"success": True, "order_id": order_id, "message": f"Created new sales order with ID {order_id}."}
    except Exception as e:
        logger.error(f"Error in create_new_sales_order: {e}")
        return {"error": str(e)}

# --- TOOL DEFINITION 8: Update Product Price ---
def update_product_price(product_name: str, new_price: float, odoo_conn: dict = None) -> dict:
    """
    Updates the price of a product.
    """
    logger.info(f"Executing tool: update_product_price for product='{product_name}', new_price={new_price}")
    try:
        if odoo_conn:
            uid = odoo_conn['uid']
            models = odoo_conn['models']
            db = odoo_conn['db']
            password = odoo_conn['password']
        else:
            uid, models = get_odoo_models_proxy()
            db = ODOO_DB
            password = ODOO_PASSWORD
        product_ids = models.execute_kw(
            db, uid, password, 'product.product', 'search',
            [[['name', 'ilike', product_name]]]
        )
        if not product_ids:
            return {"error": f"Product '{product_name}' not found."}
        models.execute_kw(
            db, uid, password, 'product.product', 'write',
            [product_ids, {'list_price': new_price}]
        )
        return {"success": True, "message": f"Updated price for '{product_name}' to {new_price}."}
    except Exception as e:
        logger.error(f"Error in update_product_price: {e}")
        return {"error": str(e)}

# --- TOOL DEFINITION 9: Fetch All Products ---
def fetch_all_products(odoo_conn: dict = None) -> list:
    """
    Fetches all products with their name, price, and quantity on hand.
    """
    logger.info("Executing tool: fetch_all_products")
    try:
        if odoo_conn:
            uid = odoo_conn['uid']
            models = odoo_conn['models']
            db = odoo_conn['db']
            password = odoo_conn['password']
        else:
            uid, models = get_odoo_models_proxy()
            db = ODOO_DB
            password = ODOO_PASSWORD
        product_ids = models.execute_kw(
            db, uid, password, 'product.product', 'search',
            [[]]
        )
        products = models.execute_kw(
            db, uid, password, 'product.product', 'read',
            [product_ids], {'fields': ['name', 'list_price', 'qty_available']}
        )
        return products
    except Exception as e:
        logger.error(f"Error in fetch_all_products: {e}")
        return [{"error": str(e)}]

# --- TOOL DEFINITION 10: Fetch All Leads ---
def fetch_all_leads(odoo_conn: dict = None) -> list:
    """
    Fetches all leads/opportunities with basic details.
    """
    logger.info("Executing tool: fetch_all_leads")
    try:
        if odoo_conn:
            uid = odoo_conn['uid']
            models = odoo_conn['models']
            db = odoo_conn['db']
            password = odoo_conn['password']
        else:
            uid, models = get_odoo_models_proxy()
            db = ODOO_DB
            password = ODOO_PASSWORD
        lead_ids = models.execute_kw(
            db, uid, password, 'crm.lead', 'search',
            [[]]
        )
        leads = models.execute_kw(
            db, uid, password, 'crm.lead', 'read',
            [lead_ids], {'fields': ['name', 'contact_name', 'email_from', 'phone', 'stage_id', 'user_id']}
        )
        return leads
    except Exception as e:
        logger.error(f"Error in fetch_all_leads: {e}")
        return [{"error": str(e)}]

# --- TOOL DEFINITION 11: Update Lead Stage ---
def update_lead_stage(lead_id: int, new_stage_id: int, odoo_conn: dict = None) -> dict:
    """
    Updates the stage of a lead/opportunity.
    """
    logger.info(f"Executing tool: update_lead_stage for lead_id={lead_id}, new_stage_id={new_stage_id}")
    try:
        if odoo_conn:
            uid = odoo_conn['uid']
            models = odoo_conn['models']
            db = odoo_conn['db']
            password = odoo_conn['password']
        else:
            uid, models = get_odoo_models_proxy()
            db = ODOO_DB
            password = ODOO_PASSWORD
        models.execute_kw(
            db, uid, password, 'crm.lead', 'write',
            [[lead_id], {'stage_id': new_stage_id}]
        )
        return {"success": True, "message": f"Lead {lead_id} moved to stage {new_stage_id}."}
    except Exception as e:
        logger.error(f"Error in update_lead_stage: {e}")
        return {"error": str(e)}

# --- TOOL DEFINITION 12: Fetch All Customers ---
def fetch_all_customers(odoo_conn: dict = None) -> list:
    """
    Fetches all customers/partners with their name and email.
    """
    logger.info("Executing tool: fetch_all_customers")
    try:
        if odoo_conn:
            uid = odoo_conn['uid']
            models = odoo_conn['models']
            db = odoo_conn['db']
            password = odoo_conn['password']
        else:
            uid, models = get_odoo_models_proxy()
            db = ODOO_DB
            password = ODOO_PASSWORD
        partner_ids = models.execute_kw(
            db, uid, password, 'res.partner', 'search',
            [[['customer_rank', '>', 0]]]
        )
        partners = models.execute_kw(
            db, uid, password, 'res.partner', 'read',
            [partner_ids], {'fields': ['name', 'email']}
        )
        return partners
    except Exception as e:
        logger.error(f"Error in fetch_all_customers: {e}")
        return [{"error": str(e)}]

# --- TOOL DEFINITION: Fetch All Products Brief ---
def fetch_all_products_brief(odoo_conn: dict = None) -> list:
    """
    Fetches all products with their id and name only (for selection purposes).
    """
    logger.info("Executing tool: fetch_all_products_brief")
    try:
        if odoo_conn:
            uid = odoo_conn['uid']
            models = odoo_conn['models']
            db = odoo_conn['db']
            password = odoo_conn['password']
        else:
            uid, models = get_odoo_models_proxy()
            db = ODOO_DB
            password = ODOO_PASSWORD
        product_ids = models.execute_kw(
            db, uid, password, 'product.product', 'search',
            [[]]
        )
        products = models.execute_kw(
            db, uid, password, 'product.product', 'read',
            [product_ids], {'fields': ['id', 'name']}
        )
        return products
    except Exception as e:
        logger.error(f"Error in fetch_all_products_brief: {e}")
        return [{"error": str(e)}]

# --- TOOL DEFINITION: Fetch Product Variants ---
def fetch_product_variants(product_template_name: str = None, product_template_id: int = None, odoo_conn: dict = None) -> list:
    """
    Fetches all product variants for a given product template (by name or id), optionally matching attribute values from the input string.
    Returns a list of variants with id, name, attribute values, price, and stock.
    """
    logger.info(f"Executing tool: fetch_product_variants for template_name='{product_template_name}', template_id={product_template_id}")
    try:
        if odoo_conn:
            uid = odoo_conn['uid']
            models = odoo_conn['models']
            db = odoo_conn['db']
            password = odoo_conn['password']
        else:
            uid, models = get_odoo_models_proxy()
            db = ODOO_DB
            password = ODOO_PASSWORD

        # If product_template_id is provided, use it directly
        template_ids = []
        if product_template_id is not None:
            template_ids = [product_template_id]
        elif product_template_name:
            # Split input into words for flexible matching
            input_words = product_template_name.lower().split()
            # Search for all templates whose name contains any word
            all_template_ids = models.execute_kw(
                db, uid, password, 'product.template', 'search',
                [[['name', 'ilike', word]] for word in input_words]
            )
            if not all_template_ids:
                return {"error": f"No product template found matching '{product_template_name}'."}
            template_ids = all_template_ids
        else:
            return {"error": "Must provide either product_template_name or product_template_id."}

        matched_variants = []
        for tmpl_id in template_ids:
            # Get the template name
            tmpl_data = models.execute_kw(
                db, uid, password, 'product.template', 'read',
                [tmpl_id], {'fields': ['name']}
            )
            if not tmpl_data:
                continue
            tmpl_name = tmpl_data[0]['name']
            # Remove template name words from input to get possible attribute words
            attr_words = []
            if product_template_name:
                tmpl_name_words = set(tmpl_name.lower().split())
                input_words = product_template_name.lower().split()
                attr_words = [w for w in input_words if w not in tmpl_name_words]
            # Find all product.product (variants) for this template
            variant_ids = models.execute_kw(
                db, uid, password, 'product.product', 'search',
                [[['product_tmpl_id', '=', tmpl_id]]]
            )
            if not variant_ids:
                continue
            variants = models.execute_kw(
                db, uid, password, 'product.product', 'read',
                [variant_ids], {'fields': ['id', 'name', 'attribute_value_ids', 'list_price', 'qty_available']}
            )
            for variant in variants:
                # Fetch attribute value names
                attr_value_ids = variant.get('attribute_value_ids', [])
                attr_values = []
                if attr_value_ids:
                    attr_value_recs = models.execute_kw(
                        db, uid, password, 'product.attribute.value', 'read',
                        [attr_value_ids], {'fields': ['name', 'attribute_id']}
                    )
                    attr_values = [av['name'].lower() for av in attr_value_recs]
                    variant['attribute_values'] = [
                        {'attribute': av['attribute_id'][1] if isinstance(av['attribute_id'], list) else av['attribute_id'], 'value': av['name']} for av in attr_value_recs
                    ]
                else:
                    variant['attribute_values'] = []
                # If attr_words are present, all must match some attribute value
                if attr_words:
                    if all(any(word in attr for attr in attr_values) for word in attr_words):
                        matched_variants.append(variant)
                else:
                    matched_variants.append(variant)
        if not matched_variants:
            return {"error": f"No product variants found matching '{product_template_name}'."}
        return matched_variants
    except Exception as e:
        logger.error(f"Error in fetch_product_variants: {e}")
        return [{"error": str(e)}]