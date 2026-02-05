# Copyright (c) 2026, Emilio Cliff and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.query_builder import DocType
from frappe.query_builder.functions import Sum

from warehouse_management.warehouse_management.stock_management.stock_valuation import (
    get_moving_average_rate,
)


def execute(filters: dict | None = None):
    """Return columns and data for the report.

    This is the main entry point for the report. It accepts the filters as a
    dictionary and should return columns and data. It is called by the framework
    every time the report is refreshed or a filter is updated.
    """
    columns = get_columns()
    data = get_stock_balance()

    return columns, data


def get_columns() -> list[dict]:
    """Return columns for the report.

    One field definition per column, just like a DocType field definition.
    """
    columns = [
        {
            "label": _("Item Name"),
            "fieldname": "item_name",
            "fieldtype": "Data",
        },
        {
            "label": _("Balance Qty"),
            "fieldname": "balance_qty",
            "fieldtype": "Float",
        },
        {
            "label": _("Valuation Rate"),
            "fieldname": "valuation_rate",
            "fieldtype": "Currency",
        },
        {
            "label": _("Stock Value"),
            "fieldname": "stock_value",
            "fieldtype": "Currency",
        },
    ]

    return columns


def get_stock_balance():
    """Get stock balance data without filters."""
    as_on_date = frappe.utils.today()

    ssle = DocType("Stateless Stock Ledger Entry")
    item = DocType("Item")
    balance_qty = Sum(ssle.quantity).as_("balance_qty")

    q = (
        frappe.qb.from_(ssle)
        .select(ssle.item_code, item.item_name, ssle.warehouse, balance_qty)
        .left_join(item)
        .on(ssle.item_code == item.name)
        .where(ssle.posting_date <= as_on_date)
        .groupby(ssle.item_code, item.item_name, ssle.warehouse)
        .having(Sum(ssle.quantity) != 0)
        .orderby(ssle.item_code)
    )

    print(q.get_sql())
    print(q.walk())

    balance_data = q.run(as_dict=True)

    for row in balance_data:
        row.valuation_rate = get_moving_average_rate(
            row.item_code, row.warehouse, as_on_date
        )
        row.stock_value = row.balance_qty * row.valuation_rate

    return balance_data
