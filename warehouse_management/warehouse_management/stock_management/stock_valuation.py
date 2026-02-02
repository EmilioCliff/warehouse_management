import frappe
from frappe.utils import flt


def _get_effective_posting_date(posting_date):
    """Return posting date or today's date if not provided"""
    return posting_date or frappe.utils.today()


def _execute_valuation_query(query, params):
    """Execute SQL query and return first result or 0"""
    result = frappe.db.sql(query, params, as_dict=True)
    return result[0] if result else {}


def get_moving_average_rate(item_code, warehouse, posting_date=None):
    """
    Calculate moving average rate for an item in a warehouse.
    Formula: Total value of incoming stock / Total incoming quantity
    """
    effective_date = _get_effective_posting_date(posting_date)

    query = """
        SELECT 
            SUM(quantity * incoming_rate) / NULLIF(SUM(quantity), 0) as valuation_rate
        FROM `tabStateless Stock Ledger Entry`
        WHERE item_code = %s
            AND warehouse = %s
            AND posting_date <= %s
            AND quantity > 0
    """

    result = _execute_valuation_query(query, (item_code, warehouse, effective_date))
    return flt(result.get("valuation_rate", 0))


def get_stock_balance(item_code, warehouse, posting_date=None):
    """Get current stock balance for an item in a warehouse"""
    effective_date = _get_effective_posting_date(posting_date)

    query = """
        SELECT SUM(quantity) as balance
        FROM `tabStateless Stock Ledger Entry`
        WHERE item_code = %s
            AND warehouse = %s
            AND posting_date <= %s
    """

    result = _execute_valuation_query(query, (item_code, warehouse, effective_date))
    return flt(result.get("balance", 0))


def get_stock_value(item_code, warehouse, posting_date=None):
    """Calculate total stock value: quantity × moving average rate"""
    effective_date = _get_effective_posting_date(posting_date)

    balance = get_stock_balance(item_code, warehouse, effective_date)
    avg_rate = get_moving_average_rate(item_code, warehouse, effective_date)

    return flt(balance * avg_rate)
