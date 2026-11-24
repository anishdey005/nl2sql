-- Enterprise E-Commerce, Operations & CRM Relational Database Schema (22 Tables)
-- Dialect: SQLite 3

PRAGMA foreign_keys = ON;

-- 1. Departments
CREATE TABLE IF NOT EXISTS departments (
    department_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    code TEXT NOT NULL UNIQUE,
    budget REAL NOT NULL DEFAULT 0.0,
    created_at TEXT NOT NULL DEFAULT (DATETIME('now'))
);

-- 2. Employees
CREATE TABLE IF NOT EXISTS employees (
    employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
    department_id INTEGER NOT NULL,
    manager_id INTEGER,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT,
    job_title TEXT NOT NULL,
    salary REAL NOT NULL,
    hire_date TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('active', 'on_leave', 'terminated')),
    FOREIGN KEY (department_id) REFERENCES departments (department_id),
    FOREIGN KEY (manager_id) REFERENCES employees (employee_id)
);

-- 3. Customers
CREATE TABLE IF NOT EXISTS customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT,
    customer_segment TEXT NOT NULL CHECK (customer_segment IN ('Enterprise', 'SMB', 'Consumer', 'VIP')),
    status TEXT NOT NULL CHECK (status IN ('active', 'inactive', 'suspended')),
    created_at TEXT NOT NULL DEFAULT (DATETIME('now'))
);

-- 4. Customer Addresses
CREATE TABLE IF NOT EXISTS customer_addresses (
    address_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    address_type TEXT NOT NULL CHECK (address_type IN ('billing', 'shipping')),
    street TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    postal_code TEXT NOT NULL,
    country TEXT NOT NULL DEFAULT 'USA',
    is_default INTEGER NOT NULL DEFAULT 1 CHECK (is_default IN (0, 1)),
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id) ON DELETE CASCADE
);

-- 5. Product Categories
CREATE TABLE IF NOT EXISTS product_categories (
    category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_category_id INTEGER,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    FOREIGN KEY (parent_category_id) REFERENCES product_categories (category_id)
);

-- 6. Products
CREATE TABLE IF NOT EXISTS products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    category_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    sku TEXT NOT NULL UNIQUE,
    description TEXT,
    base_price REAL NOT NULL CHECK (base_price >= 0),
    cost_price REAL NOT NULL CHECK (cost_price >= 0),
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_at TEXT NOT NULL DEFAULT (DATETIME('now')),
    FOREIGN KEY (category_id) REFERENCES product_categories (category_id)
);

-- 7. Product Variants
CREATE TABLE IF NOT EXISTS product_variants (
    variant_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    sku TEXT NOT NULL UNIQUE,
    color TEXT,
    size TEXT,
    price_adjustment REAL NOT NULL DEFAULT 0.0,
    stock_quantity INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (product_id) REFERENCES products (product_id) ON DELETE CASCADE
);

-- 8. Suppliers
CREATE TABLE IF NOT EXISTS suppliers (
    supplier_id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    contact_name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    phone TEXT,
    city TEXT NOT NULL,
    country TEXT NOT NULL,
    rating REAL NOT NULL CHECK (rating >= 1.0 AND rating <= 5.0),
    status TEXT NOT NULL CHECK (status IN ('active', 'probation', 'inactive'))
);

-- 9. Warehouses
CREATE TABLE IF NOT EXISTS warehouses (
    warehouse_id INTEGER PRIMARY KEY AUTOINCREMENT,
    manager_employee_id INTEGER,
    name TEXT NOT NULL,
    location_city TEXT NOT NULL,
    state TEXT NOT NULL,
    country TEXT NOT NULL DEFAULT 'USA',
    capacity_units INTEGER NOT NULL,
    FOREIGN KEY (manager_employee_id) REFERENCES employees (employee_id)
);

