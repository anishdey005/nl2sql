"""
Schema Catalog & Metadata Mapping Layer for Enterprise Database.
Provides table definitions, column types, foreign key relationships,
semantic business aliases, and graph-based join path resolution.
"""

from typing import Dict, List, Set, Tuple, Optional
import os
import sqlite3

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
DB_PATH = os.path.join(PROJECT_ROOT, "data", "enterprise.db")


# Explicit Semantic Metadata for all 22 Tables
TABLE_METADATA = {
    "departments": {
        "description": "Company departments, budgets, and leadership",
        "columns": {
            "department_id": "INTEGER PRIMARY KEY - Unique ID of department",
            "name": "TEXT - Department name (e.g. Engineering, Sales, Customer Support, Finance)",
            "code": "TEXT - Short code (ENG, SLS, SUP, FIN, HR, etc.)",
            "budget": "REAL - Annual budget in USD",
            "created_at": "TEXT - Creation timestamp",
        },
        "keywords": ["department", "dept", "budget", "cost center"],
    },
    "employees": {
        "description": "Company staff, job titles, salaries, managers, and departments",
        "columns": {
            "employee_id": "INTEGER PRIMARY KEY - Unique employee ID",
            "department_id": "INTEGER - FK to departments.department_id",
            "manager_id": "INTEGER - FK self-reference to employees.employee_id",
            "first_name": "TEXT - First name",
            "last_name": "TEXT - Last name",
            "email": "TEXT - Internal work email",
            "phone": "TEXT - Work phone",
            "job_title": "TEXT - Job title / role",
            "salary": "REAL - Annual salary in USD",
            "hire_date": "TEXT - Date hired (YYYY-MM-DD)",
            "status": "TEXT - 'active', 'on_leave', 'terminated'",
        },
        "keywords": ["employee", "staff", "worker", "salary", "payroll", "manager", "hired", "job title", "team"],
    },
    "customers": {
        "description": "Customers who purchase products across retail and enterprise tiers",
        "columns": {
            "customer_id": "INTEGER PRIMARY KEY - Unique customer ID",
            "first_name": "TEXT - First name",
            "last_name": "TEXT - Last name",
            "email": "TEXT - Customer email",
            "phone": "TEXT - Phone number",
            "customer_segment": "TEXT - 'Enterprise', 'SMB', 'Consumer', 'VIP'",
            "status": "TEXT - 'active', 'inactive', 'suspended'",
            "created_at": "TEXT - Sign-up timestamp (YYYY-MM-DD HH:MM:SS)",
        },
        "keywords": ["customer", "client", "buyer", "user", "segment", "vip", "enterprise client", "consumer"],
    },
    "customer_addresses": {
        "description": "Physical addresses for customer shipping and billing",
        "columns": {
            "address_id": "INTEGER PRIMARY KEY - Unique address ID",
            "customer_id": "INTEGER - FK to customers.customer_id",
            "address_type": "TEXT - 'shipping' or 'billing'",
            "street": "TEXT - Street address",
            "city": "TEXT - City name",
            "state": "TEXT - Two-letter state abbreviation (CA, TX, NY, WA, etc.)",
            "postal_code": "TEXT - Postal / ZIP code",
            "country": "TEXT - Country (USA)",
            "is_default": "INTEGER - 1 if primary address, 0 otherwise",
        },
        "keywords": ["address", "city", "state", "postal", "zip", "location", "billing address", "shipping address"],
    },
    "product_categories": {
        "description": "Product taxonomy and categories",
        "columns": {
            "category_id": "INTEGER PRIMARY KEY - Category ID",
            "parent_category_id": "INTEGER - Self-reference FK for subcategories",
            "name": "TEXT - Category name (e.g. Computers & Laptops, Audio, Smart Home)",
            "description": "TEXT - Details of category",
        },
        "keywords": ["category", "categories", "product line", "product type"],
    },
    "products": {
        "description": "Catalog of all products sold",
        "columns": {
            "product_id": "INTEGER PRIMARY KEY - Unique product ID",
            "category_id": "INTEGER - FK to product_categories.category_id",
            "name": "TEXT - Product name",
            "sku": "TEXT - Stock keeping unit identifier",
            "description": "TEXT - Product specifications and description",
            "base_price": "REAL - Retail price in USD",
            "cost_price": "REAL - Manufacturing/procurement unit cost in USD",
            "is_active": "INTEGER - 1 if available for sale, 0 if discontinued",
            "created_at": "TEXT - Date added to catalog",
        },
        "keywords": ["product", "item", "catalog", "price", "cost", "sku", "merchandise", "profit margin"],
    },
    "product_variants": {
        "description": "Color, size, and specification variations of products",
        "columns": {
            "variant_id": "INTEGER PRIMARY KEY - Variant ID",
            "product_id": "INTEGER - FK to products.product_id",
            "sku": "TEXT - Variant SKU",
            "color": "TEXT - Color (Space Gray, Silver, Midnight Black, etc.)",
            "size": "TEXT - Size or capacity (Standard, 16GB / 512GB, 32GB / 1TB, etc.)",
            "price_adjustment": "REAL - Price difference from product base_price",
            "stock_quantity": "INTEGER - Units available",
        },
        "keywords": ["variant", "color", "size", "edition", "specification"],
    },
    "suppliers": {
        "description": "External vendors providing hardware components and raw inventory",
        "columns": {
            "supplier_id": "INTEGER PRIMARY KEY - Unique supplier ID",
            "name": "TEXT - Supplier company name",
            "contact_name": "TEXT - Primary representative",
            "email": "TEXT - Contact email",
            "phone": "TEXT - Contact phone",
            "city": "TEXT - Supplier city",
            "country": "TEXT - Supplier country (USA, Japan, Germany, Taiwan, etc.)",
            "rating": "REAL - Supplier reliability score (1.0 to 5.0)",
            "status": "TEXT - 'active', 'probation', 'inactive'",
        },
        "keywords": ["supplier", "vendor", "manufacturer", "partner", "procurement source", "supplier rating"],
    },
    "warehouses": {
        "description": "Distribution centers and storage facilities",
        "columns": {
            "warehouse_id": "INTEGER PRIMARY KEY - Unique warehouse ID",
            "manager_employee_id": "INTEGER - FK to employees.employee_id",
            "name": "TEXT - Facility name",
            "location_city": "TEXT - City location",
            "state": "TEXT - State",
            "country": "TEXT - Country",
            "capacity_units": "INTEGER - Total inventory unit capacity",
        },
        "keywords": ["warehouse", "fulfillment center", "facility", "depot", "hub", "storage location"],
    },
    "inventory_items": {
        "description": "Real-time stock quantities across warehouses for each product",
        "columns": {
            "inventory_id": "INTEGER PRIMARY KEY - Unique inventory record ID",
            "product_id": "INTEGER - FK to products.product_id",
            "variant_id": "INTEGER - FK to product_variants.variant_id",
            "warehouse_id": "INTEGER - FK to warehouses.warehouse_id",
            "quantity_on_hand": "INTEGER - Current units in stock",
            "reorder_point": "INTEGER - Threshold for low stock alert",
            "last_restocked_at": "TEXT - Date of last restock (YYYY-MM-DD)",
        },
        "keywords": ["inventory", "stock", "quantity on hand", "out of stock", "reorder", "low stock", "restocked"],
    },
    "purchase_orders": {
        "description": "Procurement orders placed to external suppliers for inventory replenishment",
        "columns": {
            "po_id": "INTEGER PRIMARY KEY - Purchase order number",
            "supplier_id": "INTEGER - FK to suppliers.supplier_id",
            "warehouse_id": "INTEGER - FK to warehouses.warehouse_id",
            "created_by_employee_id": "INTEGER - FK to employees.employee_id",
            "order_date": "TEXT - Date PO was created (YYYY-MM-DD)",
            "expected_date": "TEXT - Anticipated delivery date",
            "total_amount": "REAL - Total cost in USD",
            "status": "TEXT - 'draft', 'ordered', 'received', 'cancelled'",
        },
        "keywords": ["purchase order", "po", "supplier order", "procurement", "order from supplier"],
    },
    "purchase_order_items": {
        "description": "Line items for purchase orders placed to suppliers",
        "columns": {
            "po_item_id": "INTEGER PRIMARY KEY - PO item ID",
            "po_id": "INTEGER - FK to purchase_orders.po_id",
            "product_id": "INTEGER - FK to products.product_id",
            "quantity_ordered": "INTEGER - Units ordered from supplier",
            "unit_cost": "REAL - Agreed price per unit in USD",
            "quantity_received": "INTEGER - Units delivered to warehouse so far",
        },
        "keywords": ["po item", "procured item", "quantity ordered", "unit cost"],
    },
    "coupons": {
        "description": "Promotional discount codes and campaigns",
        "columns": {
            "coupon_id": "INTEGER PRIMARY KEY - Coupon ID",
            "code": "TEXT - Promo code string (e.g. SUMMER20, ENTERPRISE15)",
            "discount_type": "TEXT - 'percentage' or 'fixed_amount'",
            "discount_value": "REAL - % discount or dollar amount discount",
            "min_order_amount": "REAL - Minimum order spend required",
            "start_date": "TEXT - Valid from (YYYY-MM-DD)",
            "end_date": "TEXT - Valid until (YYYY-MM-DD)",
            "max_uses": "INTEGER - Max redemption allowance",
            "times_used": "INTEGER - Total times redeemed",
            "is_active": "INTEGER - 1 if active, 0 if expired/disabled",
        },
        "keywords": ["coupon", "promo", "promotion", "discount code", "voucher", "campaign"],
    },
    "orders": {
        "description": "Customer purchase orders",
        "columns": {
            "order_id": "INTEGER PRIMARY KEY - Unique order ID",
            "customer_id": "INTEGER - FK to customers.customer_id",
            "shipping_address_id": "INTEGER - FK to customer_addresses.address_id",
            "order_date": "TEXT - Date & time order placed (YYYY-MM-DD HH:MM:SS)",
            "status": "TEXT - 'pending', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded'",
            "subtotal": "REAL - Sum of line items before tax/discount",
            "tax_amount": "REAL - Sales tax charged",
            "shipping_fee": "REAL - Freight/shipping charge",
            "discount_amount": "REAL - Total coupon/promo savings",
            "total_amount": "REAL - Final total billed (subtotal + tax + shipping - discount)",
            "payment_method": "TEXT - 'credit_card', 'paypal', 'bank_transfer', 'apple_pay'",
        },
        "keywords": ["order", "sale", "revenue", "sales", "spending", "spend", "purchased", "transaction", "bought", "gross sales"],
    },
    "order_items": {
        "description": "Line items contained within each customer order",
        "columns": {
            "order_item_id": "INTEGER PRIMARY KEY - Order line ID",
            "order_id": "INTEGER - FK to orders.order_id",
            "product_id": "INTEGER - FK to products.product_id",
            "variant_id": "INTEGER - FK to product_variants.variant_id",
            "quantity": "INTEGER - Units purchased",
            "unit_price": "REAL - Unit sale price at time of purchase",
            "total_price": "REAL - Line total (quantity * unit_price)",
        },
        "keywords": ["order item", "units sold", "quantity sold", "bestseller", "most popular", "items ordered"],
    },
    "payments": {
        "description": "Financial payment transactions processing customer orders",
        "columns": {
            "payment_id": "INTEGER PRIMARY KEY - Payment ID",
            "order_id": "INTEGER - FK to orders.order_id",
            "payment_date": "TEXT - Transaction timestamp (YYYY-MM-DD HH:MM:SS)",
            "amount": "REAL - Amount settled in USD",
            "payment_method": "TEXT - Method used",
            "payment_status": "TEXT - 'authorized', 'captured', 'failed', 'refunded'",
            "transaction_reference": "TEXT - External gateway reference ID",
        },
        "keywords": ["payment", "transaction", "settlement", "refund", "gateway", "failed payment", "captured"],
    },
    "shipments": {
        "description": "Logistics delivery records and tracking info for orders",
        "columns": {
            "shipment_id": "INTEGER PRIMARY KEY - Shipment ID",
            "order_id": "INTEGER - FK to orders.order_id",
            "warehouse_id": "INTEGER - FK to warehouses.warehouse_id",
            "carrier": "TEXT - 'FedEx', 'UPS', 'DHL', 'USPS'",
            "tracking_number": "TEXT - Tracking number code",
            "ship_date": "TEXT - Date departed warehouse",
            "estimated_delivery": "TEXT - Target delivery date",
            "actual_delivery": "TEXT - Actual delivery timestamp",
            "shipment_status": "TEXT - 'preparing', 'in_transit', 'delivered', 'delayed', 'returned'",
        },
        "keywords": ["shipment", "shipping", "carrier", "tracking", "delivery", "fedex", "ups", "dhl", "transit time"],
    },
    "reviews": {
        "description": "Product ratings and reviews posted by verified customers",
        "columns": {
            "review_id": "INTEGER PRIMARY KEY - Review ID",
            "product_id": "INTEGER - FK to products.product_id",
            "customer_id": "INTEGER - FK to customers.customer_id",
            "rating": "INTEGER - 1 to 5 star rating",
            "title": "TEXT - Review headline",
            "comment": "TEXT - Customer feedback text",
            "review_date": "TEXT - Review date (YYYY-MM-DD)",
            "is_verified_purchase": "INTEGER - 1 if confirmed buyer, 0 otherwise",
        },
        "keywords": ["review", "rating", "stars", "feedback", "customer satisfaction", "top rated", "lowest rated"],
    },
    "discounts_applied": {
        "description": "Junction table recording coupon usage per order",
        "columns": {
            "discount_id": "INTEGER PRIMARY KEY - Record ID",
            "order_id": "INTEGER - FK to orders.order_id",
            "coupon_id": "INTEGER - FK to coupons.coupon_id",
            "amount_saved": "REAL - Dollar savings applied to the order",
            "applied_at": "TEXT - Timestamp applied",
        },
        "keywords": ["discount applied", "coupon redemption", "amount saved", "promo savings"],
    },
    "support_tickets": {
        "description": "Customer support tickets, issues, and resolution tracking",
        "columns": {
            "ticket_id": "INTEGER PRIMARY KEY - Ticket ID",
            "customer_id": "INTEGER - FK to customers.customer_id",
            "assigned_employee_id": "INTEGER - FK to employees.employee_id",
            "subject": "TEXT - Issue subject line",
            "priority": "TEXT - 'low', 'medium', 'high', 'urgent'",
            "status": "TEXT - 'open', 'in_progress', 'resolved', 'closed'",
            "category": "TEXT - 'Billing', 'Shipping', 'Returns', 'Product Question', 'Technical'",
            "created_at": "TEXT - Ticket creation timestamp",
            "resolved_at": "TEXT - Resolution timestamp",
        },
        "keywords": ["ticket", "support", "helpdesk", "issue", "complaint", "customer service", "resolution time", "open tickets"],
    },
    "ticket_messages": {
        "description": "Conversation message threads between customers and support agents",
        "columns": {
            "message_id": "INTEGER PRIMARY KEY - Message ID",
            "ticket_id": "INTEGER - FK to support_tickets.ticket_id",
            "sender_type": "TEXT - 'customer', 'agent', 'system'",
            "sender_id": "INTEGER - customer_id or employee_id depending on sender_type",
            "message_text": "TEXT - Content of message",
            "created_at": "TEXT - Timestamp sent",
        },
        "keywords": ["message", "thread", "conversation", "reply", "agent response"],
    },
    "audit_logs": {
        "description": "System event audit trail tracking modifications and events",
        "columns": {
            "log_id": "INTEGER PRIMARY KEY - Audit log ID",
            "entity_name": "TEXT - Affected table name ('orders', 'inventory_items', etc.)",
            "entity_id": "INTEGER - Primary key of affected record",
            "action": "TEXT - 'CREATE', 'UPDATE', 'DELETE', 'STATUS_CHANGE', 'PAYMENT_EVENT'",
            "changed_by_employee_id": "INTEGER - FK to employees.employee_id",
            "timestamp": "TEXT - Timestamp of action",
            "details": "TEXT - Description of change",
        },
        "keywords": ["audit", "log", "history", "who changed", "activity", "event log"],
    },
}

