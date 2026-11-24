"""
Generates and verifies 105 enterprise benchmark queries across Easy, Medium, and Hard complexities.
Validates all ground-truth SQL statements against the enterprise database.
"""

import json
import os
import sqlite3

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
DB_PATH = os.path.join(PROJECT_ROOT, "data", "enterprise.db")
OUTPUT_PATH = os.path.join(CURRENT_DIR, "benchmark_queries.json")

# 105 Curated Business Queries with Ground-Truth SQL
QUERIES = [
    # --- EASY QUERIES (1 - 35) ---
    {
        "id": "Q001",
        "category": "Sales",
        "difficulty": "Easy",
        "question": "How many total orders are in the database?",
        "ground_truth_sql": "SELECT COUNT(*) AS total_orders FROM orders;"
    },
    {
        "id": "Q002",
        "category": "Customers",
        "difficulty": "Easy",
        "question": "List all customers in the VIP customer segment",
        "ground_truth_sql": "SELECT customer_id, first_name, last_name, email FROM customers WHERE customer_segment = 'VIP';"
    },
    {
        "id": "Q003",
        "category": "Products",
        "difficulty": "Easy",
        "question": "What is the average base price of all active products?",
        "ground_truth_sql": "SELECT ROUND(AVG(base_price), 2) AS avg_price FROM products WHERE is_active = 1;"
    },
    {
        "id": "Q004",
        "category": "HR",
        "difficulty": "Easy",
        "question": "Show all employees with a salary greater than 100000",
        "ground_truth_sql": "SELECT employee_id, first_name, last_name, job_title, salary FROM employees WHERE salary > 100000 ORDER BY salary DESC;"
    },
    {
        "id": "Q005",
        "category": "Suppliers",
        "difficulty": "Easy",
        "question": "List active suppliers with a rating of 4.8 or higher",
        "ground_truth_sql": "SELECT supplier_id, name, country, rating FROM suppliers WHERE status = 'active' AND rating >= 4.8 ORDER BY rating DESC;"
    },
    {
        "id": "Q006",
        "category": "Inventory",
        "difficulty": "Easy",
        "question": "Find all inventory records where quantity on hand is less than or equal to 20",
        "ground_truth_sql": "SELECT inventory_id, product_id, warehouse_id, quantity_on_hand, reorder_point FROM inventory_items WHERE quantity_on_hand <= 20 ORDER BY quantity_on_hand ASC;"
    },
    {
        "id": "Q007",
        "category": "Support",
        "difficulty": "Easy",
        "question": "Count the number of open support tickets",
        "ground_truth_sql": "SELECT COUNT(*) AS open_tickets_count FROM support_tickets WHERE status = 'open';"
    },
    {
        "id": "Q008",
        "category": "Coupons",
        "difficulty": "Easy",
        "question": "List active coupons that offer percentage discounts",
        "ground_truth_sql": "SELECT code, discount_value, min_order_amount FROM coupons WHERE is_active = 1 AND discount_type = 'percentage';"
    },
    {
        "id": "Q009",
        "category": "Warehouses",
        "difficulty": "Easy",
        "question": "What is the total storage capacity across all warehouses?",
        "ground_truth_sql": "SELECT SUM(capacity_units) AS total_capacity FROM warehouses;"
    },
    {
        "id": "Q010",
        "category": "Sales",
        "difficulty": "Easy",
        "question": "Count the number of delivered orders",
        "ground_truth_sql": "SELECT COUNT(*) AS delivered_count FROM orders WHERE status = 'delivered';"
    },
    {
        "id": "Q011",
        "category": "Customers",
        "difficulty": "Easy",
        "question": "How many active customers are there?",
        "ground_truth_sql": "SELECT COUNT(*) AS active_customers FROM customers WHERE status = 'active';"
    },
    {
        "id": "Q012",
        "category": "Products",
        "difficulty": "Easy",
        "question": "Find the top 5 most expensive products by base price",
        "ground_truth_sql": "SELECT product_id, name, base_price FROM products ORDER BY base_price DESC LIMIT 5;"
    },
    {
        "id": "Q013",
        "category": "HR",
        "difficulty": "Easy",
        "question": "List all departments and their annual budgets",
        "ground_truth_sql": "SELECT name, code, budget FROM departments ORDER BY budget DESC;"
    },
    {
        "id": "Q014",
        "category": "Suppliers",
        "difficulty": "Easy",
        "question": "Count suppliers grouped by country",
        "ground_truth_sql": "SELECT country, COUNT(*) AS supplier_count FROM suppliers GROUP BY country ORDER BY supplier_count DESC;"
    },
    {
        "id": "Q015",
        "category": "Support",
        "difficulty": "Easy",
        "question": "Count support tickets grouped by priority",
        "ground_truth_sql": "SELECT priority, COUNT(*) AS count FROM support_tickets GROUP BY priority ORDER BY count DESC;"
    },
    {
        "id": "Q016",
        "category": "Reviews",
        "difficulty": "Easy",
        "question": "How many 5-star reviews have been submitted?",
        "ground_truth_sql": "SELECT COUNT(*) AS five_star_reviews FROM reviews WHERE rating = 5;"
    },
    {
        "id": "Q017",
        "category": "Logistics",
        "difficulty": "Easy",
        "question": "Count shipments handled by each carrier",
        "ground_truth_sql": "SELECT carrier, COUNT(*) AS total_shipments FROM shipments GROUP BY carrier ORDER BY total_shipments DESC;"
    },
    {
        "id": "Q018",
        "category": "Sales",
        "difficulty": "Easy",
        "question": "What is the maximum order total amount?",
        "ground_truth_sql": "SELECT MAX(total_amount) AS max_order_amount FROM orders;"
    },
    {
        "id": "Q019",
        "category": "Products",
        "difficulty": "Easy",
        "question": "List all products in category 1",
        "ground_truth_sql": "SELECT product_id, name, sku, base_price FROM products WHERE category_id = 1;"
    },
    {
        "id": "Q020",
        "category": "Procurement",
        "difficulty": "Easy",
        "question": "List purchase orders with total amount greater than 50000",
        "ground_truth_sql": "SELECT po_id, supplier_id, order_date, total_amount, status FROM purchase_orders WHERE total_amount > 50000 ORDER BY total_amount DESC;"
    },
    {
        "id": "Q021",
        "category": "Customers",
        "difficulty": "Easy",
        "question": "Count customers in each segment",
        "ground_truth_sql": "SELECT customer_segment, COUNT(*) AS count FROM customers GROUP BY customer_segment ORDER BY count DESC;"
    },
    {
        "id": "Q022",
        "category": "Audit",
        "difficulty": "Easy",
        "question": "Show the 10 most recent audit log records",
        "ground_truth_sql": "SELECT log_id, entity_name, action, timestamp, details FROM audit_logs ORDER BY timestamp DESC LIMIT 10;"
    },
    {
        "id": "Q023",
        "category": "Payments",
        "difficulty": "Easy",
        "question": "Count payments by payment status",
        "ground_truth_sql": "SELECT payment_status, COUNT(*) AS count, ROUND(SUM(amount), 2) AS total_settled FROM payments GROUP BY payment_status;"
    },
    {
        "id": "Q024",
        "category": "Logistics",
        "difficulty": "Easy",
        "question": "List all shipments that have delivered status",
        "ground_truth_sql": "SELECT shipment_id, order_id, carrier, tracking_number, actual_delivery FROM shipments WHERE shipment_status = 'delivered' LIMIT 10;"
    },
    {
        "id": "Q025",
        "category": "Coupons",
        "difficulty": "Easy",
        "question": "Find the top 3 most used coupon codes",
        "ground_truth_sql": "SELECT code, discount_type, discount_value, times_used FROM coupons ORDER BY times_used DESC LIMIT 3;"
    },
    {
        "id": "Q026",
        "category": "Sales",
        "difficulty": "Easy",
        "question": "What is the average order total for delivered orders?",
        "ground_truth_sql": "SELECT ROUND(AVG(total_amount), 2) AS avg_delivered_total FROM orders WHERE status = 'delivered';"
    },
    {
        "id": "Q027",
        "category": "HR",
        "difficulty": "Easy",
        "question": "How many employees are in department 1?",
        "ground_truth_sql": "SELECT COUNT(*) AS employee_count FROM employees WHERE department_id = 1;"
    },
    {
        "id": "Q028",
        "category": "Inventory",
        "difficulty": "Easy",
        "question": "What is the total quantity of inventory units on hand across all warehouses?",
        "ground_truth_sql": "SELECT SUM(quantity_on_hand) AS total_stock FROM inventory_items;"
    },
    {
        "id": "Q029",
        "category": "Products",
        "difficulty": "Easy",
        "question": "Find products with profit margin (base_price minus cost_price) greater than 500",
        "ground_truth_sql": "SELECT product_id, name, base_price, cost_price, ROUND(base_price - cost_price, 2) AS margin FROM products WHERE (base_price - cost_price) > 500 ORDER BY margin DESC;"
    },
    {
        "id": "Q030",
        "category": "Support",
        "difficulty": "Easy",
        "question": "Count tickets by category",
        "ground_truth_sql": "SELECT category, COUNT(*) AS count FROM support_tickets GROUP BY category ORDER BY count DESC;"
    },
    {
        "id": "Q031",
        "category": "Reviews",
        "difficulty": "Easy",
        "question": "What is the overall average rating across all reviews?",
        "ground_truth_sql": "SELECT ROUND(AVG(rating), 2) AS average_rating FROM reviews;"
    },
    {
        "id": "Q032",
        "category": "Customers",
        "difficulty": "Easy",
        "question": "List all customer addresses located in California (CA)",
        "ground_truth_sql": "SELECT address_id, customer_id, street, city, postal_code FROM customer_addresses WHERE state = 'CA';"
    },
    {
        "id": "Q033",
        "category": "Logistics",
        "difficulty": "Easy",
        "question": "List warehouses in Texas (TX)",
        "ground_truth_sql": "SELECT warehouse_id, name, location_city, capacity_units FROM warehouses WHERE state = 'TX';"
    },
    {
        "id": "Q034",
        "category": "Payments",
        "difficulty": "Easy",
        "question": "What is the total revenue captured through credit card payments?",
        "ground_truth_sql": "SELECT ROUND(SUM(amount), 2) AS total_credit_card_revenue FROM payments WHERE payment_method = 'credit_card' AND payment_status = 'captured';"
    },
    {
        "id": "Q035",
        "category": "Procurement",
        "difficulty": "Easy",
        "question": "Count purchase orders by status",
        "ground_truth_sql": "SELECT status, COUNT(*) AS count, ROUND(SUM(total_amount), 2) AS total_value FROM purchase_orders GROUP BY status;"
    },

    # --- MEDIUM QUERIES (36 - 75) ---
    {
        "id": "Q036",
        "category": "Sales",
        "difficulty": "Medium",
        "question": "Show total sales revenue and number of orders for each customer segment",
        "ground_truth_sql": (
            "SELECT c.customer_segment, COUNT(o.order_id) AS total_orders, "
            "ROUND(SUM(o.total_amount), 2) AS total_revenue "
            "FROM customers c "
            "JOIN orders o ON c.customer_id = o.customer_id "
            "WHERE o.status != 'cancelled' "
            "GROUP BY c.customer_segment "
            "ORDER BY total_revenue DESC;"
        )
    },
    {
        "id": "Q037",
        "category": "Products",
        "difficulty": "Medium",
        "question": "List product categories with total number of products in each category",
        "ground_truth_sql": (
            "SELECT pc.name AS category_name, COUNT(p.product_id) AS product_count "
            "FROM product_categories pc "
            "JOIN products p ON pc.category_id = p.category_id "
            "GROUP BY pc.category_id, pc.name "
            "ORDER BY product_count DESC;"
        )
    },
    {
        "id": "Q038",
        "category": "HR",
        "difficulty": "Medium",
        "question": "Show department names with their average employee salary and employee count",
        "ground_truth_sql": (
            "SELECT d.name AS department, COUNT(e.employee_id) AS staff_count, "
            "ROUND(AVG(e.salary), 2) AS avg_salary "
            "FROM departments d "
            "JOIN employees e ON d.department_id = e.department_id "
            "GROUP BY d.department_id, d.name "
            "ORDER BY avg_salary DESC;"
        )
    },
    {
        "id": "Q039",
        "category": "Inventory",
        "difficulty": "Medium",
        "question": "Show product name, warehouse name, and stock quantity for products with less than 25 units",
        "ground_truth_sql": (
            "SELECT p.name AS product_name, w.name AS warehouse_name, i.quantity_on_hand "
            "FROM inventory_items i "
            "JOIN products p ON i.product_id = p.product_id "
            "JOIN warehouses w ON i.warehouse_id = w.warehouse_id "
            "WHERE i.quantity_on_hand < 25 "
            "ORDER BY i.quantity_on_hand ASC;"
        )
    },
    {
        "id": "Q040",
        "category": "Reviews",
        "difficulty": "Medium",
        "question": "Find average review rating and review count for each product having at least 3 reviews",
        "ground_truth_sql": (
            "SELECT p.name AS product_name, ROUND(AVG(r.rating), 2) AS avg_rating, COUNT(r.review_id) AS review_count "
            "FROM products p "
            "JOIN reviews r ON p.product_id = r.product_id "
            "GROUP BY p.product_id, p.name "
            "HAVING review_count >= 3 "
            "ORDER BY avg_rating DESC;"
        )
    },
    {
        "id": "Q041",
        "category": "Sales",
        "difficulty": "Medium",
        "question": "List top 5 products by total units sold",
        "ground_truth_sql": (
            "SELECT p.product_id, p.name AS product_name, SUM(oi.quantity) AS total_units_sold "
            "FROM products p "
            "JOIN order_items oi ON p.product_id = oi.product_id "
            "GROUP BY p.product_id, p.name "
            "ORDER BY total_units_sold DESC "
            "LIMIT 5;"
        )
    },
    {
        "id": "Q042",
        "category": "Logistics",
        "difficulty": "Medium",
        "question": "Show warehouse name, carrier, and count of shipments dispatched",
        "ground_truth_sql": (
            "SELECT w.name AS warehouse_name, s.carrier, COUNT(s.shipment_id) AS shipment_count "
            "FROM shipments s "
            "JOIN warehouses w ON s.warehouse_id = w.warehouse_id "
            "GROUP BY w.name, s.carrier "
            "ORDER BY warehouse_name, shipment_count DESC;"
        )
    },
    {
        "id": "Q043",
        "category": "Support",
        "difficulty": "Medium",
        "question": "List support agents and the number of tickets assigned to each",
        "ground_truth_sql": (
            "SELECT e.first_name || ' ' || e.last_name AS agent_name, COUNT(st.ticket_id) AS ticket_count "
            "FROM employees e "
            "JOIN support_tickets st ON e.employee_id = st.assigned_employee_id "
            "GROUP BY e.employee_id, agent_name "
            "ORDER BY ticket_count DESC;"
        )
    },
    {
        "id": "Q044",
        "category": "Procurement",
        "difficulty": "Medium",
        "question": "Show total purchase order spending per supplier for received orders",
        "ground_truth_sql": (
            "SELECT s.name AS supplier_name, s.country, ROUND(SUM(po.total_amount), 2) AS total_procured "
            "FROM suppliers s "
            "JOIN purchase_orders po ON s.supplier_id = po.supplier_id "
            "WHERE po.status = 'received' "
            "GROUP BY s.supplier_id, s.name, s.country "
            "ORDER BY total_procured DESC;"
        )
    },
    {
        "id": "Q045",
        "category": "Coupons",
        "difficulty": "Medium",
        "question": "Show coupon code and total amount saved across all orders",
        "ground_truth_sql": (
            "SELECT c.code, COUNT(da.order_id) AS times_applied, ROUND(SUM(da.amount_saved), 2) AS total_savings "
            "FROM coupons c "
            "JOIN discounts_applied da ON c.coupon_id = da.coupon_id "
            "GROUP BY c.coupon_id, c.code "
            "ORDER BY total_savings DESC;"
        )
    },
    {
        "id": "Q046",
        "category": "Sales",
        "difficulty": "Medium",
        "question": "Calculate monthly revenue trend for delivered and shipped orders",
        "ground_truth_sql": (
            "SELECT strftime('%Y-%m', order_date) AS order_month, "
            "ROUND(SUM(total_amount), 2) AS monthly_revenue, "
            "COUNT(order_id) AS order_count "
            "FROM orders "
            "WHERE status IN ('delivered', 'shipped') "
            "GROUP BY order_month "
            "ORDER BY order_month ASC;"
        )
    },
    {
        "id": "Q047",
        "category": "HR",
        "difficulty": "Medium",
        "question": "Show each employee name alongside their direct manager's name",
        "ground_truth_sql": (
            "SELECT e.first_name || ' ' || e.last_name AS employee_name, e.job_title, "
            "m.first_name || ' ' || m.last_name AS manager_name "
            "FROM employees e "
            "JOIN employees m ON e.manager_id = m.employee_id "
            "ORDER BY manager_name, employee_name;"
        )
    },
    {
        "id": "Q048",
        "category": "Customers",
        "difficulty": "Medium",
        "question": "Find customers who have placed 3 or more orders",
        "ground_truth_sql": (
            "SELECT c.customer_id, c.first_name, c.last_name, COUNT(o.order_id) AS order_count "
            "FROM customers c "
            "JOIN orders o ON c.customer_id = o.customer_id "
            "GROUP BY c.customer_id, c.first_name, c.last_name "
            "HAVING order_count >= 3 "
            "ORDER BY order_count DESC;"
        )
    },
    {
        "id": "Q049",
        "category": "Products",
        "difficulty": "Medium",
        "question": "Show total sales revenue generated by each product category",
        "ground_truth_sql": (
            "SELECT pc.name AS category_name, ROUND(SUM(oi.total_price), 2) AS category_revenue "
            "FROM product_categories pc "
            "JOIN products p ON pc.category_id = p.category_id "
            "JOIN order_items oi ON p.product_id = oi.product_id "
            "GROUP BY pc.category_id, pc.name "
            "ORDER BY category_revenue DESC;"
        )
    },
    {
        "id": "Q050",
        "category": "Logistics",
        "difficulty": "Medium",
        "question": "List warehouse names and the warehouse manager's name",
        "ground_truth_sql": (
            "SELECT w.name AS warehouse_name, w.location_city, "
            "e.first_name || ' ' || e.last_name AS manager_name "
            "FROM warehouses w "
            "JOIN employees e ON w.manager_employee_id = e.employee_id;"
        )
    },
    {
        "id": "Q051",
        "category": "Sales",
        "difficulty": "Medium",
        "question": "List the top 5 customers by total spending",
        "ground_truth_sql": (
            "SELECT c.customer_id, c.first_name, c.last_name, ROUND(SUM(o.total_amount), 2) AS total_spent "
            "FROM customers c "
            "JOIN orders o ON c.customer_id = o.customer_id "
            "WHERE o.status != 'cancelled' "
            "GROUP BY c.customer_id, c.first_name, c.last_name "
            "ORDER BY total_spent DESC "
            "LIMIT 5;"
        )
    },
    {
        "id": "Q052",
        "category": "Support",
        "difficulty": "Medium",
        "question": "Find customers who have submitted urgent priority support tickets",
        "ground_truth_sql": (
            "SELECT DISTINCT c.customer_id, c.first_name, c.last_name, c.email, st.subject "
            "FROM customers c "
            "JOIN support_tickets st ON c.customer_id = st.customer_id "
            "WHERE st.priority = 'urgent';"
        )
    },
    {
        "id": "Q053",
        "category": "Procurement",
        "difficulty": "Medium",
        "question": "Show purchase orders received by each warehouse with total amount",
        "ground_truth_sql": (
            "SELECT w.name AS warehouse_name, COUNT(po.po_id) AS total_pos, "
            "ROUND(SUM(po.total_amount), 2) AS total_procured_value "
            "FROM warehouses w "
            "JOIN purchase_orders po ON w.warehouse_id = po.warehouse_id "
            "WHERE po.status = 'received' "
            "GROUP BY w.warehouse_id, w.name "
            "ORDER BY total_procured_value DESC;"
        )
    },
    {
        "id": "Q054",
        "category": "Payments",
        "difficulty": "Medium",
        "question": "Show average payment amount per payment method for captured payments",
        "ground_truth_sql": (
            "SELECT payment_method, COUNT(*) AS txn_count, ROUND(AVG(amount), 2) AS avg_amount "
            "FROM payments "
            "WHERE payment_status = 'captured' "
            "GROUP BY payment_method "
            "ORDER BY avg_amount DESC;"
        )
    },
    {
        "id": "Q055",
        "category": "Inventory",
        "difficulty": "Medium",
        "question": "Show warehouses and their total inventory units across all products",
        "ground_truth_sql": (
            "SELECT w.name AS warehouse_name, SUM(i.quantity_on_hand) AS total_units_stored "
            "FROM warehouses w "
            "JOIN inventory_items i ON w.warehouse_id = i.warehouse_id "
            "GROUP BY w.warehouse_id, w.name "
            "ORDER BY total_units_stored DESC;"
        )
    },
    {
        "id": "Q056",
        "category": "Products",
        "difficulty": "Medium",
        "question": "Show count of product variants available for each product",
        "ground_truth_sql": (
            "SELECT p.name AS product_name, COUNT(pv.variant_id) AS variant_count "
            "FROM products p "
            "JOIN product_variants pv ON p.product_id = pv.product_id "
            "GROUP BY p.product_id, p.name "
            "ORDER BY variant_count DESC, product_name ASC "
            "LIMIT 10;"
        )
    },
    {
        "id": "Q057",
        "category": "Sales",
        "difficulty": "Medium",
        "question": "Find average order value per payment method",
        "ground_truth_sql": (
            "SELECT payment_method, ROUND(AVG(total_amount), 2) AS avg_order_value "
            "FROM orders "
            "WHERE status = 'delivered' "
            "GROUP BY payment_method "
            "ORDER BY avg_order_value DESC;"
        )
    },
    {
        "id": "Q058",
        "category": "HR",
        "difficulty": "Medium",
        "question": "Show total salary budget spent versus department allocated budget",
        "ground_truth_sql": (
            "SELECT d.name AS department_name, d.budget AS allocated_budget, "
            "ROUND(SUM(e.salary), 2) AS actual_salary_spend, "
            "ROUND(d.budget - SUM(e.salary), 2) AS remaining_budget "
            "FROM departments d "
            "JOIN employees e ON d.department_id = e.department_id "
            "GROUP BY d.department_id, d.name, d.budget "
            "ORDER BY remaining_budget ASC;"
        )
    },
    {
        "id": "Q059",
        "category": "Support",
        "difficulty": "Medium",
        "question": "Count messages per support ticket for tickets with more than 2 messages",
        "ground_truth_sql": (
            "SELECT st.ticket_id, st.subject, COUNT(tm.message_id) AS msg_count "
            "FROM support_tickets st "
            "JOIN ticket_messages tm ON st.ticket_id = tm.ticket_id "
            "GROUP BY st.ticket_id, st.subject "
            "HAVING msg_count > 2 "
            "ORDER BY msg_count DESC;"
        )
    },
    {
        "id": "Q060",
        "category": "Customers",
        "difficulty": "Medium",
        "question": "Show customers and the city of their primary shipping address",
        "ground_truth_sql": (
            "SELECT c.customer_id, c.first_name, c.last_name, ca.city, ca.state "
            "FROM customers c "
            "JOIN customer_addresses ca ON c.customer_id = ca.customer_id "
            "WHERE ca.address_type = 'shipping' AND ca.is_default = 1 "
            "LIMIT 10;"
        )
    },
    {
        "id": "Q061",
        "category": "Reviews",
        "difficulty": "Medium",
        "question": "List verified reviews for products in the Computers & Laptops category",
        "ground_truth_sql": (
            "SELECT p.name AS product_name, r.rating, r.title, r.review_date "
            "FROM reviews r "
            "JOIN products p ON r.product_id = p.product_id "
            "JOIN product_categories pc ON p.category_id = pc.category_id "
            "WHERE pc.name = 'Computers & Laptops' AND r.is_verified_purchase = 1 "
            "ORDER BY r.review_date DESC "
            "LIMIT 10;"
        )
    },
    {
        "id": "Q062",
        "category": "Audit",
        "difficulty": "Medium",
        "question": "Show audit logs with the employee name who performed the change",
        "ground_truth_sql": (
            "SELECT al.log_id, al.entity_name, al.action, al.timestamp, "
            "e.first_name || ' ' || e.last_name AS employee_name "
            "FROM audit_logs al "
            "JOIN employees e ON al.changed_by_employee_id = e.employee_id "
            "ORDER BY al.timestamp DESC "
            "LIMIT 10;"
        )
    },
    {
        "id": "Q063",
        "category": "Procurement",
        "difficulty": "Medium",
        "question": "Show suppliers and the employee who created purchase orders to them",
        "ground_truth_sql": (
            "SELECT DISTINCT s.name AS supplier_name, "
            "e.first_name || ' ' || e.last_name AS procurement_specialist "
            "FROM purchase_orders po "
            "JOIN suppliers s ON po.supplier_id = s.supplier_id "
            "JOIN employees e ON po.created_by_employee_id = e.employee_id "
            "ORDER BY supplier_name;"
        )
    },
    {
        "id": "Q064",
        "category": "Sales",
        "difficulty": "Medium",
        "question": "Show top 5 states by total order spending",
        "ground_truth_sql": (
            "SELECT ca.state, ROUND(SUM(o.total_amount), 2) AS state_revenue, COUNT(o.order_id) AS order_count "
            "FROM orders o "
            "JOIN customer_addresses ca ON o.shipping_address_id = ca.address_id "
            "WHERE o.status != 'cancelled' "
            "GROUP BY ca.state "
            "ORDER BY state_revenue DESC "
            "LIMIT 5;"
        )
    },
    {
        "id": "Q065",
        "category": "Inventory",
        "difficulty": "Medium",
        "question": "Find inventory items that have never been restocked or have null restock dates",
        "ground_truth_sql": (
            "SELECT p.name AS product_name, w.name AS warehouse_name, i.quantity_on_hand "
            "FROM inventory_items i "
            "JOIN products p ON i.product_id = p.product_id "
            "JOIN warehouses w ON i.warehouse_id = w.warehouse_id "
            "WHERE i.last_restocked_at IS NULL;"
        )
    },
    {
        "id": "Q066",
        "category": "Products",
        "difficulty": "Medium",
        "question": "List products where total unit sales exceed 10 units",
        "ground_truth_sql": (
            "SELECT p.name AS product_name, SUM(oi.quantity) AS total_sold "
            "FROM products p "
            "JOIN order_items oi ON p.product_id = oi.product_id "
            "GROUP BY p.product_id, p.name "
            "HAVING total_sold > 10 "
            "ORDER BY total_sold DESC;"
        )
    },
    {
        "id": "Q067",
        "category": "HR",
        "difficulty": "Medium",
        "question": "Find employees who were hired in 2023",
        "ground_truth_sql": (
            "SELECT employee_id, first_name, last_name, job_title, hire_date "
            "FROM employees "
            "WHERE hire_date LIKE '2023%' "
            "ORDER BY hire_date ASC;"
        )
    },
    {
        "id": "Q068",
        "category": "Support",
        "difficulty": "Medium",
        "question": "Show resolved tickets and their assigned employee names",
        "ground_truth_sql": (
            "SELECT st.ticket_id, st.subject, st.category, "
            "e.first_name || ' ' || e.last_name AS agent_name, st.resolved_at "
            "FROM support_tickets st "
            "JOIN employees e ON st.assigned_employee_id = e.employee_id "
            "WHERE st.status = 'resolved' "
            "LIMIT 10;"
        )
    },
    {
        "id": "Q069",
        "category": "Sales",
        "difficulty": "Medium",
        "question": "Show total discounts granted per customer segment",
        "ground_truth_sql": (
            "SELECT c.customer_segment, ROUND(SUM(o.discount_amount), 2) AS total_discount_given "
            "FROM customers c "
            "JOIN orders o ON c.customer_id = o.customer_id "
            "GROUP BY c.customer_segment "
            "ORDER BY total_discount_given DESC;"
        )
    },
    {
        "id": "Q070",
        "category": "Procurement",
        "difficulty": "Medium",
        "question": "Show products ordered through purchase orders and total quantity procured",
        "ground_truth_sql": (
            "SELECT p.name AS product_name, SUM(poi.quantity_ordered) AS total_procured_units "
            "FROM purchase_order_items poi "
            "JOIN products p ON poi.product_id = p.product_id "
            "GROUP BY p.product_id, p.name "
            "ORDER BY total_procured_units DESC "
            "LIMIT 10;"
        )
    },
    {
        "id": "Q071",
        "category": "Logistics",
        "difficulty": "Medium",
        "question": "List delivered shipments with order total amounts",
        "ground_truth_sql": (
            "SELECT s.tracking_number, s.carrier, s.actual_delivery, o.total_amount "
            "FROM shipments s "
            "JOIN orders o ON s.order_id = o.order_id "
            "WHERE s.shipment_status = 'delivered' "
            "ORDER BY o.total_amount DESC "
            "LIMIT 10;"
        )
    },
    {
        "id": "Q072",
        "category": "Customers",
        "difficulty": "Medium",
        "question": "Find customers who have submitted at least one product review",
        "ground_truth_sql": (
            "SELECT DISTINCT c.customer_id, c.first_name, c.last_name, c.email "
            "FROM customers c "
            "JOIN reviews r ON c.customer_id = r.customer_id "
            "LIMIT 10;"
        )
    },
    {
        "id": "Q073",
        "category": "Coupons",
        "difficulty": "Medium",
        "question": "List orders that used a coupon and show amount saved",
        "ground_truth_sql": (
            "SELECT da.order_id, c.code, da.amount_saved, o.total_amount "
            "FROM discounts_applied da "
            "JOIN coupons c ON da.coupon_id = c.coupon_id "
            "JOIN orders o ON da.order_id = o.order_id "
            "ORDER BY da.amount_saved DESC "
            "LIMIT 10;"
        )
    },
    {
        "id": "Q074",
        "category": "Inventory",
        "difficulty": "Medium",
        "question": "Count how many products have low stock in Seattle warehouse",
        "ground_truth_sql": (
            "SELECT COUNT(i.inventory_id) AS low_stock_count "
            "FROM inventory_items i "
            "JOIN warehouses w ON i.warehouse_id = w.warehouse_id "
            "WHERE w.location_city = 'Seattle' AND i.quantity_on_hand <= i.reorder_point;"
        )
    },
    {
        "id": "Q075",
        "category": "Products",
        "difficulty": "Medium",
        "question": "Show products with their category description",
        "ground_truth_sql": (
            "SELECT p.product_id, p.name AS product_name, pc.name AS category_name, pc.description "
            "FROM products p "
            "JOIN product_categories pc ON p.category_id = pc.category_id "
            "LIMIT 10;"
        )
    },

    # --- HARD / COMPLEX QUERIES (76 - 105) ---
    {
        "id": "Q076",
        "category": "Sales",
        "difficulty": "Hard",
        "question": "Rank customers by total spend within each customer segment",
        "ground_truth_sql": (
            "SELECT c.customer_segment, c.customer_id, c.first_name, c.last_name, "
            "ROUND(SUM(o.total_amount), 2) AS total_spend, "
            "DENSE_RANK() OVER (PARTITION BY c.customer_segment ORDER BY SUM(o.total_amount) DESC) AS rank_in_segment "
            "FROM customers c "
            "JOIN orders o ON c.customer_id = o.customer_id "
            "WHERE o.status != 'cancelled' "
            "GROUP BY c.customer_segment, c.customer_id, c.first_name, c.last_name "
            "ORDER BY c.customer_segment, rank_in_segment "
            "LIMIT 15;"
        )
    },
    {
        "id": "Q077",
        "category": "Procurement",
        "difficulty": "Hard",
        "question": "Which supplier provided the product with the highest total retail sales revenue?",
        "ground_truth_sql": (
            "SELECT s.name AS supplier_name, p.name AS product_name, "
            "ROUND(SUM(oi.total_price), 2) AS total_retail_sales "
            "FROM suppliers s "
            "JOIN purchase_orders po ON s.supplier_id = po.supplier_id "
            "JOIN purchase_order_items poi ON po.po_id = poi.po_id "
            "JOIN products p ON poi.product_id = p.product_id "
            "JOIN order_items oi ON p.product_id = oi.product_id "
            "GROUP BY s.supplier_id, s.name, p.product_id, p.name "
            "ORDER BY total_retail_sales DESC "
            "LIMIT 1;"
        )
    },
    {
        "id": "Q078",
        "category": "Logistics",
        "difficulty": "Hard",
        "question": "Find customers whose shipments were handled by FedEx and had orders over 1000 dollars",
        "ground_truth_sql": (
            "SELECT DISTINCT c.customer_id, c.first_name, c.last_name, o.order_id, o.total_amount, s.carrier, s.tracking_number "
            "FROM customers c "
            "JOIN orders o ON c.customer_id = o.customer_id "
            "JOIN shipments s ON o.order_id = s.order_id "
            "WHERE s.carrier = 'FedEx' AND o.total_amount > 1000 "
            "ORDER BY o.total_amount DESC;"
        )
    },
    {
        "id": "Q079",
        "category": "Products",
        "difficulty": "Hard",
        "question": "Calculate gross profit margin percentage for each product category based on delivered orders",
        "ground_truth_sql": (
            "SELECT pc.name AS category_name, "
            "ROUND(SUM(oi.total_price), 2) AS gross_revenue, "
            "ROUND(SUM(oi.quantity * p.cost_price), 2) AS total_cost, "
            "ROUND((SUM(oi.total_price) - SUM(oi.quantity * p.cost_price)) / SUM(oi.total_price) * 100.0, 2) AS margin_pct "
            "FROM product_categories pc "
            "JOIN products p ON pc.category_id = p.category_id "
            "JOIN order_items oi ON p.product_id = oi.product_id "
            "JOIN orders o ON oi.order_id = o.order_id "
            "WHERE o.status = 'delivered' "
            "GROUP BY pc.category_id, pc.name "
            "ORDER BY margin_pct DESC;"
        )
    },
    {
        "id": "Q080",
        "category": "Support",
        "difficulty": "Hard",
        "question": "Show customers who have both open support tickets and orders with pending status",
        "ground_truth_sql": (
            "SELECT c.customer_id, c.first_name, c.last_name, st.subject AS ticket_subject, o.order_id AS pending_order_id "
            "FROM customers c "
            "JOIN support_tickets st ON c.customer_id = st.customer_id "
            "JOIN orders o ON c.customer_id = o.customer_id "
            "WHERE st.status = 'open' AND o.status = 'pending';"
        )
    },
    {
        "id": "Q081",
        "category": "Sales",
        "difficulty": "Hard",
        "question": "Calculate customer lifetime value and order frequency for the top 10 most valuable customers",
        "ground_truth_sql": (
            "SELECT c.customer_id, c.first_name || ' ' || c.last_name AS customer_name, "
            "c.customer_segment, COUNT(DISTINCT o.order_id) AS order_count, "
            "ROUND(SUM(o.total_amount), 2) AS lifetime_value, "
            "ROUND(AVG(o.total_amount), 2) AS average_order_value "
            "FROM customers c "
            "JOIN orders o ON c.customer_id = o.customer_id "
            "WHERE o.status != 'cancelled' "
            "GROUP BY c.customer_id, customer_name, c.customer_segment "
            "ORDER BY lifetime_value DESC "
            "LIMIT 10;"
        )
    },
    {
        "id": "Q082",
        "category": "HR",
        "difficulty": "Hard",
        "question": "Find employees who earn more than the average salary of their respective department",
        "ground_truth_sql": (
            "SELECT e.employee_id, e.first_name, e.last_name, e.salary, d.name AS department_name "
            "FROM employees e "
            "JOIN departments d ON e.department_id = d.department_id "
            "WHERE e.salary > ( "
            "    SELECT AVG(e2.salary) "
            "    FROM employees e2 "
            "    WHERE e2.department_id = e.department_id "
            ") "
            "ORDER BY e.salary DESC;"
        )
    },
    {
        "id": "Q083",
        "category": "Inventory",
        "difficulty": "Hard",
        "question": "Identify products that are low in stock across multiple warehouses simultaneously",
        "ground_truth_sql": (
            "SELECT p.product_id, p.name AS product_name, "
            "COUNT(DISTINCT i.warehouse_id) AS low_stock_warehouse_count, "
            "SUM(i.quantity_on_hand) AS total_available_stock "
            "FROM products p "
            "JOIN inventory_items i ON p.product_id = i.product_id "
            "WHERE i.quantity_on_hand <= i.reorder_point "
            "GROUP BY p.product_id, p.name "
            "HAVING low_stock_warehouse_count >= 2 "
            "ORDER BY low_stock_warehouse_count DESC;"
        )
    },
    {
        "id": "Q084",
        "category": "Reviews",
        "difficulty": "Hard",
        "question": "Compare average customer review rating against total quantity sold for each product",
        "ground_truth_sql": (
            "SELECT p.product_id, p.name AS product_name, "
            "ROUND(AVG(r.rating), 2) AS avg_customer_rating, "
            "COALESCE(SUM(oi.quantity), 0) AS total_quantity_sold "
            "FROM products p "
            "LEFT JOIN reviews r ON p.product_id = r.product_id "
            "LEFT JOIN order_items oi ON p.product_id = oi.product_id "
            "GROUP BY p.product_id, p.name "
            "HAVING avg_customer_rating IS NOT NULL "
            "ORDER BY total_quantity_sold DESC "
            "LIMIT 10;"
        )
    },
    {
        "id": "Q085",
        "category": "Logistics",
        "difficulty": "Hard",
        "question": "Find warehouses that fulfill orders for VIP customers with delivery via UPS or FedEx",
        "ground_truth_sql": (
            "SELECT DISTINCT w.name AS warehouse_name, w.location_city, s.carrier, c.customer_segment "
            "FROM warehouses w "
            "JOIN shipments s ON w.warehouse_id = s.warehouse_id "
            "JOIN orders o ON s.order_id = o.order_id "
            "JOIN customers c ON o.customer_id = c.customer_id "
            "WHERE c.customer_segment = 'VIP' AND s.carrier IN ('UPS', 'FedEx');"
        )
    },
    {
        "id": "Q086",
        "category": "Procurement",
        "difficulty": "Hard",
        "question": "List suppliers where total purchase orders received exceeds 50000 dollars and supplier rating is at least 4.5",
        "ground_truth_sql": (
            "SELECT s.supplier_id, s.name AS supplier_name, s.rating, "
            "ROUND(SUM(po.total_amount), 2) AS total_procured "
            "FROM suppliers s "
            "JOIN purchase_orders po ON s.supplier_id = po.supplier_id "
            "WHERE po.status = 'received' AND s.rating >= 4.5 "
            "GROUP BY s.supplier_id, s.name, s.rating "
            "HAVING total_procured > 50000 "
            "ORDER BY total_procured DESC;"
        )
    },
    {
        "id": "Q087",
        "category": "Sales",
        "difficulty": "Hard",
        "question": "Identify products with zero sales in the order items table",
        "ground_truth_sql": (
            "SELECT p.product_id, p.name, p.base_price, pc.name AS category_name "
            "FROM products p "
            "JOIN product_categories pc ON p.category_id = pc.category_id "
            "LEFT JOIN order_items oi ON p.product_id = oi.product_id "
            "WHERE oi.order_item_id IS NULL;"
        )
    },
    {
        "id": "Q088",
        "category": "Support",
        "difficulty": "Hard",
        "question": "Calculate resolution rate and average resolution time in hours for each support agent",
        "ground_truth_sql": (
            "SELECT e.first_name || ' ' || e.last_name AS agent_name, "
            "COUNT(st.ticket_id) AS total_assigned, "
            "SUM(CASE WHEN st.status IN ('resolved', 'closed') THEN 1 ELSE 0 END) AS resolved_count, "
            "ROUND(AVG(CASE WHEN st.resolved_at IS NOT NULL THEN (julianday(st.resolved_at) - julianday(st.created_at)) * 24.0 END), 1) AS avg_resolution_hours "
            "FROM employees e "
            "JOIN support_tickets st ON e.employee_id = st.assigned_employee_id "
            "GROUP BY e.employee_id, agent_name "
            "ORDER BY resolved_count DESC;"
        )
    },
    {
        "id": "Q089",
        "category": "Coupons",
        "difficulty": "Hard",
        "question": "Which coupon generated the highest total order revenue when applied?",
        "ground_truth_sql": (
            "SELECT c.code, c.discount_type, c.discount_value, "
            "ROUND(SUM(o.total_amount), 2) AS total_order_revenue, "
            "ROUND(SUM(da.amount_saved), 2) AS total_discounts_given "
            "FROM coupons c "
            "JOIN discounts_applied da ON c.coupon_id = da.coupon_id "
            "JOIN orders o ON da.order_id = o.order_id "
            "GROUP BY c.coupon_id, c.code "
            "ORDER BY total_order_revenue DESC "
            "LIMIT 1;"
        )
    },
    {
        "id": "Q090",
        "category": "Audit",
        "difficulty": "Hard",
        "question": "Count audit trail actions grouped by department of the employee who made the change",
        "ground_truth_sql": (
            "SELECT d.name AS department_name, al.action, COUNT(al.log_id) AS event_count "
            "FROM audit_logs al "
            "JOIN employees e ON al.changed_by_employee_id = e.employee_id "
            "JOIN departments d ON e.department_id = d.department_id "
            "GROUP BY d.department_id, d.name, al.action "
            "ORDER BY d.name, event_count DESC;"
        )
    },
    {
        "id": "Q091",
        "category": "Sales",
        "difficulty": "Hard",
        "question": "Find the month with the highest gross sales revenue in history",
        "ground_truth_sql": (
            "SELECT strftime('%Y-%m', order_date) AS best_month, "
            "ROUND(SUM(total_amount), 2) AS gross_revenue, "
            "COUNT(order_id) AS total_orders "
            "FROM orders "
            "WHERE status != 'cancelled' "
            "GROUP BY best_month "
            "ORDER BY gross_revenue DESC "
            "LIMIT 1;"
        )
    },
    {
        "id": "Q092",
        "category": "Logistics",
        "difficulty": "Hard",
        "question": "Show carriers with average delivery transit time in days for delivered shipments",
        "ground_truth_sql": (
            "SELECT carrier, COUNT(shipment_id) AS delivered_shipments, "
            "ROUND(AVG(julianday(actual_delivery) - julianday(ship_date)), 1) AS avg_delivery_days "
            "FROM shipments "
            "WHERE shipment_status = 'delivered' AND actual_delivery IS NOT NULL AND ship_date IS NOT NULL "
            "GROUP BY carrier "
            "ORDER BY avg_delivery_days ASC;"
        )
    },
    {
        "id": "Q093",
        "category": "Customers",
        "difficulty": "Hard",
        "question": "List customers who have purchased products across 3 or more distinct product categories",
        "ground_truth_sql": (
            "SELECT c.customer_id, c.first_name, c.last_name, "
            "COUNT(DISTINCT p.category_id) AS distinct_categories_bought "
            "FROM customers c "
            "JOIN orders o ON c.customer_id = o.customer_id "
            "JOIN order_items oi ON o.order_id = oi.order_id "
            "JOIN products p ON oi.product_id = p.product_id "
            "GROUP BY c.customer_id, c.first_name, c.last_name "
            "HAVING distinct_categories_bought >= 3 "
            "ORDER BY distinct_categories_bought DESC;"
        )
    },
    {
        "id": "Q094",
        "category": "Products",
        "difficulty": "Hard",
        "question": "Rank product categories by total net profit (total sales minus procurement cost)",
        "ground_truth_sql": (
            "SELECT pc.name AS category_name, "
            "ROUND(SUM(oi.total_price), 2) AS revenue, "
            "ROUND(SUM(oi.quantity * p.cost_price), 2) AS total_cost, "
            "ROUND(SUM(oi.total_price) - SUM(oi.quantity * p.cost_price), 2) AS net_profit "
            "FROM product_categories pc "
            "JOIN products p ON pc.category_id = p.category_id "
            "JOIN order_items oi ON p.product_id = oi.product_id "
            "JOIN orders o ON oi.order_id = o.order_id "
            "WHERE o.status = 'delivered' "
            "GROUP BY pc.category_id, pc.name "
            "ORDER BY net_profit DESC;"
        )
    },
    {
        "id": "Q095",
        "category": "HR",
        "difficulty": "Hard",
        "question": "Show department managers and the count of direct report employees they supervise",
        "ground_truth_sql": (
            "SELECT m.employee_id AS manager_id, m.first_name || ' ' || m.last_name AS manager_name, "
            "m.job_title, COUNT(e.employee_id) AS direct_reports_count "
            "FROM employees m "
            "JOIN employees e ON m.employee_id = e.manager_id "
            "GROUP BY m.employee_id, manager_name, m.job_title "
            "ORDER BY direct_reports_count DESC;"
        )
    },
    {
        "id": "Q096",
        "category": "Inventory",
        "difficulty": "Hard",
        "question": "Calculate total inventory asset value (quantity on hand times product cost price) per warehouse",
        "ground_truth_sql": (
            "SELECT w.name AS warehouse_name, w.location_city, "
            "SUM(i.quantity_on_hand) AS total_units, "
            "ROUND(SUM(i.quantity_on_hand * p.cost_price), 2) AS total_inventory_value "
            "FROM warehouses w "
            "JOIN inventory_items i ON w.warehouse_id = i.warehouse_id "
            "JOIN products p ON i.product_id = p.product_id "
            "GROUP BY w.warehouse_id, w.name, w.location_city "
            "ORDER BY total_inventory_value DESC;"
        )
    },
    {
        "id": "Q097",
        "category": "Suppliers",
        "difficulty": "Hard",
        "question": "Show suppliers along with the warehouse city where their purchase orders were fulfilled",
        "ground_truth_sql": (
            "SELECT DISTINCT s.name AS supplier_name, s.country AS supplier_country, "
            "w.name AS warehouse_name, w.location_city AS destination_city "
            "FROM suppliers s "
            "JOIN purchase_orders po ON s.supplier_id = po.supplier_id "
            "JOIN warehouses w ON po.warehouse_id = w.warehouse_id "
            "WHERE po.status = 'received' "
            "ORDER BY supplier_name, destination_city;"
        )
    },
    {
        "id": "Q098",
        "category": "Sales",
        "difficulty": "Hard",
        "question": "Calculate the percentage contribution of each payment method to total captured revenue",
        "ground_truth_sql": (
            "SELECT payment_method, "
            "ROUND(SUM(amount), 2) AS method_revenue, "
            "ROUND(SUM(amount) * 100.0 / (SELECT SUM(amount) FROM payments WHERE payment_status = 'captured'), 2) AS percentage_of_total "
            "FROM payments "
            "WHERE payment_status = 'captured' "
            "GROUP BY payment_method "
            "ORDER BY method_revenue DESC;"
        )
    },
    {
        "id": "Q099",
        "category": "Support",
        "difficulty": "Hard",
        "question": "List customers who opened multiple support tickets along with their customer segment",
        "ground_truth_sql": (
            "SELECT c.customer_id, c.first_name, c.last_name, c.customer_segment, "
            "COUNT(st.ticket_id) AS ticket_count "
            "FROM customers c "
            "JOIN support_tickets st ON c.customer_id = st.customer_id "
            "GROUP BY c.customer_id, c.first_name, c.last_name, c.customer_segment "
            "HAVING ticket_count >= 2 "
            "ORDER BY ticket_count DESC;"
        )
    },
    {
        "id": "Q100",
        "category": "Procurement",
        "difficulty": "Hard",
        "question": "Identify purchase orders where quantity received was less than quantity ordered",
        "ground_truth_sql": (
            "SELECT po.po_id, s.name AS supplier_name, p.name AS product_name, "
            "poi.quantity_ordered, poi.quantity_received, "
            "(poi.quantity_ordered - poi.quantity_received) AS shortfall "
            "FROM purchase_orders po "
            "JOIN suppliers s ON po.supplier_id = s.supplier_id "
            "JOIN purchase_order_items poi ON po.po_id = poi.po_id "
            "JOIN products p ON poi.product_id = p.product_id "
            "WHERE poi.quantity_received < poi.quantity_ordered "
            "ORDER BY shortfall DESC "
            "LIMIT 10;"
        )
    },
    {
        "id": "Q101",
        "category": "Reviews",
        "difficulty": "Hard",
        "question": "Show product categories having an average customer review rating of at least 4.0",
        "ground_truth_sql": (
            "SELECT pc.name AS category_name, "
            "ROUND(AVG(r.rating), 2) AS category_avg_rating, "
            "COUNT(r.review_id) AS total_reviews "
            "FROM product_categories pc "
            "JOIN products p ON pc.category_id = p.category_id "
            "JOIN reviews r ON p.product_id = r.product_id "
            "GROUP BY pc.category_id, pc.name "
            "HAVING category_avg_rating >= 4.0 "
            "ORDER BY category_avg_rating DESC;"
        )
    },
    {
        "id": "Q102",
        "category": "Sales",
        "difficulty": "Hard",
        "question": "Find the top 3 best-selling products by quantity for each product category",
        "ground_truth_sql": (
            "WITH ranked_products AS ( "
            "    SELECT pc.name AS category_name, p.name AS product_name, "
            "    SUM(oi.quantity) AS units_sold, "
            "    ROW_NUMBER() OVER (PARTITION BY pc.category_id ORDER BY SUM(oi.quantity) DESC) AS rank_in_cat "
            "    FROM product_categories pc "
            "    JOIN products p ON pc.category_id = p.category_id "
            "    JOIN order_items oi ON p.product_id = oi.product_id "
            "    GROUP BY pc.category_id, pc.name, p.product_id, p.name "
            ") "
            "SELECT category_name, product_name, units_sold "
            "FROM ranked_products "
            "WHERE rank_in_cat <= 3 "
            "ORDER BY category_name, units_sold DESC "
            "LIMIT 20;"
        )
    },
    {
        "id": "Q103",
        "category": "HR",
        "difficulty": "Hard",
        "question": "List employees who manage warehouses and show the total capacity of warehouses they oversee",
        "ground_truth_sql": (
            "SELECT e.employee_id, e.first_name || ' ' || e.last_name AS manager_name, "
            "e.job_title, COUNT(w.warehouse_id) AS facilities_managed, "
            "SUM(w.capacity_units) AS total_managed_capacity "
            "FROM employees e "
            "JOIN warehouses w ON e.employee_id = w.manager_employee_id "
            "GROUP BY e.employee_id, manager_name, e.job_title "
            "ORDER BY total_managed_capacity DESC;"
        )
    },
    {
        "id": "Q104",
        "category": "Logistics",
        "difficulty": "Hard",
        "question": "Find customer orders with shipment status of delayed or returned",
        "ground_truth_sql": (
            "SELECT o.order_id, c.first_name || ' ' || c.last_name AS customer_name, "
            "s.carrier, s.tracking_number, s.shipment_status, o.total_amount "
            "FROM orders o "
            "JOIN customers c ON o.customer_id = c.customer_id "
            "JOIN shipments s ON o.order_id = s.order_id "
            "WHERE s.shipment_status IN ('delayed', 'returned');"
        )
    },
    {
        "id": "Q105",
        "category": "Sales",
        "difficulty": "Hard",
        "question": "Calculate customer retention by counting how many customers placed orders in multiple calendar quarters",
        "ground_truth_sql": (
            "SELECT c.customer_id, c.first_name, c.last_name, "
            "COUNT(DISTINCT strftime('%Y', o.order_date) || '-Q' || ((CAST(strftime('%m', o.order_date) AS INTEGER) + 2) / 3)) AS active_quarters "
            "FROM customers c "
            "JOIN orders o ON c.customer_id = o.customer_id "
            "GROUP BY c.customer_id, c.first_name, c.last_name "
            "HAVING active_quarters >= 2 "
            "ORDER BY active_quarters DESC "
            "LIMIT 10;"
        )
    },
]


def verify_and_save_benchmark():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print(f"Validating {len(QUERIES)} ground-truth queries against database...")
    valid_count = 0
    errors = []

    for item in QUERIES:
        qid = item["id"]
        sql = item["ground_truth_sql"]
        try:
            cursor.execute(sql)
            rows = cursor.fetchall()
            valid_count += 1
        except Exception as e:
            errors.append((qid, sql, str(e)))

    conn.close()

    if errors:
        print(f"Validation failed on {len(errors)} queries:")
        for qid, sql, err in errors:
            print(f"  [{qid}] {err}")
            print(f"  SQL: {sql}")
        raise RuntimeError("Ground-truth queries validation failed.")

    print(f"All {valid_count}/{len(QUERIES)} ground-truth queries verified successfully!")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(QUERIES, f, indent=2)

    print(f"Saved benchmark suite to: {OUTPUT_PATH}")


if __name__ == "__main__":
    verify_and_save_benchmark()
