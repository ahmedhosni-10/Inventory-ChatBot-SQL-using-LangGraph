"""
setup_database.py
Creates the SQLite inventory database and seeds it with realistic test data.
Safe to re-run — uses DROP IF EXISTS + CREATE.
"""
import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "inventory.db")


def get_connection():
    return sqlite3.connect(DB_PATH)


def create_schema(conn: sqlite3.Connection):
    cursor = conn.cursor()

    # Enable foreign keys
    cursor.execute("PRAGMA foreign_keys = ON")

    # ── Customers ──────────────────────────────────────────────────────────────
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Customers (
        CustomerId      INTEGER PRIMARY KEY AUTOINCREMENT,
        CustomerCode    TEXT UNIQUE NOT NULL,
        CustomerName    TEXT NOT NULL,
        Email           TEXT,
        Phone           TEXT,
        BillingAddress1 TEXT,
        BillingCity     TEXT,
        BillingCountry  TEXT,
        CreatedAt       TEXT NOT NULL DEFAULT (datetime('now')),
        UpdatedAt       TEXT,
        IsActive        INTEGER NOT NULL DEFAULT 1
    )""")

    # ── Vendors ────────────────────────────────────────────────────────────────
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Vendors (
        VendorId    INTEGER PRIMARY KEY AUTOINCREMENT,
        VendorCode  TEXT UNIQUE NOT NULL,
        VendorName  TEXT NOT NULL,
        Email       TEXT,
        Phone       TEXT,
        AddressLine1 TEXT,
        City        TEXT,
        Country     TEXT,
        CreatedAt   TEXT NOT NULL DEFAULT (datetime('now')),
        UpdatedAt   TEXT,
        IsActive    INTEGER NOT NULL DEFAULT 1
    )""")

    # ── Sites ──────────────────────────────────────────────────────────────────
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Sites (
        SiteId      INTEGER PRIMARY KEY AUTOINCREMENT,
        SiteCode    TEXT UNIQUE NOT NULL,
        SiteName    TEXT NOT NULL,
        AddressLine1 TEXT,
        City        TEXT,
        Country     TEXT,
        TimeZone    TEXT,
        CreatedAt   TEXT NOT NULL DEFAULT (datetime('now')),
        UpdatedAt   TEXT,
        IsActive    INTEGER NOT NULL DEFAULT 1
    )""")

    # ── Locations ──────────────────────────────────────────────────────────────
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Locations (
        LocationId       INTEGER PRIMARY KEY AUTOINCREMENT,
        SiteId           INTEGER NOT NULL,
        LocationCode     TEXT NOT NULL,
        LocationName     TEXT NOT NULL,
        ParentLocationId INTEGER,
        CreatedAt        TEXT NOT NULL DEFAULT (datetime('now')),
        UpdatedAt        TEXT,
        IsActive         INTEGER NOT NULL DEFAULT 1,
        UNIQUE (SiteId, LocationCode),
        FOREIGN KEY (SiteId) REFERENCES Sites(SiteId),
        FOREIGN KEY (ParentLocationId) REFERENCES Locations(LocationId)
    )""")

    # ── Items ──────────────────────────────────────────────────────────────────
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Items (
        ItemId        INTEGER PRIMARY KEY AUTOINCREMENT,
        ItemCode      TEXT UNIQUE NOT NULL,
        ItemName      TEXT NOT NULL,
        Category      TEXT,
        UnitOfMeasure TEXT,
        CreatedAt     TEXT NOT NULL DEFAULT (datetime('now')),
        UpdatedAt     TEXT,
        IsActive      INTEGER NOT NULL DEFAULT 1
    )""")

    # ── Assets ─────────────────────────────────────────────────────────────────
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Assets (
        AssetId      INTEGER PRIMARY KEY AUTOINCREMENT,
        AssetTag     TEXT UNIQUE NOT NULL,
        AssetName    TEXT NOT NULL,
        SiteId       INTEGER NOT NULL,
        LocationId   INTEGER,
        SerialNumber TEXT,
        Category     TEXT,
        Status       TEXT NOT NULL DEFAULT 'Active',
        Cost         REAL,
        PurchaseDate TEXT,
        VendorId     INTEGER,
        CreatedAt    TEXT NOT NULL DEFAULT (datetime('now')),
        UpdatedAt    TEXT,
        FOREIGN KEY (SiteId) REFERENCES Sites(SiteId),
        FOREIGN KEY (LocationId) REFERENCES Locations(LocationId),
        FOREIGN KEY (VendorId) REFERENCES Vendors(VendorId)
    )""")

    # ── Bills ──────────────────────────────────────────────────────────────────
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Bills (
        BillId       INTEGER PRIMARY KEY AUTOINCREMENT,
        VendorId     INTEGER NOT NULL,
        BillNumber   TEXT NOT NULL,
        BillDate     TEXT NOT NULL,
        DueDate      TEXT,
        TotalAmount  REAL NOT NULL,
        Currency     TEXT NOT NULL DEFAULT 'USD',
        Status       TEXT NOT NULL DEFAULT 'Open',
        CreatedAt    TEXT NOT NULL DEFAULT (datetime('now')),
        UpdatedAt    TEXT,
        UNIQUE (VendorId, BillNumber),
        FOREIGN KEY (VendorId) REFERENCES Vendors(VendorId)
    )""")

    # ── PurchaseOrders ─────────────────────────────────────────────────────────
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS PurchaseOrders (
        POId       INTEGER PRIMARY KEY AUTOINCREMENT,
        PONumber   TEXT UNIQUE NOT NULL,
        VendorId   INTEGER NOT NULL,
        PODate     TEXT NOT NULL,
        Status     TEXT NOT NULL DEFAULT 'Open',
        SiteId     INTEGER,
        CreatedAt  TEXT NOT NULL DEFAULT (datetime('now')),
        UpdatedAt  TEXT,
        FOREIGN KEY (VendorId) REFERENCES Vendors(VendorId),
        FOREIGN KEY (SiteId) REFERENCES Sites(SiteId)
    )""")

    # ── PurchaseOrderLines ─────────────────────────────────────────────────────
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS PurchaseOrderLines (
        POLineId    INTEGER PRIMARY KEY AUTOINCREMENT,
        POId        INTEGER NOT NULL,
        LineNumber  INTEGER NOT NULL,
        ItemId      INTEGER,
        ItemCode    TEXT NOT NULL,
        Description TEXT,
        Quantity    REAL NOT NULL,
        UnitPrice   REAL NOT NULL,
        UNIQUE (POId, LineNumber),
        FOREIGN KEY (POId) REFERENCES PurchaseOrders(POId),
        FOREIGN KEY (ItemId) REFERENCES Items(ItemId)
    )""")

    # ── SalesOrders ────────────────────────────────────────────────────────────
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS SalesOrders (
        SOId       INTEGER PRIMARY KEY AUTOINCREMENT,
        SONumber   TEXT UNIQUE NOT NULL,
        CustomerId INTEGER NOT NULL,
        SODate     TEXT NOT NULL,
        Status     TEXT NOT NULL DEFAULT 'Open',
        SiteId     INTEGER,
        CreatedAt  TEXT NOT NULL DEFAULT (datetime('now')),
        UpdatedAt  TEXT,
        FOREIGN KEY (CustomerId) REFERENCES Customers(CustomerId),
        FOREIGN KEY (SiteId) REFERENCES Sites(SiteId)
    )""")

    # ── SalesOrderLines ────────────────────────────────────────────────────────
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS SalesOrderLines (
        SOLineId    INTEGER PRIMARY KEY AUTOINCREMENT,
        SOId        INTEGER NOT NULL,
        LineNumber  INTEGER NOT NULL,
        ItemId      INTEGER,
        ItemCode    TEXT NOT NULL,
        Description TEXT,
        Quantity    REAL NOT NULL,
        UnitPrice   REAL NOT NULL,
        UNIQUE (SOId, LineNumber),
        FOREIGN KEY (SOId) REFERENCES SalesOrders(SOId),
        FOREIGN KEY (ItemId) REFERENCES Items(ItemId)
    )""")

    # ── AssetTransactions ──────────────────────────────────────────────────────
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS AssetTransactions (
        AssetTxnId     INTEGER PRIMARY KEY AUTOINCREMENT,
        AssetId        INTEGER NOT NULL,
        FromLocationId INTEGER,
        ToLocationId   INTEGER,
        TxnType        TEXT NOT NULL,
        Quantity       INTEGER NOT NULL DEFAULT 1,
        TxnDate        TEXT NOT NULL DEFAULT (datetime('now')),
        Note           TEXT,
        FOREIGN KEY (AssetId) REFERENCES Assets(AssetId),
        FOREIGN KEY (FromLocationId) REFERENCES Locations(LocationId),
        FOREIGN KEY (ToLocationId) REFERENCES Locations(LocationId)
    )""")

    conn.commit()
    print("[OK] Schema created successfully.")