# Foreign Key Join Graph (Undirected edges with explicit join ON clauses)
FOREIGN_KEY_EDGES = [
    ("departments", "employees", "departments.department_id = employees.department_id"),
    ("employees", "warehouses", "employees.employee_id = warehouses.manager_employee_id"),
    ("employees", "purchase_orders", "employees.employee_id = purchase_orders.created_by_employee_id"),
    ("employees", "support_tickets", "employees.employee_id = support_tickets.assigned_employee_id"),
    ("employees", "audit_logs", "employees.employee_id = audit_logs.changed_by_employee_id"),
    ("customers", "customer_addresses", "customers.customer_id = customer_addresses.customer_id"),
    ("customers", "orders", "customers.customer_id = orders.customer_id"),
    ("customers", "reviews", "customers.customer_id = reviews.customer_id"),
    ("customers", "support_tickets", "customers.customer_id = support_tickets.customer_id"),
    ("customer_addresses", "orders", "customer_addresses.address_id = orders.shipping_address_id"),
    ("product_categories", "products", "product_categories.category_id = products.category_id"),
    ("products", "product_variants", "products.product_id = product_variants.product_id"),
    ("products", "inventory_items", "products.product_id = inventory_items.product_id"),
    ("products", "purchase_order_items", "products.product_id = purchase_order_items.product_id"),
    ("products", "order_items", "products.product_id = order_items.product_id"),
    ("products", "reviews", "products.product_id = reviews.product_id"),
    ("product_variants", "inventory_items", "product_variants.variant_id = inventory_items.variant_id"),
    ("product_variants", "order_items", "product_variants.variant_id = order_items.variant_id"),
    ("suppliers", "purchase_orders", "suppliers.supplier_id = purchase_orders.supplier_id"),
    ("warehouses", "inventory_items", "warehouses.warehouse_id = inventory_items.warehouse_id"),
    ("warehouses", "purchase_orders", "warehouses.warehouse_id = purchase_orders.warehouse_id"),
    ("warehouses", "shipments", "warehouses.warehouse_id = shipments.warehouse_id"),
    ("purchase_orders", "purchase_order_items", "purchase_orders.po_id = purchase_order_items.po_id"),
    ("orders", "order_items", "orders.order_id = order_items.order_id"),
    ("orders", "payments", "orders.order_id = payments.order_id"),
    ("orders", "shipments", "orders.order_id = shipments.order_id"),
    ("orders", "discounts_applied", "orders.order_id = discounts_applied.order_id"),
    ("coupons", "discounts_applied", "coupons.coupon_id = discounts_applied.coupon_id"),
    ("support_tickets", "ticket_messages", "support_tickets.ticket_id = ticket_messages.ticket_id"),
]


