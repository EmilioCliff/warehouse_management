import frappe
from frappe import _

# Document status constants
DOCTYPE_STATUS_DRAFT = 0
DOCTYPE_STATUS_SUBMITTED = 1
DOCTYPE_STATUS_CANCELLED = 2

# Stock entry type constants
ENTRY_TYPE_RECEIPT = "Material Receipt"
ENTRY_TYPE_ISSUE = "Material Issue"
ENTRY_TYPE_TRANSFER = "Material Transfer"


def create_ledger_entries(doc, method=None):
    """
    Main entry point for creating stock ledger entries on document submission.
    Processes stock entry and creates appropriate ledger entries.
    """
    if not doc.docstatus == DOCTYPE_STATUS_SUBMITTED:
        return

    _process_stock_entry_items(doc)


def _process_stock_entry_items(doc):
    """Process each item in the stock entry based on entry type"""
    for item_row in doc.items:
        entry_type = doc.stock_entry_type

        if entry_type == ENTRY_TYPE_RECEIPT:
            _handle_material_receipt(doc, item_row)
        elif entry_type == ENTRY_TYPE_ISSUE:
            _handle_material_issue(doc, item_row)
        elif entry_type == ENTRY_TYPE_TRANSFER:
            _handle_material_transfer(doc, item_row)


def _handle_material_receipt(doc, item_row):
    """Handle Material Receipt: Create positive entry for target warehouse"""
    if not item_row.t_warehouse:
        return

    _create_ledger_entry_for_item(
        item=item_row,
        warehouse=item_row.t_warehouse,
        quantity=item_row.qty,
        rate=item_row.basic_rate,
        doc_info={
            "voucher_type": doc.doctype,
            "voucher_no": doc.name,
            "posting_date": doc.posting_date,
            "posting_time": doc.posting_time,
            "company": doc.company,
        },
    )


def _handle_material_issue(doc, item_row):
    """Handle Material Issue: Create negative entry for source warehouse"""
    if not item_row.s_warehouse:
        return

    outgoing_qty = -1 * item_row.qty
    _create_ledger_entry_for_item(
        item=item_row,
        warehouse=item_row.s_warehouse,
        quantity=outgoing_qty,
        rate=0,
        doc_info={
            "voucher_type": doc.doctype,
            "voucher_no": doc.name,
            "posting_date": doc.posting_date,
            "posting_time": doc.posting_time,
            "company": doc.company,
        },
    )


def _handle_material_transfer(doc, item_row):
    """Handle Material Transfer: Create entries for both source and target warehouses"""
    doc_info = {
        "voucher_type": doc.doctype,
        "voucher_no": doc.name,
        "posting_date": doc.posting_date,
        "posting_time": doc.posting_time,
        "company": doc.company,
    }

    # Process outgoing entry from source warehouse
    if item_row.s_warehouse:
        outgoing_qty = -1 * item_row.qty
        _create_ledger_entry_for_item(
            item=item_row,
            warehouse=item_row.s_warehouse,
            quantity=outgoing_qty,
            rate=0,
            doc_info=doc_info,
        )

    # Process incoming entry to target warehouse
    if item_row.t_warehouse:
        _create_ledger_entry_for_item(
            item=item_row,
            warehouse=item_row.t_warehouse,
            quantity=item_row.qty,
            rate=item_row.basic_rate,
            doc_info=doc_info,
        )


def _create_ledger_entry_for_item(item, warehouse, quantity, rate, doc_info):
    """
    Create a single stock ledger entry with provided parameters.
    Encapsulates the logic for determining incoming rate based on quantity.
    """
    incoming_rate = rate if quantity > 0 else 0

    entry_doc = frappe.get_doc(
        {
            "doctype": "Stateless Stock Ledger Entry",
            "item_code": item.item_code,
            "warehouse": warehouse,
            "quantity": quantity,
            "incoming_rate": incoming_rate,
            "voucher_type": doc_info["voucher_type"],
            "voucher_no": doc_info["voucher_no"],
            "voucher_detail_no": item.name,
            "company": doc_info["company"],
            "posting_date": doc_info["posting_date"],
            "posting_time": doc_info["posting_time"],
            "stock_uom": item.stock_uom,
            "transaction_uom": item.uom,
            "conversion_factor": item.conversion_factor,
        }
    )

    entry_doc.insert()


def delete_ledger_entries(doc, method=None):
    """
    Delete all stock ledger entries when a document is cancelled.
    Only processes documents in cancelled state.
    """
    if not doc.docstatus == DOCTYPE_STATUS_CANCELLED:
        return

    frappe.db.delete(
        "Stateless Stock Ledger Entry",
        {"voucher_type": doc.doctyp, "voucher_no": doc.name},
    )