def seed_data(conn: sqlite3.Connection):
    cursor = conn.cursor()

    # Check if already seeded
    cursor.execute("SELECT COUNT(*) FROM Vendors")
    if cursor.fetchone()[0] > 0:
        print("[INFO] Database already seeded -- skipping.")
        return

    # ── Customers ──────────────────────────────────────────────────────────────
    customers = [
        ("CUST-001", "Apex Technologies Ltd",       "billing@apex-tech.com",    "+1-555-0101", "100 Tech Park Blvd",     "Austin",      "USA",     1),
        ("CUST-002", "BlueSky Manufacturing",        "ap@bluesky-mfg.com",       "+1-555-0102", "250 Industrial Ave",     "Chicago",     "USA",     1),
        ("CUST-003", "Crestview Logistics",          "orders@crestview.com",     "+44-20-7946", "12 Harbour Lane",        "London",      "UK",      1),
        ("CUST-004", "Delta Retail Group",           "procurement@delta-rg.com", "+1-555-0104", "88 Commerce St",         "New York",    "USA",     1),
        ("CUST-005", "Evergreen Solutions",          "info@evergreensol.com",    "+49-30-1234", "Unter den Linden 5",     "Berlin",      "Germany", 1),
        ("CUST-006", "FuturePath Consulting",        "accounts@futurepath.io",   "+1-555-0106", "3000 Silicon Rd",        "San Jose",    "USA",     0),  # Inactive
    ]
    cursor.executemany("""
        INSERT INTO Customers (CustomerCode,CustomerName,Email,Phone,BillingAddress1,BillingCity,BillingCountry,IsActive)
        VALUES (?,?,?,?,?,?,?,?)""", customers)

    # ── Vendors ────────────────────────────────────────────────────────────────
    vendors = [
        ("VND-001", "TechSupply Corp",       "sales@techsupply.com",    "+1-555-0201", "500 Vendor Way",    "Dallas",      "USA",     1),
        ("VND-002", "Global Hardware Inc",   "orders@globalhw.com",     "+1-555-0202", "200 Parts Blvd",    "Houston",     "USA",     1),
        ("VND-003", "ProOffice Supplies",    "info@prooffice.com",      "+44-20-8000", "45 Office Park",    "Manchester",  "UK",      1),
        ("VND-004", "NetworkPro Ltd",        "billing@networkpro.co",   "+1-555-0204", "1 Network Circle",  "Seattle",     "USA",     1),
        ("VND-005", "SafetyFirst Equipment", "contact@safetyfirst.com", "+1-555-0205", "90 Safety Ln",      "Denver",      "USA",     1),
        ("VND-006", "OldStock Traders",      "info@oldstock.com",       "+1-555-0206", "7 Warehouse Rd",    "Phoenix",     "USA",     0),  # Inactive
    ]
    cursor.executemany("""
        INSERT INTO Vendors (VendorCode,VendorName,Email,Phone,AddressLine1,City,Country,IsActive)
        VALUES (?,?,?,?,?,?,?,?)""", vendors)

    # ── Sites ──────────────────────────────────────────────────────────────────
    sites = [
        ("SITE-HQ",  "Headquarters",        "1 Corporate Plaza",    "New York",    "USA",        "America/New_York",    1),
        ("SITE-WH1", "Warehouse North",     "500 Storage Blvd",     "Chicago",     "USA",        "America/Chicago",     1),
        ("SITE-WH2", "Warehouse South",     "300 Logistics Ave",    "Atlanta",     "USA",        "America/New_York",    1),
        ("SITE-MFG", "Manufacturing Plant", "200 Factory Rd",       "Detroit",     "USA",        "America/Detroit",     1),
        ("SITE-LON", "London Office",       "10 Canary Wharf",      "London",      "UK",         "Europe/London",       1),
        ("SITE-OLD", "Decommissioned Depot","99 Old Rd",            "Cleveland",   "USA",        "America/New_York",    0),  # Inactive
    ]
    cursor.executemany("""
        INSERT INTO Sites (SiteCode,SiteName,AddressLine1,City,Country,TimeZone,IsActive)
        VALUES (?,?,?,?,?,?,?)""", sites)

    # ── Locations (SiteId references above, 1-indexed) ─────────────────────────
    # Site 1 = HQ, Site 2 = WH1, Site 3 = WH2, Site 4 = MFG, Site 5 = LON
    locations = [
        # HQ locations
        (1, "HQ-FL1",  "Floor 1 - Reception",     None),
        (1, "HQ-FL2",  "Floor 2 - IT Department", None),
        (1, "HQ-FL3",  "Floor 3 - Finance",        None),
        (1, "HQ-SRV",  "Server Room",              2),    # Child of Floor 2
        # WH1 locations
        (2, "WH1-A",   "Aisle A - Electronics",   None),
        (2, "WH1-B",   "Aisle B - Hardware",       None),
        (2, "WH1-C",   "Aisle C - Consumables",    None),
        # WH2 locations
        (3, "WH2-A",   "Aisle A - Furniture",      None),
        (3, "WH2-B",   "Aisle B - Heavy Equipment",None),
        # MFG locations
        (4, "MFG-L1",  "Production Line 1",        None),
        (4, "MFG-L2",  "Production Line 2",        None),
        (4, "MFG-STR", "Raw Materials Store",       None),
        # London
        (5, "LON-FL1", "Floor 1",                  None),
        (5, "LON-FL2", "Floor 2",                  None),
    ]
    cursor.executemany("""
        INSERT INTO Locations (SiteId,LocationCode,LocationName,ParentLocationId)
        VALUES (?,?,?,?)""", locations)

    # ── Items ──────────────────────────────────────────────────────────────────
    items = [
        ("ITM-LAP-001", "Dell Latitude 5540 Laptop",    "IT Equipment",  "Unit",  1),
        ("ITM-MON-001", "LG 27\" 4K Monitor",           "IT Equipment",  "Unit",  1),
        ("ITM-DSK-001", "Adjustable Standing Desk",     "Furniture",     "Unit",  1),
        ("ITM-CHR-001", "Ergonomic Office Chair",       "Furniture",     "Unit",  1),
        ("ITM-SWT-001", "Cisco Catalyst 2960 Switch",   "Networking",    "Unit",  1),
        ("ITM-CAB-001", "CAT6 Ethernet Cable 5m",       "Networking",    "Box",   1),
        ("ITM-PRN-001", "HP LaserJet Pro Printer",      "IT Equipment",  "Unit",  1),
        ("ITM-SRV-001", "Dell PowerEdge R750 Server",   "IT Equipment",  "Unit",  1),
        ("ITM-UPS-001", "APC Smart-UPS 3000VA",         "Power",        "Unit",  1),
        ("ITM-CAM-001", "IP Security Camera",           "Security",     "Unit",  1),
        ("ITM-PPR-001", "A4 Copy Paper (Box of 5 Reams)","Consumables", "Box",   1),
        ("ITM-INK-001", "Printer Ink Cartridge Set",    "Consumables",  "Set",   1),
        ("ITM-DISC-001","Legacy Storage Drive",         "IT Equipment",  "Unit",  0),  # Inactive
    ]
    cursor.executemany("""
        INSERT INTO Items (ItemCode,ItemName,Category,UnitOfMeasure,IsActive)
        VALUES (?,?,?,?,?)""", items)

    # ── Assets ─────────────────────────────────────────────────────────────────
    # (AssetTag, AssetName, SiteId, LocationId, SerialNumber, Category, Status, Cost, PurchaseDate, VendorId)
    assets = [
        # HQ Assets
        ("AST-0001", "Dell Laptop #1 - CEO",          1, 2,  "SN-DL-00001", "IT Equipment", "Active",    1299.99, "2023-01-15", 1),
        ("AST-0002", "Dell Laptop #2 - CFO",          1, 3,  "SN-DL-00002", "IT Equipment", "Active",    1299.99, "2023-01-15", 1),
        ("AST-0003", "Dell Laptop #3 - IT Admin",     1, 2,  "SN-DL-00003", "IT Equipment", "Active",    1299.99, "2023-02-10", 1),
        ("AST-0004", "LG Monitor #1",                 1, 2,  "SN-LG-00001", "IT Equipment", "Active",     549.00, "2023-02-10", 1),
        ("AST-0005", "LG Monitor #2",                 1, 3,  "SN-LG-00002", "IT Equipment", "Active",     549.00, "2023-02-10", 1),
        ("AST-0006", "Standing Desk - CEO Office",    1, 2,  None,           "Furniture",    "Active",     850.00, "2022-11-01", 3),
        ("AST-0007", "Ergonomic Chair - CFO",         1, 3,  None,           "Furniture",    "Active",     425.00, "2022-11-01", 3),
        ("AST-0008", "HP Printer - Reception",        1, 1,  "SN-HP-00001", "IT Equipment", "Active",     399.00, "2023-03-05", 1),
        ("AST-0009", "Dell Server #1 - Primary",      1, 4,  "SN-SRV-0001", "IT Equipment", "Active",    5499.00, "2022-06-20", 1),
        ("AST-0010", "APC UPS #1",                    1, 4,  "SN-APC-0001", "Power",        "Active",    1200.00, "2022-06-20", 1),
        ("AST-0011", "Cisco Switch - HQ Core",        1, 4,  "SN-CSC-0001", "Networking",   "Active",    3200.00, "2022-06-20", 4),
        ("AST-0012", "IP Camera - Floor 1 Lobby",     1, 1,  "SN-CAM-0001", "Security",     "Active",     280.00, "2023-05-01", 5),
        ("AST-0013", "IP Camera - Server Room",       1, 4,  "SN-CAM-0002", "Security",     "Active",     280.00, "2023-05-01", 5),
        # WH1 Assets
        ("AST-0014", "Dell Laptop #4 - WH1 Manager",  2, 5,  "SN-DL-00004", "IT Equipment", "Active",   1199.00, "2023-04-01", 1),
        ("AST-0015", "Cisco Switch - WH1",             2, 5,  "SN-CSC-0002", "Networking",   "Active",   1800.00, "2023-04-01", 4),
        ("AST-0016", "APC UPS - WH1",                  2, 5,  "SN-APC-0002", "Power",        "Active",    950.00, "2023-04-01", 1),
        ("AST-0017", "HP Printer - WH1 Office",        2, 5,  "SN-HP-00002", "IT Equipment", "Active",    399.00, "2023-04-15", 1),
        ("AST-0018", "Forklift Battery Charger",       2, 6,  "SN-FBC-0001", "Heavy Equip",  "Active",   2100.00, "2022-09-15", 2),
        # WH2 Assets
        ("AST-0019", "Dell Laptop #5 - WH2 Manager",  3, 9,  "SN-DL-00005", "IT Equipment", "Active",   1199.00, "2023-06-01", 1),
        ("AST-0020", "Pallet Jack #1",                 3, 9,  "SN-PJ-00001", "Heavy Equip",  "Active",    650.00, "2022-03-10", 2),
        ("AST-0021", "Pallet Jack #2",                 3, 9,  "SN-PJ-00002", "Heavy Equip",  "Maintenance","650.00","2022-03-10",2),
        # MFG Assets
        ("AST-0022", "CNC Machine #1",                 4, 10, "SN-CNC-0001", "Machinery",    "Active",  45000.00, "2021-01-10", 2),
        ("AST-0023", "CNC Machine #2",                 4, 11, "SN-CNC-0002", "Machinery",    "Active",  45000.00, "2021-01-10", 2),
        ("AST-0024", "Industrial Printer",             4, 10, "SN-IDP-0001", "IT Equipment", "Active",   2800.00, "2022-07-20", 1),
        ("AST-0025", "Safety Camera - MFG Line 1",    4, 10, "SN-CAM-0003", "Security",     "Active",    280.00, "2023-05-01", 5),
        # London Assets
        ("AST-0026", "Dell Laptop #6 - London",       5, 13, "SN-DL-00006", "IT Equipment", "Active",   1350.00, "2023-07-01", 1),
        ("AST-0027", "LG Monitor - London",            5, 13, "SN-LG-00003", "IT Equipment", "Active",    549.00, "2023-07-01", 1),
        ("AST-0028", "Ergonomic Chair - London",       5, 13, None,           "Furniture",    "Active",    425.00, "2023-07-01", 3),
        # Retired / Disposed
        ("AST-0029", "Old Dell Laptop - Retired",      1, 2,  "SN-DL-OLD01", "IT Equipment", "Disposed",  799.00, "2019-03-01", 1),
        ("AST-0030", "Legacy Server - Decommissioned", 1, 4,  "SN-SRV-OLD1", "IT Equipment", "Retired",  3200.00, "2018-06-15", 1),
        ("AST-0031", "Old Forklift",                   2, 6,  "SN-FL-OLD01", "Heavy Equip",  "Disposed", 15000.00,"2017-01-01", 2),
    ]
    cursor.executemany("""
        INSERT INTO Assets (AssetTag,AssetName,SiteId,LocationId,SerialNumber,Category,Status,Cost,PurchaseDate,VendorId)
        VALUES (?,?,?,?,?,?,?,?,?,?)""", assets)

    # ── Bills ──────────────────────────────────────────────────────────────────
    bills = [
        (1, "BILL-TC-2023-001", "2023-01-31", "2023-02-28",  8750.00, "USD", "Paid"),
        (1, "BILL-TC-2023-002", "2023-02-28", "2023-03-31",  3200.00, "USD", "Paid"),
        (1, "BILL-TC-2023-003", "2023-07-15", "2023-08-15",  5499.00, "USD", "Open"),
        (2, "BILL-GH-2023-001", "2023-02-10", "2023-03-10",  17650.00,"USD", "Paid"),
        (2, "BILL-GH-2023-002", "2023-09-01", "2023-10-01",  2750.00, "USD", "Open"),
        (3, "BILL-PO-2023-001", "2023-01-20", "2023-02-20",  2125.00, "USD", "Paid"),
        (3, "BILL-PO-2023-002", "2023-07-05", "2023-08-05",  1275.00, "USD", "Overdue"),
        (4, "BILL-NP-2023-001", "2023-02-15", "2023-03-15",  5000.00, "USD", "Paid"),
        (4, "BILL-NP-2023-002", "2023-04-01", "2023-05-01",  1800.00, "USD", "Open"),
        (5, "BILL-SF-2023-001", "2023-05-10", "2023-06-10",  2800.00, "USD", "Paid"),
        (5, "BILL-SF-2023-002", "2023-05-10", "2023-06-10",   840.00, "USD", "Overdue"),
    ]
    cursor.executemany("""
        INSERT INTO Bills (VendorId,BillNumber,BillDate,DueDate,TotalAmount,Currency,Status)
        VALUES (?,?,?,?,?,?,?)""", bills)

    # ── Purchase Orders ────────────────────────────────────────────────────────
    pos = [
        ("PO-2023-001", 1, "2023-01-05", "Closed",  1),
        ("PO-2023-002", 1, "2023-02-01", "Closed",  1),
        ("PO-2023-003", 2, "2023-02-01", "Closed",  2),
        ("PO-2023-004", 3, "2023-01-10", "Closed",  1),
        ("PO-2023-005", 4, "2023-02-10", "Closed",  1),
        ("PO-2023-006", 5, "2023-04-25", "Closed",  1),
        ("PO-2023-007", 1, "2023-07-01", "Open",    2),
        ("PO-2023-008", 2, "2023-08-15", "Open",    4),
        ("PO-2023-009", 4, "2023-09-01", "Pending", 5),
    ]
    cursor.executemany("""
        INSERT INTO PurchaseOrders (PONumber,VendorId,PODate,Status,SiteId)
        VALUES (?,?,?,?,?)""", pos)

    # ── PO Lines ───────────────────────────────────────────────────────────────
    po_lines = [
        (1, 1, "ITM-LAP-001", "Dell Latitude 5540 Laptop",    5.0, 1299.99),
        (1, 2, "ITM-MON-001", "LG 27\" 4K Monitor",           5.0,  549.00),
        (2, 1, "ITM-SRV-001", "Dell PowerEdge R750 Server",   1.0, 5499.00),
        (2, 2, "ITM-UPS-001", "APC Smart-UPS 3000VA",         1.0, 1200.00),
        (3, 1, "ITM-DSK-001", "Standing Desk",                10.0,  850.00),
        (3, 2, "ITM-CHR-001", "Ergonomic Office Chair",       10.0,  425.00),
        (4, 1, "ITM-SWT-001", "Cisco Catalyst 2960 Switch",   3.0, 1800.00),
        (5, 1, "ITM-CAM-001", "IP Security Camera",           6.0,  280.00),
        (6, 1, "ITM-PRN-001", "HP LaserJet Pro Printer",      2.0,  399.00),
        (7, 1, "ITM-LAP-001", "Dell Latitude 5540 Laptop",    2.0, 1299.99),
        (7, 2, "ITM-MON-001", "LG 27\" 4K Monitor",           2.0,  549.00),
        (8, 1, "ITM-UPS-001", "APC Smart-UPS 3000VA",         2.0,  950.00),
        (9, 1, "ITM-SWT-001", "Cisco Catalyst 2960 Switch",   2.0, 1800.00),
    ]
    cursor.executemany("""
        INSERT INTO PurchaseOrderLines (POId,LineNumber,ItemCode,Description,Quantity,UnitPrice)
        VALUES (?,?,?,?,?,?)""", po_lines)

    # ── Sales Orders ───────────────────────────────────────────────────────────
    sos = [
        ("SO-2023-001", 1, "2023-03-10", "Closed", 1),
        ("SO-2023-002", 2, "2023-04-05", "Closed", 2),
        ("SO-2023-003", 3, "2023-05-20", "Closed", 3),
        ("SO-2023-004", 4, "2023-06-15", "Open",   1),
        ("SO-2023-005", 1, "2023-08-01", "Open",   2),
        ("SO-2023-006", 5, "2023-09-10", "Pending",5),
    ]
    cursor.executemany("""
        INSERT INTO SalesOrders (SONumber,CustomerId,SODate,Status,SiteId)
        VALUES (?,?,?,?,?)""", sos)

    # ── SO Lines ───────────────────────────────────────────────────────────────
    so_lines = [
        (1, 1, "ITM-LAP-001", "Dell Latitude 5540 Laptop",  3.0, 1599.99),
        (1, 2, "ITM-MON-001", "LG 27\" 4K Monitor",         3.0,  699.00),
        (2, 1, "ITM-DSK-001", "Adjustable Standing Desk",   5.0,  999.00),
        (2, 2, "ITM-CHR-001", "Ergonomic Office Chair",     5.0,  550.00),
        (3, 1, "ITM-PRN-001", "HP LaserJet Pro Printer",    2.0,  499.00),
        (3, 2, "ITM-INK-001", "Printer Ink Cartridge Set", 10.0,   45.00),
        (4, 1, "ITM-CAM-001", "IP Security Camera",         4.0,  350.00),
        (4, 2, "ITM-SWT-001", "Cisco Catalyst 2960 Switch", 1.0, 2200.00),
        (5, 1, "ITM-LAP-001", "Dell Latitude 5540 Laptop",  2.0, 1599.99),
        (6, 1, "ITM-UPS-001", "APC Smart-UPS 3000VA",       1.0, 1499.00),
    ]
    cursor.executemany("""
        INSERT INTO SalesOrderLines (SOId,LineNumber,ItemCode,Description,Quantity,UnitPrice)
        VALUES (?,?,?,?,?,?)""", so_lines)

    # ── Asset Transactions ─────────────────────────────────────────────────────
    # (AssetId, FromLocationId, ToLocationId, TxnType, Quantity, TxnDate, Note)
    txns = [
        # Initial deployments (no FromLocation at acquisition)
        (1,  None, 2, "Deployment", 1, "2023-01-20", "CEO laptop deployed to IT dept"),
        (9,  None, 4, "Deployment", 1, "2022-06-25", "Primary server deployed to server room"),
        (22, None,10, "Deployment", 1, "2021-01-15", "CNC Machine #1 deployed to Line 1"),
        (23, None,11, "Deployment", 1, "2021-01-15", "CNC Machine #2 deployed to Line 2"),
        # Moves
        (4,  2,    3, "Transfer",   1, "2023-06-01", "Monitor moved from IT to Finance for temp use"),
        (7,  3,    1, "Transfer",   1, "2023-07-15", "CFO chair moved to reception temporarily"),
        (14, 5,    7, "Transfer",   1, "2023-08-10", "WH1 laptop moved to Aisle C for stocktake"),
        # Maintenance
        (21, 9,  None,"Maintenance",1, "2023-09-01", "Pallet jack #2 sent for service"),
        # Disposal
        (29, 2,  None,"Disposal",   1, "2023-01-10", "Old laptop wiped and disposed"),
        (31, 6,  None,"Disposal",   1, "2023-02-28", "Old forklift scrapped"),
    ]
    cursor.executemany("""
        INSERT INTO AssetTransactions (AssetId,FromLocationId,ToLocationId,TxnType,Quantity,TxnDate,Note)
        VALUES (?,?,?,?,?,?,?)""", txns)

    conn.commit()
    print("[OK] Seed data inserted successfully.")


def main():
    print(f"[SETUP] Setting up database at: {DB_PATH}")
    conn = get_connection()
    try:
        create_schema(conn)
        seed_data(conn)

        # Quick summary
        cursor = conn.cursor()
        tables = ["Customers", "Vendors", "Sites", "Locations", "Items",
                  "Assets", "Bills", "PurchaseOrders", "SalesOrders", "AssetTransactions"]
        print("\n[SUMMARY] Database Row Counts:")
        print(f"  {'Table':<25} {'Rows':>6}")
        print(f"  {'-'*32}")
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"  {table:<25} {count:>6}")
        print("\n[READY] Database is ready!")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
