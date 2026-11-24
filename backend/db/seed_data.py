"""
Seed script for Enterprise Relational Database (22 tables, 2,500+ records)
Ensures realistic, deterministic data with valid foreign keys.
"""

import os
import random
import sqlite3
from datetime import datetime, timedelta

# Fix random seed for reproducible benchmark and consistent test results
random.seed(42)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(CURRENT_DIR))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
DB_PATH = os.path.join(DATA_DIR, "enterprise.db")
SCHEMA_PATH = os.path.join(CURRENT_DIR, "schema.sql")


def init_database(db_path: str = DB_PATH, schema_path: str = SCHEMA_PATH) -> None:
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    with open(schema_path, "r", encoding="utf-8") as f:
        schema_sql = f.read()
    conn.executescript(schema_sql)
    conn.commit()
    conn.close()


def seed_database(db_path: str = DB_PATH) -> dict:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    counts = {}

    # 1. Departments (8)
    departments = [
        ("Engineering", "ENG", 1200000.0),
        ("Customer Support", "SUP", 450000.0),
        ("Sales", "SLS", 850000.0),
        ("Marketing", "MKT", 600000.0),
        ("Supply Chain & Logistics", "SCL", 750000.0),
        ("Finance", "FIN", 500000.0),
        ("Human Resources", "HR", 350000.0),
        ("Product Management", "PRD", 700000.0),
    ]
    cursor.executemany(
        "INSERT INTO departments (name, code, budget) VALUES (?, ?, ?);",
        departments,
    )
    counts["departments"] = len(departments)

    # 2. Employees (25)
    first_names = [
        "Alex", "Jordan", "Taylor", "Morgan", "Sam", "Chris", "Pat", "Casey",
        "Riley", "Avery", "Cameron", "Dakota", "Jamie", "Logan", "Reese",
        "Kendall", "Quinn", "Skyler", "Harper", "Rowan", "Hayden", "Finley",
        "Emerson", "River", "Parker"
    ]
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller",
        "Davis", "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez",
        "Wilson", "Anderson", "Thomas", "Taylor", "Moore", "Jackson", "Martin",
        "Lee", "Perez", "Thompson", "White", "Harris"
    ]
    job_titles = [
        ("Engineering", "VP of Engineering", 195000.0),
        ("Engineering", "Senior Software Engineer", 145000.0),
        ("Engineering", "DevOps Engineer", 130000.0),
        ("Engineering", "Database Administrator", 135000.0),
        ("Customer Support", "Support Director", 115000.0),
        ("Customer Support", "Senior Support Specialist", 68000.0),
        ("Customer Support", "Support Representative", 52000.0),
        ("Customer Support", "Technical Support Lead", 78000.0),
        ("Sales", "Head of Sales", 160000.0),
        ("Sales", "Enterprise Account Executive", 120000.0),
        ("Sales", "Account Manager", 85000.0),
        ("Sales", "Sales Development Rep", 60000.0),
        ("Marketing", "Chief Marketing Officer", 175000.0),
        ("Marketing", "Growth Marketing Lead", 105000.0),
        ("Marketing", "Content Strategist", 75000.0),
        ("Supply Chain & Logistics", "Director of Logistics", 140000.0),
        ("Supply Chain & Logistics", "Warehouse Operations Manager", 90000.0),
        ("Supply Chain & Logistics", "Inventory Controller", 72000.0),
        ("Finance", "CFO", 210000.0),
        ("Finance", "Senior Financial Analyst", 110000.0),
        ("Finance", "Staff Accountant", 78000.0),
        ("Human Resources", "HR Director", 125000.0),
        ("Human Resources", "Talent Acquisition Lead", 85000.0),
        ("Product Management", "VP of Product", 185000.0),
        ("Product Management", "Senior Product Manager", 140000.0),
    ]

    employees_data = []
    base_date = datetime(2021, 1, 1)
    for i, (dept_name, title, salary) in enumerate(job_titles):
        cursor.execute("SELECT department_id FROM departments WHERE name = ?", (dept_name,))
        dept_id = cursor.fetchone()[0]
        f_name = first_names[i]
        l_name = last_names[i]
        email = f"{f_name.lower()}.{l_name.lower()}@enterprise.internal"
        phone = f"+1-555-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        hire_date = (base_date + timedelta(days=random.randint(0, 1100))).strftime("%Y-%m-%d")
        manager_id = 1 if i != 0 and i < 8 else (8 if i >= 8 and i < 12 else (16 if i >= 15 and i < 18 else None))
        employees_data.append((dept_id, manager_id, f_name, l_name, email, phone, title, salary, hire_date, "active"))

    cursor.executemany(
        """INSERT INTO employees (department_id, manager_id, first_name, last_name, email, phone, job_title, salary, hire_date, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""",
        employees_data,
    )
    counts["employees"] = len(employees_data)

    # 3. Customers (100)
    segments = ["Enterprise", "SMB", "Consumer", "VIP"]
    customer_data = []
    c_base_date = datetime(2023, 1, 1)
    for i in range(100):
        fn = random.choice(first_names)
        ln = random.choice(last_names)
        email = f"user{i+1}_{fn.lower()}@example.com"
        phone = f"+1-800-{random.randint(100, 999)}-{random.randint(1000, 9999)}"
        segment = random.choices(segments, weights=[0.15, 0.25, 0.50, 0.10])[0]
        status = random.choices(["active", "inactive", "suspended"], weights=[0.90, 0.08, 0.02])[0]
        created_at = (c_base_date + timedelta(days=random.randint(0, 700))).strftime("%Y-%m-%d %H:%M:%S")
        customer_data.append((fn, ln, email, phone, segment, status, created_at))

    cursor.executemany(
        """INSERT INTO customers (first_name, last_name, email, phone, customer_segment, status, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?);""",
        customer_data,
    )
    counts["customers"] = len(customer_data)

    # 4. Customer Addresses (120)
    cities_states = [
        ("San Francisco", "CA", "94105"), ("New York", "NY", "10001"),
        ("Austin", "TX", "78701"), ("Seattle", "WA", "98101"),
        ("Chicago", "IL", "60601"), ("Boston", "MA", "02108"),
        ("Atlanta", "GA", "30301"), ("Denver", "CO", "80201"),
        ("Miami", "FL", "33101"), ("San Diego", "CA", "92101")
    ]
    addr_data = []
    for cid in range(1, 101):
        city, state, zip_code = random.choice(cities_states)
        street = f"{random.randint(100, 9999)} Market Street"
        addr_data.append((cid, "shipping", street, city, state, zip_code, "USA", 1))
        if cid <= 20:
            b_city, b_state, b_zip = random.choice(cities_states)
            addr_data.append((cid, "billing", f"{random.randint(100, 9999)} Financial Way", b_city, b_state, b_zip, "USA", 0))

    cursor.executemany(
        """INSERT INTO customer_addresses (customer_id, address_type, street, city, state, postal_code, country, is_default)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?);""",
        addr_data,
    )
    counts["customer_addresses"] = len(addr_data)

    # 5. Product Categories (10)
    categories = [
        ("Computers & Laptops", None, "High-performance workstations and laptops"),
        ("Smartphones & Accessories", None, "Flagship mobile phones, cases, and chargers"),
        ("Audio & Headphones", None, "Studio monitors, noise-canceling headphones, and earbuds"),
        ("Office Furniture", None, "Ergonomic chairs, sit-stand desks, and desk mats"),
        ("Smart Home & IoT", None, "Smart hubs, security cameras, and automated lighting"),
        ("Wearables & Fitness", None, "Smartwatches, health bands, and trackers"),
        ("Networking & Enterprise", None, "Routers, managed switches, and access points"),
        ("Monitors & Displays", None, "4K UHD, Ultrawide, and OLED professional displays"),
        ("Storage & Memory", None, "NVMe SSDs, external backup drives, and NAS systems"),
        ("Power & Cables", None, "GaN fast chargers, surge protectors, and Thunderbolt cables"),
    ]
    cursor.executemany(
        "INSERT INTO product_categories (name, parent_category_id, description) VALUES (?, ?, ?);",
        categories,
    )
    counts["product_categories"] = len(categories)

    # 6. Products (50)
    product_templates = [
        (1, "ApexPro 16 Workstation Laptop", "APX-NB-16", 2499.00, 1650.00),
        (1, "ApexBook Air 13 Ultra", "APX-NB-13", 1199.00, 780.00),
        (1, "Titan Tower Desktop Intel i9", "TTN-PC-01", 3199.00, 2100.00),
        (1, "MicroEdge Mini PC Ryzen 9", "MCR-PC-02", 799.00, 520.00),
        (1, "CloudStation Server Blade", "CLD-SRV-01", 4500.00, 3100.00),
        (2, "Vanguard Phone 15 Pro Max", "VNG-PH-15", 1099.00, 680.00),
        (2, "Vanguard Phone 15 Standard", "VNG-PH-15S", 799.00, 480.00),
        (2, "MagSafe Duo Fast Wireless Pad", "MAG-PAD-01", 89.00, 32.00),
        (2, "ArmorFlex Tough Case iPhone 15", "ARM-CS-01", 39.99, 8.50),
        (2, "Precision Stylus Pen Ultra", "STY-PN-01", 99.00, 35.00),
        (3, "AcousticZen ANC Wireless Headphones", "ACZ-HP-01", 349.00, 180.00),
        (3, "TrueTone Studio In-Ear Monitors", "TRT-EM-01", 179.00, 85.00),
        (3, "SoundBar Prime Dolby Atmos", "SND-BR-01", 499.00, 260.00),
        (3, "StudioMicrophone XLR Cardioid", "MIC-XLR-01", 199.00, 95.00),
        (3, "UltraBass Portable Bluetooth Speaker", "SPK-BT-01", 129.00, 55.00),
        (4, "ErgoPro Mesh Executive Chair", "ERG-CHR-01", 649.00, 320.00),
        (4, "Elevate Electric Sit-Stand Desk 60x30", "DSK-SIT-01", 599.00, 290.00),
        (4, "Dual Monitor Gas Spring Arm Mount", "MNT-ARM-02", 119.00, 45.00),
        (4, "Memory Foam Ergonomic Footrest", "FTR-FOAM-01", 49.00, 16.00),
        (4, "Felt Desk Mat Large 36x16", "MAT-FLT-01", 35.00, 9.00),
        (5, "Aegis Home Security Camera 4K", "SEC-CAM-4K", 149.00, 65.00),
        (5, "SmartHub Connect Matter Thread", "HUB-MTR-01", 129.00, 52.00),
        (5, "Smart Thermostat Pro Eco", "THM-ECO-01", 199.00, 95.00),
        (5, "Smart Door Lock Fingerprint Wi-Fi", "LCK-WIFI-01", 229.00, 110.00),
        (5, "Atmosphere LED Ambient Light Bar", "LGT-LED-01", 79.00, 28.00),
        (6, "PulseTrack GPS Smartwatch Sapphire", "PLS-SW-01", 399.00, 190.00),
        (6, "FitStep Band 5 Activity Tracker", "FIT-BND-05", 89.00, 35.00),
        (6, "AeroWatch Titan Edition LTE", "AER-WCH-01", 549.00, 280.00),
        (6, "Sport Loop Breathable Watch Strap", "WCH-STP-01", 29.00, 6.00),
        (6, "Biometric Smart Ring Titanium", "RNG-BIO-01", 299.00, 140.00),
        (7, "Enterprise Multi-Gig 24-Port Switch", "NET-SWT-24", 899.00, 480.00),
        (7, "Tri-Band Wi-Fi 7 Mesh Router 2-Pack", "NET-WF7-02", 599.00, 310.00),
        (7, "Outdoor PoE Weatherproof Access Point", "NET-POE-01", 249.00, 115.00),
        (7, "Hardware Firewall Gateway Appliance", "NET-FRW-01", 749.00, 390.00),
        (7, "10Gb SFP+ Fiber Optic Transceiver", "NET-SFP-10", 69.00, 22.00),
        (8, "UltraView 34-Inch Curved OLED 175Hz", "DISP-34-OLED", 899.00, 490.00),
        (8, "ProArt Studio 27-Inch 4K Color Acc", "DISP-27-4K", 649.00, 350.00),
        (8, "FieldMonitor Portable 15.6 USB-C", "DISP-15-PRT", 229.00, 105.00),
        (8, "CommandDesk 49-Inch Super Ultrawide", "DISP-49-SUW", 1299.00, 750.00),
        (8, "ZeroBezel 24-Inch IPS Office Display", "DISP-24-IPS", 169.00, 85.00),
        (9, "HyperDrive 2TB Gen5 NVMe M.2 SSD", "SSD-NVME-2TB", 219.00, 115.00),
        (9, "HyperDrive 4TB Gen4 NVMe M.2 SSD", "SSD-NVME-4TB", 329.00, 180.00),
        (9, "SecureVault 8TB External USB-C HDD", "EXT-HDD-8TB", 189.00, 98.00),
        (9, "TeraBay 4-Bay NAS Storage Enclosure", "NAS-BAY-04", 499.00, 260.00),
        (9, "ProGrade 256GB SDXC V90 UHS-II Card", "CRD-SD-256", 129.00, 55.00),
        (10, "140W GaN 3-Port Fast Wall Charger", "CHG-GAN-140", 79.00, 28.00),
        (10, "Braided Thunderbolt 4 Cable 2m", "CBL-TB4-02", 45.00, 12.00),
        (10, "12-in-1 Thunderbolt Docking Station", "DCK-TB4-12", 279.00, 135.00),
        (10, "Heavy-Duty Surge Protector 8-Outlet", "PWR-SRG-08", 39.00, 14.00),
        (10, "Magnetic Wireless 10000mAh Power Bank", "PWR-BNK-10", 59.00, 22.00),
    ]

    p_data = []
    p_base_date = datetime(2023, 2, 1)
    for cat_id, name, sku, price, cost in product_templates:
        c_date = (p_base_date + timedelta(days=random.randint(0, 300))).strftime("%Y-%m-%d %H:%M:%S")
        p_data.append((cat_id, name, sku, f"Premium grade {name} with enterprise warranty", price, cost, 1, c_date))

    cursor.executemany(
        """INSERT INTO products (category_id, name, sku, description, base_price, cost_price, is_active, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?);""",
        p_data,
    )
    counts["products"] = len(p_data)

    # 7. Product Variants (100)
    variant_data = []
    colors = ["Space Gray", "Silver", "Midnight Black", "Arctic White", "Deep Blue"]
    sizes = ["Standard", "16GB / 512GB", "32GB / 1TB", "64GB / 2TB", "Large", "Medium"]
    for pid in range(1, 51):
        # 2 variants per product
        for v_idx in range(2):
            v_sku = f"VAR-P{pid:02d}-{v_idx+1}"
            color = colors[(pid + v_idx) % len(colors)]
            size = sizes[(pid + v_idx) % len(sizes)]
            adj = 0.0 if v_idx == 0 else random.choice([50.0, 100.0, 150.0, -20.0])
            stock = random.randint(15, 250)
            variant_data.append((pid, v_sku, color, size, adj, stock))

    cursor.executemany(
        """INSERT INTO product_variants (product_id, sku, color, size, price_adjustment, stock_quantity)
           VALUES (?, ?, ?, ?, ?, ?);""",
        variant_data,
    )
    counts["product_variants"] = len(variant_data)

    # 8. Suppliers (15)
    supplier_list = [
        ("Apex Silicon Fab Ltd", "Hao Chen", "contact@apexsilicon.tw", "+886-2-5551234", "Hsinchu", "Taiwan", 4.9, "active"),
        ("Tokyo Precision Optics", "Kenji Sato", "sales@tokyo-optics.jp", "+81-3-5558765", "Tokyo", "Japan", 4.8, "active"),
        ("Bavaria Electronics GmbH", "Stefan Becker", "info@bavaria-elec.de", "+49-89-5554321", "Munich", "Germany", 4.7, "active"),
        ("Seoul MicroDisplay Corp", "Min-ho Park", "orders@seouldisplay.kr", "+82-2-5559876", "Seoul", "South Korea", 4.9, "active"),
        ("Pacific Component Logistics", "Sarah Jenkins", "sarah@paclogistic.com", "+1-415-5553322", "San Francisco", "USA", 4.5, "active"),
        ("Nordic Acoustic Labs", "Lars Lindqvist", "lars@nordicacoustic.se", "+46-8-5556677", "Stockholm", "Sweden", 4.6, "active"),
        ("Ontario Aluminum Works", "Marc Tremblay", "mtremblay@ontarioworks.ca", "+1-416-5559988", "Toronto", "Canada", 4.4, "active"),
        ("Silicon Valley Sensors Inc", "David Zhao", "dzhao@svsensors.com", "+1-408-5551100", "San Jose", "USA", 4.7, "active"),
        ("Shenzhen FastPack Co", "Li Wei", "sales@szfastpack.cn", "+86-755-5554433", "Shenzhen", "China", 4.3, "active"),
        ("Kyoto Battery Technologies", "Yuki Tanaka", "tanaka@kyotobatt.jp", "+81-75-5552211", "Kyoto", "Japan", 4.8, "active"),
        ("Texas Thermal Dynamics", "Robert Miller", "rmiller@txthermal.com", "+1-512-5557766", "Austin", "USA", 4.6, "active"),
        ("Zurich Precision Mechanisms", "Beatrix Meyer", "bmeyer@zurichmech.ch", "+41-44-5558899", "Zurich", "Switzerland", 4.9, "active"),
        ("EuroPower Circuitry BV", "Jan van Dijk", "sales@europower.nl", "+31-20-5556655", "Amsterdam", "Netherlands", 4.2, "probation"),
        ("Singapore Micro Connectors", "Grace Tan", "gtan@sgconnect.sg", "+65-6555-1234", "Singapore", "Singapore", 4.7, "active"),
        ("Cascade Cable Manufacturing", "Brian Adams", "badams@cascadecable.com", "+1-503-5554321", "Portland", "USA", 4.5, "active"),
    ]
    cursor.executemany(
        """INSERT INTO suppliers (name, contact_name, email, phone, city, country, rating, status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?);""",
        supplier_list,
    )
    counts["suppliers"] = len(supplier_list)

    # 9. Warehouses (6)
    warehouses = [
        (17, "Central West Hub", "Seattle", "WA", "USA", 50000),
        (17, "Midwest Fulfillment Center", "Chicago", "IL", "USA", 85000),
        (17, "Southern Texas Logistics", "Dallas", "TX", "USA", 70000),
        (17, "Southeast Mega Distribution", "Atlanta", "GA", "USA", 95000),
        (17, "Northeast Express Depot", "New York", "NY", "USA", 40000),
        (17, "Pacific Gateway Terminal", "Los Angeles", "CA", "USA", 65000),
    ]
    cursor.executemany(
        """INSERT INTO warehouses (manager_employee_id, name, location_city, state, country, capacity_units)
           VALUES (?, ?, ?, ?, ?, ?);""",
        warehouses,
    )
    counts["warehouses"] = len(warehouses)

    # 10. Inventory Items (150)
    inventory_data = []
    inv_date_base = datetime(2024, 1, 1)
    for pid in range(1, 51):
        # Distribute across 3 warehouses each
        wh_ids = random.sample(range(1, 7), 3)
        for wid in wh_ids:
            qty = random.randint(5, 300)
            reorder = random.choice([20, 30, 50])
            restocked = (inv_date_base + timedelta(days=random.randint(0, 200))).strftime("%Y-%m-%d")
            # Link to first variant or None
            vid = (pid - 1) * 2 + 1
            inventory_data.append((pid, vid, wid, qty, reorder, restocked))

    cursor.executemany(
        """INSERT INTO inventory_items (product_id, variant_id, warehouse_id, quantity_on_hand, reorder_point, last_restocked_at)
           VALUES (?, ?, ?, ?, ?, ?);""",
        inventory_data,
    )
    counts["inventory_items"] = len(inventory_data)

    # 11. Purchase Orders (40)
    po_data = []
    po_base_date = datetime(2023, 6, 1)
    for i in range(40):
        sup_id = random.randint(1, 15)
        wh_id = random.randint(1, 6)
        emp_id = random.choice([16, 17, 18])  # Supply chain team
        odate = (po_base_date + timedelta(days=random.randint(0, 450))).strftime("%Y-%m-%d")
        edate = (datetime.strptime(odate, "%Y-%m-%d") + timedelta(days=random.randint(14, 45))).strftime("%Y-%m-%d")
        total_amt = round(random.uniform(5000.0, 85000.0), 2)
        status = random.choices(["received", "ordered", "draft", "cancelled"], weights=[0.7, 0.2, 0.05, 0.05])[0]
        po_data.append((sup_id, wh_id, emp_id, odate, edate, total_amt, status))

    cursor.executemany(
        """INSERT INTO purchase_orders (supplier_id, warehouse_id, created_by_employee_id, order_date, expected_date, total_amount, status)
           VALUES (?, ?, ?, ?, ?, ?, ?);""",
        po_data,
    )
    counts["purchase_orders"] = len(po_data)

    # 12. Purchase Order Items (120)
    poi_data = []
    for poid in range(1, 41):
        num_items = random.randint(2, 4)
        pids = random.sample(range(1, 51), num_items)
        for pid in pids:
            cursor.execute("SELECT cost_price FROM products WHERE product_id = ?", (pid,))
            cost = cursor.fetchone()[0]
            qty_ord = random.randint(50, 500)
            qty_rec = qty_ord if random.random() > 0.15 else int(qty_ord * random.uniform(0.7, 0.95))
            poi_data.append((poid, pid, qty_ord, cost, qty_rec))

    cursor.executemany(
        """INSERT INTO purchase_order_items (po_id, product_id, quantity_ordered, unit_cost, quantity_received)
           VALUES (?, ?, ?, ?, ?);""",
        poi_data,
    )
    counts["purchase_order_items"] = len(poi_data)

    # 13. Coupons (15)
    coupons = [
        ("SUMMER20", "percentage", 20.0, 100.0, "2024-06-01", "2024-08-31", 500, 240, 1),
        ("ENTERPRISE15", "percentage", 15.0, 1000.0, "2024-01-01", "2025-12-31", 1000, 480, 1),
        ("WELCOME10", "percentage", 10.0, 50.0, "2023-01-01", "2025-12-31", 2000, 950, 1),
        ("FLASH50", "fixed_amount", 50.0, 250.0, "2024-11-20", "2024-11-30", 300, 290, 0),
        ("VIP25", "percentage", 25.0, 500.0, "2024-01-01", "2025-12-31", 500, 185, 1),
        ("TECHSAVE", "fixed_amount", 100.0, 800.0, "2024-03-01", "2024-12-31", 400, 120, 1),
        ("FREESHIP", "fixed_amount", 15.0, 30.0, "2023-05-01", "2025-05-01", 3000, 1500, 1),
        ("CYBERMON", "percentage", 30.0, 200.0, "2024-11-25", "2024-12-05", 800, 780, 0),
        ("SPRING10", "percentage", 10.0, 75.0, "2024-03-01", "2024-05-31", 600, 310, 0),
        ("AUTUMN15", "percentage", 15.0, 150.0, "2024-09-01", "2024-11-15", 500, 280, 1),
        ("PARTNER50", "fixed_amount", 50.0, 400.0, "2024-02-01", "2025-02-01", 250, 95, 1),
        ("NEWYEAR20", "percentage", 20.0, 150.0, "2024-12-25", "2025-01-10", 400, 390, 0),
        ("WORKFORCE25", "percentage", 25.0, 1500.0, "2024-01-01", "2025-12-31", 100, 45, 1),
        ("ACCESSORY10", "fixed_amount", 10.0, 40.0, "2024-04-01", "2024-10-31", 1000, 430, 0),
        ("HOLIDAY35", "percentage", 35.0, 500.0, "2024-12-10", "2024-12-31", 500, 470, 0),
    ]
    cursor.executemany(
        """INSERT INTO coupons (code, discount_type, discount_value, min_order_amount, start_date, end_date, max_uses, times_used, is_active)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);""",
        coupons,
    )
    counts["coupons"] = len(coupons)

    # 14. Orders (200)
    order_data = []
    order_date_base = datetime(2023, 9, 1)
    payment_methods = ["credit_card", "paypal", "bank_transfer", "apple_pay"]
    order_statuses = ["delivered", "shipped", "processing", "pending", "cancelled", "refunded"]

    for oid in range(1, 201):
        cid = random.randint(1, 100)
        # pick a valid address for this customer
        cursor.execute("SELECT address_id FROM customer_addresses WHERE customer_id = ? LIMIT 1", (cid,))
        addr_row = cursor.fetchone()
        addr_id = addr_row[0] if addr_row else 1
        odate = (order_date_base + timedelta(days=random.randint(0, 450), hours=random.randint(0, 23))).strftime("%Y-%m-%d %H:%M:%S")
        status = random.choices(order_statuses, weights=[0.65, 0.15, 0.08, 0.05, 0.04, 0.03])[0]
        pay_method = random.choice(payment_methods)
        # Placeholders for financial fields, will update after order_items
        order_data.append((cid, addr_id, odate, status, 0.0, 0.0, 0.0, 0.0, 0.0, pay_method))

    cursor.executemany(
        """INSERT INTO orders (customer_id, shipping_address_id, order_date, status, subtotal, tax_amount, shipping_fee, discount_amount, total_amount, payment_method)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""",
        order_data,
    )
    counts["orders"] = len(order_data)

    # 15. Order Items (550) & recalculate orders totals
    order_items_data = []
    for oid in range(1, 201):
        num_items = random.choices([1, 2, 3, 4, 5], weights=[0.3, 0.35, 0.2, 0.1, 0.05])[0]
        chosen_pids = random.sample(range(1, 51), num_items)
        subtotal = 0.0
        for pid in chosen_pids:
            cursor.execute("SELECT base_price FROM products WHERE product_id = ?", (pid,))
            price = cursor.fetchone()[0]
            qty = random.choices([1, 2, 3, 5, 10], weights=[0.65, 0.20, 0.10, 0.03, 0.02])[0]
            vid = (pid - 1) * 2 + random.choice([1, 2])
            item_total = round(price * qty, 2)
            subtotal += item_total
            order_items_data.append((oid, pid, vid, qty, price, item_total))

        # Financial breakdown
        tax = round(subtotal * 0.0825, 2)
        shipping = 0.0 if subtotal > 150 else 15.00
        discount = round(subtotal * 0.10, 2) if (oid % 3 == 0) else 0.0
        total = round(subtotal + tax + shipping - discount, 2)
        cursor.execute(
            """UPDATE orders SET subtotal = ?, tax_amount = ?, shipping_fee = ?, discount_amount = ?, total_amount = ?
               WHERE order_id = ?;""",
            (subtotal, tax, shipping, discount, total, oid),
        )

    cursor.executemany(
        """INSERT INTO order_items (order_id, product_id, variant_id, quantity, unit_price, total_price)
           VALUES (?, ?, ?, ?, ?, ?);""",
        order_items_data,
    )
    counts["order_items"] = len(order_items_data)

    # 16. Payments (200)
    payment_data = []
    for oid in range(1, 201):
        cursor.execute("SELECT order_date, total_amount, payment_method, status FROM orders WHERE order_id = ?", (oid,))
        odate, total, method, ostatus = cursor.fetchone()
        pstatus = "refunded" if ostatus == "refunded" else ("failed" if ostatus == "cancelled" and random.random() < 0.5 else "captured")
        tx_ref = f"TXN-{random.randint(10000000, 99999999)}"
        payment_data.append((oid, odate, total, method, pstatus, tx_ref))

    cursor.executemany(
        """INSERT INTO payments (order_id, payment_date, amount, payment_method, payment_status, transaction_reference)
           VALUES (?, ?, ?, ?, ?, ?);""",
        payment_data,
    )
    counts["payments"] = len(payment_data)

    # 17. Shipments (180)
    shipment_data = []
    carriers = ["FedEx", "UPS", "DHL", "USPS"]
    for oid in range(1, 181):
        cursor.execute("SELECT order_date, status FROM orders WHERE order_id = ?", (oid,))
        odate_str, ostatus = cursor.fetchone()
        odate = datetime.strptime(odate_str, "%Y-%m-%d %H:%M:%S")
        carrier = random.choice(carriers)
        trk = f"{carrier[:2].upper()}{random.randint(1000000000, 9999999999)}"
        wh_id = random.randint(1, 6)

        if ostatus in ["delivered", "shipped"]:
            sdate = (odate + timedelta(hours=random.randint(12, 48))).strftime("%Y-%m-%d %H:%M:%S")
            edate = (odate + timedelta(days=random.randint(3, 7))).strftime("%Y-%m-%d")
            adate = (odate + timedelta(days=random.randint(3, 6))).strftime("%Y-%m-%d %H:%M:%S") if ostatus == "delivered" else None
            s_status = "delivered" if ostatus == "delivered" else "in_transit"
        elif ostatus == "processing":
            sdate, edate, adate = None, None, None
            s_status = "preparing"
        else:
            sdate, edate, adate = None, None, None
            s_status = "returned" if ostatus == "refunded" else "preparing"

        shipment_data.append((oid, wh_id, carrier, trk, sdate, edate, adate, s_status))

    cursor.executemany(
        """INSERT INTO shipments (order_id, warehouse_id, carrier, tracking_number, ship_date, estimated_delivery, actual_delivery, shipment_status)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?);""",
        shipment_data,
    )
    counts["shipments"] = len(shipment_data)

    # 18. Reviews (150)
    review_comments = [
        (5, "Incredible performance!", "Exceeded all my expectations. Flawless build quality and snappy response."),
        (5, "Best purchase of the year", "Great value for money, integrates effortlessly with the rest of my setup."),
        (4, "Very solid device", "Does what it says. Battery life could be slightly better, but overall very happy."),
        (4, "Great enterprise quality", "Deploys smoothly across our fleet, user feedback has been very positive."),
        (3, "Average, meets basic needs", "Does the job, but software interface could use some refinement."),
        (2, "Disappointed with build", "Ran hotter than expected under moderate load. Expected more at this price."),
        (1, "Issues on day one", "Unit arrived with packaging damaged and intermittent connectivity."),
        (5, "Outstanding support & quality", "Had a minor query and support resolved it within 2 hours. Top notch!"),
    ]
    review_data = []
    r_base_date = datetime(2023, 10, 1)
    for _ in range(150):
        pid = random.randint(1, 50)
        cid = random.randint(1, 100)
        rating, title, comment = random.choices(
            review_comments,
            weights=[0.35, 0.25, 0.15, 0.10, 0.07, 0.04, 0.02, 0.02]
        )[0]
        rdate = (r_base_date + timedelta(days=random.randint(0, 400))).strftime("%Y-%m-%d")
        review_data.append((pid, cid, rating, title, comment, rdate, 1))

    cursor.executemany(
        """INSERT INTO reviews (product_id, customer_id, rating, title, comment, review_date, is_verified_purchase)
           VALUES (?, ?, ?, ?, ?, ?, ?);""",
        review_data,
    )
    counts["reviews"] = len(review_data)

    # 19. Discounts Applied (80)
    disc_data = []
    for oid in range(1, 81):
        coupon_id = random.randint(1, 15)
        cursor.execute("SELECT discount_amount FROM orders WHERE order_id = ?", (oid,))
        disc_amt = cursor.fetchone()[0]
        if disc_amt > 0:
            disc_data.append((oid, coupon_id, disc_amt))
        else:
            disc_data.append((oid, coupon_id, 25.0))

    cursor.executemany(
        "INSERT INTO discounts_applied (order_id, coupon_id, amount_saved) VALUES (?, ?, ?);",
        disc_data,
    )
    counts["discounts_applied"] = len(disc_data)

    # 20. Support Tickets (80)
    ticket_subjects = [
        ("Billing", "Invoice breakdown discrepancy", "medium"),
        ("Billing", "Duplicate charge on credit card", "high"),
        ("Shipping", "Tracking number not updating for 4 days", "medium"),
        ("Shipping", "Package delivered to wrong address", "urgent"),
        ("Returns", "Request return label for damaged variant", "medium"),
        ("Product Question", "Compatibility with Wi-Fi 7 access points", "low"),
        ("Product Question", "Firmware update release timeline", "low"),
        ("Technical", "SSO integration timeout during sync", "high"),
        ("Technical", "API rate limit reached on batch query", "urgent"),
        ("Technical", "Hardware peripheral driver error in Windows 11", "medium"),
    ]
    ticket_data = []
    t_base_date = datetime(2023, 11, 1)
    support_agent_ids = [5, 6, 7, 8]  # Customer support employees

    for tid in range(1, 81):
        cid = random.randint(1, 100)
        cat, subj, prio = random.choice(ticket_subjects)
        agent_id = random.choice(support_agent_ids)
        cdate = (t_base_date + timedelta(days=random.randint(0, 380), hours=random.randint(0, 23)))
        cdate_str = cdate.strftime("%Y-%m-%d %H:%M:%S")
        status = random.choices(["resolved", "closed", "in_progress", "open"], weights=[0.55, 0.25, 0.12, 0.08])[0]
        rdate_str = (cdate + timedelta(hours=random.randint(2, 72))).strftime("%Y-%m-%d %H:%M:%S") if status in ["resolved", "closed"] else None
        ticket_data.append((cid, agent_id, subj, prio, status, cat, cdate_str, rdate_str))

    cursor.executemany(
        """INSERT INTO support_tickets (customer_id, assigned_employee_id, subject, priority, status, category, created_at, resolved_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?);""",
        ticket_data,
    )
    counts["support_tickets"] = len(ticket_data)

    # 21. Support Ticket Messages (200)
    msg_data = []
    for tid in range(1, 81):
        cursor.execute("SELECT customer_id, assigned_employee_id, created_at FROM support_tickets WHERE ticket_id = ?", (tid,))
        cid, emp_id, cdate_str = cursor.fetchone()
        t0 = datetime.strptime(cdate_str, "%Y-%m-%d %H:%M:%S")
        # Customer opening message
        msg_data.append((tid, "customer", cid, "Hello, I need assistance with this matter promptly.", cdate_str))
        # Agent response
        t1 = (t0 + timedelta(minutes=random.randint(15, 120))).strftime("%Y-%m-%d %H:%M:%S")
        msg_data.append((tid, "agent", emp_id, "Thank you for reaching out. I am looking into your account details now.", t1))
        if tid <= 40:
            # Followup
            t2 = (t0 + timedelta(hours=random.randint(3, 10))).strftime("%Y-%m-%d %H:%M:%S")
            msg_data.append((tid, "agent", emp_id, "This issue has been resolved. Please let us know if you need anything else.", t2))

    cursor.executemany(
        """INSERT INTO ticket_messages (ticket_id, sender_type, sender_id, message_text, created_at)
           VALUES (?, ?, ?, ?, ?);""",
        msg_data,
    )
    counts["ticket_messages"] = len(msg_data)

    # 22. Audit Logs (150)
    audit_actions = [
        ("orders", "STATUS_CHANGE", "Order status changed to delivered"),
        ("inventory_items", "UPDATE", "Restocked 50 units via PO"),
        ("products", "UPDATE", "Price adjusted for seasonal promotion"),
        ("payments", "PAYMENT_EVENT", "Payment authorized via Stripe gateway"),
        ("support_tickets", "STATUS_CHANGE", "Ticket marked resolved"),
        ("customers", "UPDATE", "Customer upgraded to VIP tier"),
    ]
    audit_data = []
    a_base_date = datetime(2024, 1, 1)
    for _ in range(150):
        entity, action, details = random.choice(audit_actions)
        eid = random.randint(1, 100)
        changed_by = random.randint(1, 25)
        tstamp = (a_base_date + timedelta(days=random.randint(0, 300), hours=random.randint(0, 23))).strftime("%Y-%m-%d %H:%M:%S")
        audit_data.append((entity, eid, action, changed_by, tstamp, details))

    cursor.executemany(
        """INSERT INTO audit_logs (entity_name, entity_id, action, changed_by_employee_id, timestamp, details)
           VALUES (?, ?, ?, ?, ?, ?);""",
        audit_data,
    )
    counts["audit_logs"] = len(audit_data)

    conn.commit()
    conn.close()

    total_records = sum(counts.values())
    counts["TOTAL"] = total_records
    return counts


if __name__ == "__main__":
    print(f"Initializing database at: {DB_PATH}")
    init_database(DB_PATH, SCHEMA_PATH)
    print("Database initialized. Seeding 22 tables...")
    counts = seed_database(DB_PATH)
    print("--- Seeding Summary ---")
    for table, count in counts.items():
        if table != "TOTAL":
            print(f"  {table.ljust(24)}: {count:4d} rows")
    print(f"Total records seeded: {counts['TOTAL']}")