class SchemaCatalog:
    """Provides schema retrieval, semantic routing, and join path inference."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._build_graph()

    def _build_graph(self):
        self.graph: Dict[str, List[Tuple[str, str]]] = {table: [] for table in TABLE_METADATA}
        for t1, t2, on_clause in FOREIGN_KEY_EDGES:
            self.graph[t1].append((t2, on_clause))
            self.graph[t2].append((t1, on_clause))

    def get_table_row_counts(self) -> Dict[str, int]:
        """Queries actual database row counts for all tables."""
        if not os.path.exists(self.db_path):
            return {table: 0 for table in TABLE_METADATA}
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        counts = {}
        for table in TABLE_METADATA:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                counts[table] = cursor.fetchone()[0]
            except Exception:
                counts[table] = 0
        conn.close()
        return counts

    def find_shortest_join_path(self, start: str, end: str) -> Optional[List[Tuple[str, str]]]:
        """
        Uses BFS to find the shortest join path between two tables.
        Returns list of (next_table, on_clause).
        """
        if start == end:
            return []
        
        queue = [[(start, "")]]
        visited = {start}

        while queue:
            path = queue.pop(0)
            current_table = path[-1][0]

            for neighbor, on_clause in self.graph.get(current_table, []):
                if neighbor == end:
                    return path[1:] + [(neighbor, on_clause)]
                if neighbor not in visited:
                    visited.add(neighbor)
                    new_path = list(path)
                    new_path.append((neighbor, on_clause))
                    queue.append(new_path)
        return None

    def identify_relevant_tables(self, natural_language_query: str) -> List[str]:
        """
        Identifies tables directly referenced by query keywords, and adds necessary
        intermediate tables to ensure connectivity for joins.
        """
        q_lower = natural_language_query.lower()
        direct_matches: Set[str] = set()

        for table, meta in TABLE_METADATA.items():
            # Check table name
            if table in q_lower or table.rstrip("s") in q_lower:
                direct_matches.add(table)
                continue
            # Check keywords
            for kw in meta["keywords"]:
                if kw in q_lower:
                    direct_matches.add(table)
                    break
            # Check column names
            for col in meta["columns"]:
                if f" {col} " in f" {q_lower} " or f" {col.replace('_', ' ')} " in f" {q_lower} ":
                    direct_matches.add(table)
                    break

        # Defaults if query is very broad
        if not direct_matches:
            direct_matches = {"orders", "order_items", "products", "customers"}

        # Connect isolated tables via shortest paths in the foreign key graph
        connected_tables = set(direct_matches)
        table_list = list(direct_matches)
        for i in range(len(table_list)):
            for j in range(i + 1, len(table_list)):
                path = self.find_shortest_join_path(table_list[i], table_list[j])
                if path:
                    for hop_table, _ in path:
                        connected_tables.add(hop_table)

        return sorted(list(connected_tables))

    def format_schema_for_prompt(self, relevant_tables: Optional[List[str]] = None) -> str:
        """
        Builds high-density, prompt-optimized schema context for Llama 3.1 8B.
        Includes table schema, column descriptions, and join guidance.
        """
        tables = relevant_tables if relevant_tables else list(TABLE_METADATA.keys())
        lines = ["### DATABASE SCHEMA (SQLite 3):"]

        for table in tables:
            meta = TABLE_METADATA.get(table)
            if not meta:
                continue
            lines.append(f"\nTable `{table}`: {meta['description']}")
            for col_name, col_info in meta["columns"].items():
                lines.append(f"  - `{col_name}`: {col_info}")

        # Relevant join relationships
        lines.append("\n### VERIFIED JOIN RELATIONSHIPS (Use these exact ON conditions):")
        for t1, t2, on_clause in FOREIGN_KEY_EDGES:
            if t1 in tables and t2 in tables:
                lines.append(f"  - {t1} JOIN {t2} ON {on_clause}")

        return "\n".join(lines)


# Global catalog instance
catalog = SchemaCatalog()
