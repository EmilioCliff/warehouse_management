# Warehouse Management

A comprehensive **warehouse management system** for inventory tracking, stock valuation, and real-time stock balance reporting. Built with Frappe using stateless stock ledger entries and moving average costing.

---

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [Setup](#setup)
- [License](#license)

---

## Features

### Core Functionality
- **Stock Ledger Tracking**: Stateless entries for all stock movements (receipt, issue, transfer)
- **Moving Average Costing**: Real-time valuation rate calculation based on incoming stock
- **Stock Balance Reports**: Showing current balances by item and warehouse
- **Stock Valuation**: Automatic value calculation (quantity × moving average rate)

### Reports
- **Stock Balance Report**: All items with current quantities and valuations
- **Historical Data**: Query stock levels from any past date

---

## Architecture

### Core Components

**Stock Ledger** (`stateless_stock_ledger.py`):
- Processes stock entries (Material Receipt, Issue, Transfer)
- Creates appropriate ledger entries on submission

**Valuation** (`stock_valuation.py`):
- `get_moving_average_rate()` - Calculates average cost per unit
- `get_stock_balance()` - Retrieves total quantity in warehouse
- `get_stock_value()` - Computes inventory value (qty × rate)

**Reports** (`stateless_stock_balance.py`):
- Queries balances grouped by item and warehouse
- Returns complete stock view with values

### DocTypes

**Stateless Stock Ledger Entry**:
- Immutable transaction record
- Links item, warehouse, quantity, and rate
- Tracks posting date for historical queries
- No update/delete after creation

---

## Setup

### Prerequisites
- Frappe Bench
- Python 3.8+
- MySQL/MariaDB

### Installation

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app https://github.com/EmilioCliff/warehouse_management.git
bench --site $SITE_NAME install-app warehouse_management
bench --site $SITE_NAME migrate
bench start
```

Access reports at: `$SITE_NAME/app/warehouse-management`

---

## Project Structure

```
warehouse_management/
├── warehouse_management/
│   ├── stock_management/
│   │   ├── stock_valuation.py      # Valuation calculations
│   │   └── stateless_stock_ledger.py # Ledger entry creation
│   ├── report/
│   │   └── stateless_stock_balance/ # Balance report
│   ├── doctype/
│   │   └── stateless_stock_ledger_entry/
│   └── hooks.py
├── pyproject.toml
└── README.md
```

---

## Testing

Run tests with:

```bash
bench --site $SITE_NAME run-tests --app warehouse_management
```

---

## License

MIT
