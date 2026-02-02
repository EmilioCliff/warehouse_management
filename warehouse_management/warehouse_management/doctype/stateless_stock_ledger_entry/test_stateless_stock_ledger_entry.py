# Copyright (c) 2026, Emilio Cliff and Contributors
# See license.txt

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import nowtime, today

from warehouse_management.warehouse_management.stock_management.stock_valuation import (
    get_moving_average_rate,
    get_stock_balance,
)

# Test record dependencies configuration
EXTRA_TEST_RECORD_DEPENDENCIES = []
IGNORE_TEST_RECORD_DEPENDENCIES = []


class IntegrationTestStatelessStockLedgerEntry(IntegrationTestCase):
    """Test suite for Stateless Stock Ledger Entry functionality"""

    TEST_COMPANY = "_Test Company"
    TEST_ITEM = "_Test Stateless Item"
    TEST_WAREHOUSE = "_Test Stateless Warehouse - _C"
    CURRENCY = "KES"
    UOM = "Nos"

    def setUp(self):
        """Initialize test environment with required data"""
        self._initialize_test_environment()

    def tearDown(self):
        """Clean up test data after each test"""
        self._cleanup_test_data()

    def _initialize_test_environment(self):
        """Set up all necessary test fixtures"""
        self._setup_company()
        self._setup_item()
        self._setup_warehouse()

    def _setup_company(self):
        """Create test company if not already present"""
        if frappe.db.exists("Company", self.TEST_COMPANY):
            return

        company_doc = frappe.get_doc(
            {
                "doctype": "Company",
                "company_name": self.TEST_COMPANY,
                "default_currency": self.CURRENCY,
            }
        )
        company_doc.insert()

    def _setup_item(self):
        """Create test item if not already present"""
        if frappe.db.exists("Item", self.TEST_ITEM):
            return

        item_doc = frappe.get_doc(
            {
                "doctype": "Item",
                "item_code": self.TEST_ITEM,
                "item_name": "Test Stateless Item",
                "item_group": "All Item Groups",
                "is_stock_item": 1,
                "stock_uom": self.UOM,
            }
        )
        item_doc.insert()

    def _setup_warehouse(self):
        """Create test warehouse if not already present"""
        if frappe.db.exists("Warehouse", self.TEST_WAREHOUSE):
            return

        warehouse_doc = frappe.get_doc(
            {
                "doctype": "Warehouse",
                "warehouse_name": self.TEST_WAREHOUSE,
                "company": self.TEST_COMPANY,
            }
        )
        warehouse_doc.insert()

    def _cleanup_test_data(self):
        """Remove all test ledger entries"""
        frappe.db.sql(
            """
            DELETE FROM `tabStateless Stock Ledger Entry`
            WHERE item_code = %s
        """,
            (self.TEST_ITEM,),
        )

    def _create_stock_ledger_entry(self, qty, rate, voucher_no, submit=False):
        """Helper method to create stock ledger entries"""
        entry_doc = frappe.get_doc(
            {
                "doctype": "Stateless Stock Ledger Entry",
                "item_code": self.TEST_ITEM,
                "warehouse": self.TEST_WAREHOUSE,
                "posting_date": today(),
                "posting_time": nowtime(),
                "quantity": qty,
                "incoming_rate": rate,
                "voucher_type": "Stock Entry",
                "voucher_no": voucher_no,
                "company": self.TEST_COMPANY,
                "stock_uom": self.UOM,
                "transaction_uom": self.UOM,
            }
        )
        entry_doc.insert()

        if submit:
            entry_doc.submit()

        return entry_doc

    def _get_current_valuation_rate(self):
        """Retrieve current moving average rate"""
        return get_moving_average_rate(self.TEST_ITEM, self.TEST_WAREHOUSE)

    def _get_current_stock_balance(self):
        """Retrieve current stock balance"""
        return get_stock_balance(self.TEST_ITEM, self.TEST_WAREHOUSE)

    def test_moving_average_calculation(self):
        """Test moving average rate calculation with multiple transactions"""
        # Initial receipt: 10 units at rate 100
        initial_qty = 10
        initial_rate = 100
        self._create_stock_ledger_entry(
            qty=initial_qty, rate=initial_rate, voucher_no="TEST-ENTRY-1", submit=True
        )

        # Verify initial valuation
        first_valuation = self._get_current_valuation_rate()
        self.assertEqual(
            first_valuation,
            initial_rate,
            f"Initial valuation rate should be {initial_rate}, got {first_valuation}",
        )

        # Second receipt: 5 units at rate 120
        second_qty = 5
        second_rate = 120
        self._create_stock_ledger_entry(
            qty=second_qty, rate=second_rate, voucher_no="TEST-ENTRY-2", submit=False
        )

        # Calculate expected moving average: (10*100 + 5*120)/15 = 106.67
        total_value = (initial_qty * initial_rate) + (second_qty * second_rate)
        total_qty = initial_qty + second_qty
        expected_avg = total_value / total_qty

        current_valuation = self._get_current_valuation_rate()
        self.assertAlmostEqual(
            current_valuation,
            expected_avg,
            delta=0.01,
            msg=f"Moving average should be {expected_avg:.2f}, got {current_valuation}",
        )

        # Verify total stock balance
        current_balance = self._get_current_stock_balance()
        self.assertEqual(
            current_balance,
            total_qty,
            f"Stock balance should be {total_qty} units, got {current_balance}",
        )

        # Consumption: 8 units issued
        consumption_qty = -8
        self._create_stock_ledger_entry(
            qty=consumption_qty, rate=0, voucher_no="TEST-ENTRY-3", submit=False
        )

        # Verify remaining balance after consumption
        remaining_balance = self._get_current_stock_balance()
        expected_balance = total_qty + consumption_qty  # 15 + (-8) = 7
        self.assertEqual(
            remaining_balance,
            expected_balance,
            f"Stock balance after consumption should be {expected_balance} units, got {remaining_balance}",
        )

        # Verify valuation rate remains unchanged after consumption
        post_consumption_rate = self._get_current_valuation_rate()
        self.assertAlmostEqual(
            post_consumption_rate,
            expected_avg,
            delta=0.01,
            msg="Valuation rate should remain constant after consumption",
        )