-- 10. Inventory Items
CREATE TABLE IF NOT EXISTS inventory_items (
    inventory_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    variant_id INTEGER,
    warehouse_id INTEGER NOT NULL,
    quantity_on_hand INTEGER NOT NULL DEFAULT 0,
    reorder_point INTEGER NOT NULL DEFAULT 20,
    last_restocked_at TEXT,
    FOREIGN KEY (product_id) REFERENCES products (product_id),
    FOREIGN KEY (variant_id) REFERENCES product_variants (variant_id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouses (warehouse_id)
);

-- 11. Purchase Orders (To Suppliers)
CREATE TABLE IF NOT EXISTS purchase_orders (
    po_id INTEGER PRIMARY KEY AUTOINCREMENT,
    supplier_id INTEGER NOT NULL,
    warehouse_id INTEGER NOT NULL,
    created_by_employee_id INTEGER NOT NULL,
    order_date TEXT NOT NULL,
    expected_date TEXT,
    total_amount REAL NOT NULL DEFAULT 0.0,
    status TEXT NOT NULL CHECK (status IN ('draft', 'ordered', 'received', 'cancelled')),
    FOREIGN KEY (supplier_id) REFERENCES suppliers (supplier_id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouses (warehouse_id),
    FOREIGN KEY (created_by_employee_id) REFERENCES employees (employee_id)
);

-- 12. Purchase Order Items
CREATE TABLE IF NOT EXISTS purchase_order_items (
    po_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    po_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    quantity_ordered INTEGER NOT NULL,
    unit_cost REAL NOT NULL,
    quantity_received INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (po_id) REFERENCES purchase_orders (po_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products (product_id)
);

-- 13. Coupons & Promotions
CREATE TABLE IF NOT EXISTS coupons (
    coupon_id INTEGER PRIMARY KEY AUTOINCREMENT,
    code TEXT NOT NULL UNIQUE,
    discount_type TEXT NOT NULL CHECK (discount_type IN ('percentage', 'fixed_amount')),
    discount_value REAL NOT NULL,
    min_order_amount REAL NOT NULL DEFAULT 0.0,
    start_date TEXT NOT NULL,
    end_date TEXT NOT NULL,
    max_uses INTEGER NOT NULL DEFAULT 500,
    times_used INTEGER NOT NULL DEFAULT 0,
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1))
);

-- 14. Customer Orders
CREATE TABLE IF NOT EXISTS orders (
    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    shipping_address_id INTEGER,
    order_date TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('pending', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded')),
    subtotal REAL NOT NULL,
    tax_amount REAL NOT NULL DEFAULT 0.0,
    shipping_fee REAL NOT NULL DEFAULT 0.0,
    discount_amount REAL NOT NULL DEFAULT 0.0,
    total_amount REAL NOT NULL,
    payment_method TEXT NOT NULL CHECK (payment_method IN ('credit_card', 'paypal', 'bank_transfer', 'apple_pay')),
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id),
    FOREIGN KEY (shipping_address_id) REFERENCES customer_addresses (address_id)
);

-- 15. Order Items
CREATE TABLE IF NOT EXISTS order_items (
    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    product_id INTEGER NOT NULL,
    variant_id INTEGER,
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    unit_price REAL NOT NULL CHECK (unit_price >= 0),
    total_price REAL NOT NULL CHECK (total_price >= 0),
    FOREIGN KEY (order_id) REFERENCES orders (order_id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products (product_id),
    FOREIGN KEY (variant_id) REFERENCES product_variants (variant_id)
);

-- 16. Payments
CREATE TABLE IF NOT EXISTS payments (
    payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    payment_date TEXT NOT NULL,
    amount REAL NOT NULL,
    payment_method TEXT NOT NULL,
    payment_status TEXT NOT NULL CHECK (payment_status IN ('authorized', 'captured', 'failed', 'refunded')),
    transaction_reference TEXT UNIQUE,
    FOREIGN KEY (order_id) REFERENCES orders (order_id)
);

-- 17. Shipments
CREATE TABLE IF NOT EXISTS shipments (
    shipment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    warehouse_id INTEGER NOT NULL,
    carrier TEXT NOT NULL CHECK (carrier IN ('FedEx', 'UPS', 'DHL', 'USPS')),
    tracking_number TEXT UNIQUE,
    ship_date TEXT,
    estimated_delivery TEXT,
    actual_delivery TEXT,
    shipment_status TEXT NOT NULL CHECK (shipment_status IN ('preparing', 'in_transit', 'delivered', 'delayed', 'returned')),
    FOREIGN KEY (order_id) REFERENCES orders (order_id),
    FOREIGN KEY (warehouse_id) REFERENCES warehouses (warehouse_id)
);

-- 18. Product Reviews
CREATE TABLE IF NOT EXISTS reviews (
    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    title TEXT,
    comment TEXT,
    review_date TEXT NOT NULL,
    is_verified_purchase INTEGER NOT NULL DEFAULT 1 CHECK (is_verified_purchase IN (0, 1)),
    FOREIGN KEY (product_id) REFERENCES products (product_id),
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id)
);

-- 19. Discounts Applied
CREATE TABLE IF NOT EXISTS discounts_applied (
    discount_id INTEGER PRIMARY KEY AUTOINCREMENT,
    order_id INTEGER NOT NULL,
    coupon_id INTEGER NOT NULL,
    amount_saved REAL NOT NULL,
    applied_at TEXT NOT NULL DEFAULT (DATETIME('now')),
    FOREIGN KEY (order_id) REFERENCES orders (order_id) ON DELETE CASCADE,
    FOREIGN KEY (coupon_id) REFERENCES coupons (coupon_id)
);

-- 20. Support Tickets
CREATE TABLE IF NOT EXISTS support_tickets (
    ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    assigned_employee_id INTEGER,
    subject TEXT NOT NULL,
    priority TEXT NOT NULL CHECK (priority IN ('low', 'medium', 'high', 'urgent')),
    status TEXT NOT NULL CHECK (status IN ('open', 'in_progress', 'resolved', 'closed')),
    category TEXT NOT NULL CHECK (category IN ('Billing', 'Shipping', 'Returns', 'Product Question', 'Technical')),
    created_at TEXT NOT NULL,
    resolved_at TEXT,
    FOREIGN KEY (customer_id) REFERENCES customers (customer_id),
    FOREIGN KEY (assigned_employee_id) REFERENCES employees (employee_id)
);

-- 21. Support Ticket Messages
CREATE TABLE IF NOT EXISTS ticket_messages (
    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticket_id INTEGER NOT NULL,
    sender_type TEXT NOT NULL CHECK (sender_type IN ('customer', 'agent', 'system')),
    sender_id INTEGER NOT NULL,
    message_text TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (ticket_id) REFERENCES support_tickets (ticket_id) ON DELETE CASCADE
);

-- 22. Audit Logs
CREATE TABLE IF NOT EXISTS audit_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_name TEXT NOT NULL,
    entity_id INTEGER NOT NULL,
    action TEXT NOT NULL CHECK (action IN ('CREATE', 'UPDATE', 'DELETE', 'STATUS_CHANGE', 'PAYMENT_EVENT')),
    changed_by_employee_id INTEGER,
    timestamp TEXT NOT NULL DEFAULT (DATETIME('now')),
    details TEXT,
    FOREIGN KEY (changed_by_employee_id) REFERENCES employees (employee_id)
);

-- Indexes for high-performance join and aggregation queries
CREATE INDEX IF NOT EXISTS idx_orders_customer ON orders (customer_id);
CREATE INDEX IF NOT EXISTS idx_orders_date ON orders (order_date);
CREATE INDEX IF NOT EXISTS idx_orders_status ON orders (status);
CREATE INDEX IF NOT EXISTS idx_order_items_order ON order_items (order_id);
CREATE INDEX IF NOT EXISTS idx_order_items_product ON order_items (product_id);
CREATE INDEX IF NOT EXISTS idx_inventory_product ON inventory_items (product_id);
CREATE INDEX IF NOT EXISTS idx_inventory_warehouse ON inventory_items (warehouse_id);
CREATE INDEX IF NOT EXISTS idx_reviews_product ON reviews (product_id);
CREATE INDEX IF NOT EXISTS idx_tickets_customer ON support_tickets (customer_id);
CREATE INDEX IF NOT EXISTS idx_tickets_assigned ON support_tickets (assigned_employee_id);
CREATE INDEX IF NOT EXISTS idx_employees_dept ON employees (department_id);
CREATE INDEX IF NOT EXISTS idx_products_category ON products (category_id);
