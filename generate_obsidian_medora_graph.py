#!/usr/bin/env python3
"""
generate_obsidian_medora_graph.py
Generates the complete set of Obsidian Markdown files, Canvas, and Graph View configuration
for Project Medora's database schema and relations.
"""

import os
import json

def get_color_int(hex_str: str) -> int:
    return int(hex_str.lstrip('#'), 16)

# Color scheme definitions (Hex -> Decimal integer for Obsidian)
COLORS = {
    'emerald': '#10b981',   # Core Tables
    'fuchsia': '#d946ef',   # Junction / Assignment Tables
    'blue':    '#3b82f6',   # Catalogs / Lookups
    'cyan':    '#06b6d4',   # Clinical / Lab Results
    'rose':    '#f43f5e',   # Foreign Keys / Bridges
    'amber':   '#f59e0b',   # Attribute Clusters / Columns
    'indigo':  '#6366f1',   # Functional Domains / Modules
    'red':     '#ef4444',   # Security / Admin
}

GRAPH_CONFIG = {
    "collapse-filter": False,
    "search": "",
    "showTags": False,
    "showAttachments": False,
    "hideUnresolved": False,
    "showOrphans": True,
    "collapse-color-groups": False,
    "colorGroups": [
        {
            "query": "tag:#type/core-table",
            "color": {"a": 1, "rgb": get_color_int(COLORS['emerald'])}
        },
        {
            "query": "tag:#type/junction-table",
            "color": {"a": 1, "rgb": get_color_int(COLORS['fuchsia'])}
        },
        {
            "query": "tag:#type/catalog-table",
            "color": {"a": 1, "rgb": get_color_int(COLORS['blue'])}
        },
        {
            "query": "tag:#type/clinical-data",
            "color": {"a": 1, "rgb": get_color_int(COLORS['cyan'])}
        },
        {
            "query": "tag:#type/foreign-key",
            "color": {"a": 1, "rgb": get_color_int(COLORS['rose'])}
        },
        {
            "query": "tag:#type/attribute",
            "color": {"a": 1, "rgb": get_color_int(COLORS['amber'])}
        },
        {
            "query": "tag:#type/domain",
            "color": {"a": 1, "rgb": get_color_int(COLORS['indigo'])}
        },
        {
            "query": "tag:#type/security-table",
            "color": {"a": 1, "rgb": get_color_int(COLORS['red'])}
        }
    ],
    "collapse-display": False,
    "showArrow": True,
    "textFadeMultiplier": 0,
    "nodeSizeMultiplier": 1.45,
    "lineSizeMultiplier": 1.6,
    "collapse-forces": False,
    "centerStrength": 0.42,
    "repelStrength": 14.5,
    "linkStrength": 0.85,
    "linkDistance": 180,
    "scale": 1.0,
    "close": False
}

# ─── Individual Note Contents ──────────────────────────────────────────────────

NOTES = {
    "Medora Health Core.md": """---
tags:
  - type/domain
  - system/core
---
# 🏥 Medora Health Database Architecture
Central hub unifying patient records, diagnostic laboratory analytics, clinical consultations, and hospital administration.

### Functional Domains
- [[Domain - Patient Care]]
- [[Domain - Clinical Pathology]]
- [[Domain - Healthcare Providers]]
- [[Domain - System Administration]]

### Core Relational Entities
- [[patient_details]] — Master Patient Demographic & Auth Registry
- [[doctor_catalog]] — Medical Specialist & Physician Catalog
- [[tests_catalog]] — Diagnostic Lab Test Directory
- [[admin_users]] — Administrative & Security Control

### Transactional & Junction Tables
- [[blood_test_results]] — Complete Haematology Test Telemetry
- [[tests_assigned]] — Diagnostic Order & Execution Queue
- [[patient_doctor_assignment]] — Patient-Doctor Care Team Mapping

#type/domain
""",

    "patient_details.md": """---
tags:
  - type/core-table
  - schema/entity
---
# 👤 Table: patient_details
Primary entity capturing all registered patients, demographic data, and patient-portal credentials.

### Primary Key
- `PatID` INT AUTO_INCREMENT

### Relational Links & Foreign Key Bridges
- [[PatID (Foreign Key Bridge)]]
- [[blood_test_results]] (1 : N via PatID, ON DELETE CASCADE)
- [[tests_assigned]] (1 : N via PatID, ON DELETE CASCADE)
- [[patient_doctor_assignment]] (1 : N via PatID, ON DELETE CASCADE)

### Attributes & Schema Fields
- [[Patient Demographics & Vitals]]
- [[Patient Portal Credentials]]

### Domain Context
- [[Domain - Patient Care]]
- [[Medora Health Core]]

#type/core-table
""",

    "blood_test_results.md": """---
tags:
  - type/clinical-data
  - schema/entity
---
# 🔬 Table: blood_test_results
Stores full clinical blood panel analytics, complete blood counts (CBC), and differential leukocyte counts.

### Primary Key & Foreign Keys
- `ResultID` INT AUTO_INCREMENT (PK)
- `PatID` INT (FK -> [[patient_details]])
- [[PatID (Foreign Key Bridge)]]

### Relational Links
- [[patient_details]]
- [[tests_assigned]]

### Clinical Data Attributes
- [[Blood Biomarkers & Differential]]

### Domain Context
- [[Domain - Clinical Pathology]]
- [[Medora Health Core]]

#type/clinical-data
""",

    "tests_catalog.md": """---
tags:
  - type/catalog-table
  - schema/entity
---
# 🧪 Table: tests_catalog
Master repository of diagnostic lab procedures offered by Medora, containing categories, descriptions, and fee structures.

### Primary Key
- `TestID` INT AUTO_INCREMENT (PK)

### Relational Links & Foreign Key Bridges
- [[TestID (Foreign Key Bridge)]]
- [[tests_assigned]] (1 : N via TestID, ON DELETE CASCADE)

### Attributes & Details
- [[Diagnostic Tests & Tariff]]

### Domain Context
- [[Domain - Clinical Pathology]]
- [[Medora Health Core]]

#type/catalog-table
""",

    "tests_assigned.md": """---
tags:
  - type/junction-table
  - schema/entity
---
# 📋 Table: tests_assigned
Junction entity bridging Patients with Diagnostic Catalog tests to manage lab test ordering, schedule tracking, and execution status.

### Primary Key & Foreign Keys
- `AssignID` INT AUTO_INCREMENT (PK)
- `PatID` INT (FK -> [[patient_details]])
- `TestID` INT (FK -> [[tests_catalog]])
- [[PatID (Foreign Key Bridge)]]
- [[TestID (Foreign Key Bridge)]]

### Interconnected Tables
- [[patient_details]]
- [[tests_catalog]]
- [[blood_test_results]]

### Operational Tracking
- [[Lab Order Workflow & Status]]

### Domain Context
- [[Domain - Clinical Pathology]]
- [[Domain - Patient Care]]

#type/junction-table
""",

    "doctor_catalog.md": """---
tags:
  - type/catalog-table
  - schema/entity
---
# 👨‍⚕️ Table: doctor_catalog
Comprehensive master registry of certified medical doctors, specialities, clinical experience, and credentials.

### Primary Key
- `DoctorID` INT AUTO_INCREMENT (PK)

### Relational Links & Foreign Key Bridges
- [[DoctorID (Foreign Key Bridge)]]
- [[patient_doctor_assignment]] (1 : N via DoctorID, ON DELETE CASCADE)

### Credentials & Details
- [[Physician Specialities & Credentials]]

### Domain Context
- [[Domain - Healthcare Providers]]
- [[Medora Health Core]]

#type/catalog-table
""",

    "patient_doctor_assignment.md": """---
tags:
  - type/junction-table
  - schema/entity
---
# 🤝 Table: patient_doctor_assignment
Junction table mapping patients to their attending physicians and medical specialists with clinical notes and appointment assignment dates.

### Primary Key & Foreign Keys
- `AssignID` INT AUTO_INCREMENT (PK)
- `PatID` INT (FK -> [[patient_details]])
- `DoctorID` INT (FK -> [[doctor_catalog]])
- [[PatID (Foreign Key Bridge)]]
- [[DoctorID (Foreign Key Bridge)]]

### Interconnected Tables
- [[patient_details]]
- [[doctor_catalog]]

### Consultation Context
- [[Consultation Schedule & Care Notes]]

### Domain Context
- [[Domain - Healthcare Providers]]
- [[Domain - Patient Care]]

#type/junction-table
""",

    "admin_users.md": """---
tags:
  - type/security-table
  - schema/entity
---
# 🔐 Table: admin_users
Security and access control entity managing system administrators, credentials, and role-based permissions.

### Primary Key
- `AdminID` INT AUTO_INCREMENT (PK)

### Security & Privileges
- [[Role-Based Access Control (Admin)]]

### Governed System
- [[Medora Health Core]]
- [[Domain - System Administration]]
- [[patient_details]] (Administrative Overrides)

#type/security-table
""",

    "PatID (Foreign Key Bridge).md": """---
tags:
  - type/foreign-key
---
# 🔑 Foreign Key Bridge: PatID
Central integrity constraint linking the primary patient identity record to downstream clinical and scheduling events.

### Source Entity
- [[patient_details]] (Primary Key: `PatID`)

### Cascading Target Relations
- [[blood_test_results]] (`FOREIGN KEY (PatID) REFERENCES patient_details(PatID)`)
- [[tests_assigned]] (`FOREIGN KEY (PatID) REFERENCES patient_details(PatID)`)
- [[patient_doctor_assignment]] (`FOREIGN KEY (PatID) REFERENCES patient_details(PatID)`)

#type/foreign-key
""",

    "DoctorID (Foreign Key Bridge).md": """---
tags:
  - type/foreign-key
---
# 🔑 Foreign Key Bridge: DoctorID
Relational bridge linking doctor profiles to clinical assignments.

### Source Entity
- [[doctor_catalog]] (Primary Key: `DoctorID`)

### Cascading Target Relation
- [[patient_doctor_assignment]] (`FOREIGN KEY (DoctorID) REFERENCES doctor_catalog(DoctorID)`)

#type/foreign-key
""",

    "TestID (Foreign Key Bridge).md": """---
tags:
  - type/foreign-key
---
# 🔑 Foreign Key Bridge: TestID
Relational bridge linking test catalog definitions to patient lab orders.

### Source Entity
- [[tests_catalog]] (Primary Key: `TestID`)

### Cascading Target Relation
- [[tests_assigned]] (`FOREIGN KEY (TestID) REFERENCES tests_catalog(TestID)`)

#type/foreign-key
""",

    "Blood Biomarkers & Differential.md": """---
tags:
  - type/attribute
---
# 🩸 Blood Biomarkers & Differential
Clinical diagnostic attributes measured in haematological testing:
- **CBC**: `RBC`, `WBC`, `Platelets`, `Haemoglobin`, `TLC`
- **DLC**: `Neutrophils`, `Lymphocytes`, `Eosinophils`, `Basophils`, `Monocytes`
- **Metadata**: `TestDate`

Connected Table: [[blood_test_results]]

#type/attribute
""",

    "Patient Demographics & Vitals.md": """---
tags:
  - type/attribute
---
# 📋 Patient Demographics & Vitals
Identity and demographic characteristics:
- `PatName` (VARCHAR 100)
- `MobileNumber` (VARCHAR 15)
- `Address` (TEXT)
- `Age` (INT), `DOB` (DATE), `Weight` (DECIMAL)

Connected Table: [[patient_details]]

#type/attribute
""",

    "Patient Portal Credentials.md": """---
tags:
  - type/attribute
---
# 🔑 Patient Portal Credentials
Authentication attributes for patient portal access:
- `LoginID` (VARCHAR 50 UNIQUE)
- `Password` (VARCHAR 255 SHA-256)

Connected Table: [[patient_details]]

#type/attribute
""",

    "Physician Specialities & Credentials.md": """---
tags:
  - type/attribute
---
# 🩺 Physician Specialities & Credentials
Professional credentials and medical competencies:
- `DoctorName`, `Speciality`, `YearsExperience`, `Qualification`, `ContactNumber`

Connected Table: [[doctor_catalog]]

#type/attribute
""",

    "Diagnostic Tests & Tariff.md": """---
tags:
  - type/attribute
---
# 💵 Diagnostic Tests & Tariff
Test catalog specifications and fee schedules:
- `TestName`, `Category`, `Price` (INR), `Description`

Connected Table: [[tests_catalog]]

#type/attribute
""",

    "Lab Order Workflow & Status.md": """---
tags:
  - type/attribute
---
# ⏱️ Lab Order Workflow & Status
Tracking lifecycle and audit details for prescribed tests:
- `AssignDate`, `Status` (Pending, Completed, Cancelled), `Notes`

Connected Table: [[tests_assigned]]

#type/attribute
""",

    "Consultation Schedule & Care Notes.md": """---
tags:
  - type/attribute
---
# 📝 Consultation Schedule & Care Notes
Doctor consultation scheduling and medical assessment notes:
- `AssignDate`, `Notes`

Connected Table: [[patient_doctor_assignment]]

#type/attribute
""",

    "Role-Based Access Control (Admin).md": """---
tags:
  - type/attribute
---
# 🛡️ Role-Based Access Control (Admin)
System privileges and security tokens:
- `Username`, `Password` (SHA-256 Hash), `FullName`, `Role` (SuperAdmin)

Connected Table: [[admin_users]]

#type/attribute
""",

    "Domain - Patient Care.md": """---
tags:
  - type/domain
---
# 🏥 Domain: Patient Care
Covers patient registration, health history, medical appointments, and physician care teams.

### Included Tables & Hubs
- [[patient_details]]
- [[patient_doctor_assignment]]
- [[Medora Health Core]]

#type/domain
""",

    "Domain - Clinical Pathology.md": """---
tags:
  - type/domain
---
# 🔬 Domain: Clinical Pathology
Manages laboratory orders, test catalog definitions, haematology analysis, and diagnostics telemetry.

### Included Tables & Hubs
- [[blood_test_results]]
- [[tests_assigned]]
- [[tests_catalog]]
- [[Medora Health Core]]

#type/domain
""",

    "Domain - Healthcare Providers.md": """---
tags:
  - type/domain
---
# 🩺 Domain: Healthcare Providers
Encompasses doctor profiles, clinical qualifications, specialties, and doctor-patient consultations.

### Included Tables & Hubs
- [[doctor_catalog]]
- [[patient_doctor_assignment]]
- [[Medora Health Core]]

#type/domain
""",

    "Domain - System Administration.md": """---
tags:
  - type/domain
---
# 🛡️ Domain: System Administration
Oversees user authentication, database security, audit logging, and administrative governance.

### Included Tables & Hubs
- [[admin_users]]
- [[Medora Health Core]]

#type/domain
"""
}

# ─── Master Markdown File for Obsidian (Rendered + Links) ──────────────────────

MASTER_MARKDOWN = """# 🏥 Project Medora — Database Relational Architecture & Graph

> [!NOTE] 
> **Obsidian Graph View Ready**: Open Obsidian's **Graph View** (`Cmd+G` / `Ctrl+G`) to view the interactive physics constellation with custom color coding, directional relationship arrows, and cluster gravity.

---

## 🌌 Visual ER Entity-Relationship Diagram

```mermaid
erDiagram
    PATIENT_DETAILS ||--o{ BLOOD_TEST_RESULTS : "has blood tests (PatID)"
    PATIENT_DETAILS ||--o{ TESTS_ASSIGNED : "assigned tests (PatID)"
    PATIENT_DETAILS ||--o{ PATIENT_DOCTOR_ASSIGNMENT : "consults with (PatID)"
    DOCTOR_CATALOG ||--o{ PATIENT_DOCTOR_ASSIGNMENT : "attends to (DoctorID)"
    TESTS_CATALOG ||--o{ TESTS_ASSIGNED : "catalog definition (TestID)"
    ADMIN_USERS ||--o{ MEDORA_CORE : "manages & configures"

    PATIENT_DETAILS {
        int PatID PK "Auto Increment"
        string PatName "Patient Full Name"
        string MobileNumber "Contact Number"
        text Address "Residential Address"
        int Age "Age in Years"
        date DOB "Date of Birth"
        decimal Weight "Weight in kg"
        string LoginID UK "Patient Portal Login"
        string Password "SHA-256 Digest"
    }

    BLOOD_TEST_RESULTS {
        int ResultID PK "Auto Increment"
        int PatID FK "References patient_details"
        date TestDate "Date of Examination"
        decimal RBC "Red Blood Cells (10^12/L)"
        decimal WBC "White Blood Cells (10^9/L)"
        decimal Haemoglobin "Haemoglobin (g/dL)"
        decimal Platelets "Platelets (10^9/L)"
        decimal TLC "Total Leukocyte Count"
        decimal Neutrophils "Neutrophils %"
        decimal Lymphocytes "Lymphocytes %"
        decimal Eosinophils "Eosinophils %"
        decimal Basophils "Basophils %"
        decimal Monocytes "Monocytes %"
    }

    TESTS_CATALOG {
        int TestID PK "Auto Increment"
        string TestName "Test Name"
        text Description "Clinical Purpose"
        string Category "Pathology / Biochemistry"
        decimal Price "Test Fee in INR"
    }

    TESTS_ASSIGNED {
        int AssignID PK "Auto Increment"
        int PatID FK "References patient_details"
        int TestID FK "References tests_catalog"
        date AssignDate "Prescription Date"
        string Status "Pending | Completed | Cancelled"
        text Notes "Clinical Instructions"
    }

    DOCTOR_CATALOG {
        int DoctorID PK "Auto Increment"
        string DoctorName "Full Physician Name"
        string Speciality "Medical Specialty"
        int YearsExperience "Clinical Practice"
        string Qualification "Degrees & Certifications"
        string ContactNumber "Direct Contact"
    }

    PATIENT_DOCTOR_ASSIGNMENT {
        int AssignID PK "Auto Increment"
        int PatID FK "References patient_details"
        int DoctorID FK "References doctor_catalog"
        date AssignDate "Consultation Date"
        text Notes "Clinical Summary"
    }

    ADMIN_USERS {
        int AdminID PK "Auto Increment"
        string Username UK "Admin Login"
        string Password "SHA-256 Digest"
        string FullName "Administrator Name"
        string Role "Role: SuperAdmin"
    }
```

---

## 🕸️ Relational Topology Map (Obsidian Graph Nodes)

```mermaid
flowchart TD
    classDef core fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff;
    classDef junction fill:#d946ef,stroke:#c026d3,stroke-width:2px,color:#fff;
    classDef catalog fill:#3b82f6,stroke:#2563eb,stroke-width:2px,color:#fff;
    classDef clinical fill:#06b6d4,stroke:#0891b2,stroke-width:2px,color:#fff;
    classDef security fill:#ef4444,stroke:#dc2626,stroke-width:2px,color:#fff;
    classDef bridge fill:#f43f5e,stroke:#e11d48,stroke-width:2px,color:#fff;
    classDef domain fill:#6366f1,stroke:#4f46e5,stroke-width:2px,color:#fff;

    Hub["🏥 Medora Health Core"]:::domain

    subgraph PATIENTS ["Patient Care Subsystem"]
        P["👤 patient_details"]:::core
        P_ATTR["📋 Demographics & Auth"]
        P_FK["🔑 PatID Bridge"]:::bridge
    end

    subgraph PATHOLOGY ["Diagnostics & Pathology Subsystem"]
        B["🔬 blood_test_results"]:::clinical
        B_ATTR["🩸 Haematology & DLC Panel"]
        TC["🧪 tests_catalog"]:::catalog
        TC_ATTR["💵 Tests & Pricing"]
        TA["📋 tests_assigned"]:::junction
        TA_ATTR["⏱️ Order Workflow"]
        T_FK["🔑 TestID Bridge"]:::bridge
    end

    subgraph CLINICAL ["Healthcare Providers Subsystem"]
        D["👨‍⚕️ doctor_catalog"]:::catalog
        D_ATTR["🩺 Qualifications & Specialties"]
        PDA["🤝 patient_doctor_assignment"]:::junction
        PDA_ATTR["📝 Care Notes & Schedule"]
        D_FK["🔑 DoctorID Bridge"]:::bridge
    end

    subgraph ADMIN ["Administration Subsystem"]
        ADM["🔐 admin_users"]:::security
        ADM_ATTR["🛡️ RBAC Permissions"]
    end

    %% Hub Connections
    Hub --> P
    Hub --> D
    Hub --> TC
    Hub --> ADM

    %% Patient Connections
    P --> P_ATTR
    P --> P_FK
    P_FK -->|CASCADE 1:N| B
    P_FK -->|CASCADE 1:N| TA
    P_FK -->|CASCADE 1:N| PDA

    %% Pathology Connections
    B --> B_ATTR
    TC --> TC_ATTR
    TC --> T_FK
    T_FK -->|CASCADE 1:N| TA
    TA --> TA_ATTR
    TA -.->|Correlated Telemetry| B

    %% Doctor Connections
    D --> D_ATTR
    D --> D_FK
    D_FK -->|CASCADE 1:N| PDA
    PDA --> PDA_ATTR

    %% Admin Connections
    ADM --> ADM_ATTR
    ADM -.->|System Audit| P
```

---

## 🔗 Obsidian Interconnected Graph Index

### 🟢 Master & Core Tables
- [[patient_details]] — Primary Patient Entity `#type/core-table`
- [[doctor_catalog]] — Medical Doctor Directory `#type/catalog-table`
- [[tests_catalog]] — Pathology & Diagnostic Test Directory `#type/catalog-table`
- [[admin_users]] — System Security & Admin Auth `#type/security-table`

### 🟣 Relational Junction Tables
- [[patient_doctor_assignment]] — Patient-to-Doctor Mapping (PatID + DoctorID) `#type/junction-table`
- [[tests_assigned]] — Diagnostic Lab Orders (PatID + TestID) `#type/junction-table`

### 🔵 Clinical & Laboratory Results
- [[blood_test_results]] — CBC & Differential Blood Metrics `#type/clinical-data`

### 🔴 Foreign Key Bridges (Integrity Connectors)
- [[PatID (Foreign Key Bridge)]] — 1:N Cascade to Results, Orders, and Doctor Assignments `#type/foreign-key`
- [[DoctorID (Foreign Key Bridge)]] — 1:N Cascade to Patient Doctor Assignments `#type/foreign-key`
- [[TestID (Foreign Key Bridge)]] — 1:N Cascade to Test Orders `#type/foreign-key`

### 🟡 Attribute & Field Clusters
- [[Patient Demographics & Vitals]] `#type/attribute`
- [[Patient Portal Credentials]] `#type/attribute`
- [[Blood Biomarkers & Differential]] `#type/attribute`
- [[Diagnostic Tests & Tariff]] `#type/attribute`
- [[Physician Specialities & Credentials]] `#type/attribute`
- [[Lab Order Workflow & Status]] `#type/attribute`
- [[Consultation Schedule & Care Notes]] `#type/attribute`
- [[Role-Based Access Control (Admin)]] `#type/attribute`

### 🟣 System Modules & Domains
- [[Medora Health Core]] `#type/domain`
- [[Domain - Patient Care]] `#type/domain`
- [[Domain - Clinical Pathology]] `#type/domain`
- [[Domain - Healthcare Providers]] `#type/domain`
- [[Domain - System Administration]] `#type/domain`

---
*Created for Medora Clinical Management System — MySQL Database Topology in Obsidian Graph View.*
"""

# ─── Obsidian Canvas File (.canvas) ────────────────────────────────────────────

CANVAS_DATA = {
    "nodes": [
        {
            "id": "hub_node",
            "type": "text",
            "text": "## 🏥 MEDORA HEALTH DATABASE\n**Relational Architecture & Clinical Schema**\n*MySQL Engine: InnoDB | Charset: UTF8MB4*",
            "x": 350,
            "y": -180,
            "width": 420,
            "height": 110,
            "color": "6"
        },
        {
            "id": "patient_details_node",
            "type": "text",
            "text": "### 👤 patient_details `[Core Master]`\n---\n- **PatID** `INT AUTO_INCREMENT` **[PK]**\n- `PatName` VARCHAR(100)\n- `MobileNumber` VARCHAR(15)\n- `Address` TEXT\n- `Age` INT\n- `DOB` DATE\n- `Weight` DECIMAL(5,2)\n- `LoginID` VARCHAR(50) [UNIQUE]\n- `Password` VARCHAR(255) [SHA-256]",
            "x": 0,
            "y": 60,
            "width": 320,
            "height": 290,
            "color": "4"
        },
        {
            "id": "doctor_catalog_node",
            "type": "text",
            "text": "### 👨‍⚕️ doctor_catalog `[Master Catalog]`\n---\n- **DoctorID** `INT AUTO_INCREMENT` **[PK]**\n- `DoctorName` VARCHAR(100)\n- `Speciality` VARCHAR(100)\n- `YearsExperience` INT\n- `Qualification` VARCHAR(200)\n- `ContactNumber` VARCHAR(15)",
            "x": 800,
            "y": 60,
            "width": 320,
            "height": 240,
            "color": "5"
        },
        {
            "id": "tests_catalog_node",
            "type": "text",
            "text": "### 🧪 tests_catalog `[Service Catalog]`\n---\n- **TestID** `INT AUTO_INCREMENT` **[PK]**\n- `TestName` VARCHAR(100)\n- `Category` VARCHAR(50)\n- `Price` DECIMAL(8,2)\n- `Description` TEXT",
            "x": 800,
            "y": 420,
            "width": 320,
            "height": 220,
            "color": "5"
        },
        {
            "id": "patient_doctor_assignment_node",
            "type": "text",
            "text": "### 🤝 patient_doctor_assignment `[Junction]`\n---\n- **AssignID** `INT AUTO_INCREMENT` **[PK]**\n- *PatID* `INT` **[FK -> patient_details]**\n- *DoctorID* `INT` **[FK -> doctor_catalog]**\n- `AssignDate` DATE\n- `Notes` TEXT\n*(ON DELETE CASCADE)*",
            "x": 400,
            "y": 140,
            "width": 320,
            "height": 210,
            "color": "3"
        },
        {
            "id": "tests_assigned_node",
            "type": "text",
            "text": "### 📋 tests_assigned `[Junction]`\n---\n- **AssignID** `INT AUTO_INCREMENT` **[PK]**\n- *PatID* `INT` **[FK -> patient_details]**\n- *TestID* `INT` **[FK -> tests_catalog]**\n- `AssignDate` DATE\n- `Status` VARCHAR(20) [Pending|Done]\n- `Notes` TEXT\n*(ON DELETE CASCADE)*",
            "x": 400,
            "y": 430,
            "width": 320,
            "height": 230,
            "color": "3"
        },
        {
            "id": "blood_test_results_node",
            "type": "text",
            "text": "### 🔬 blood_test_results `[Clinical Telemetry]`\n---\n- **ResultID** `INT AUTO_INCREMENT` **[PK]**\n- *PatID* `INT` **[FK -> patient_details]**\n- `TestDate` DATE\n- **CBC**: `RBC`, `WBC`, `Platelets`, `Haemoglobin`, `TLC`\n- **DLC**: `Neutrophils`, `Lymphocytes`, `Eosinophils`, `Basophils`, `Monocytes`\n*(ON DELETE CASCADE)*",
            "x": 0,
            "y": 430,
            "width": 340,
            "height": 250,
            "color": "5"
        },
        {
            "id": "admin_users_node",
            "type": "text",
            "text": "### 🔐 admin_users `[System Administration]`\n---\n- **AdminID** `INT AUTO_INCREMENT` **[PK]**\n- `Username` VARCHAR(50) [UNIQUE]\n- `Password` VARCHAR(255) [SHA-256]\n- `FullName` VARCHAR(100)\n- `Role` VARCHAR(50) [SuperAdmin]",
            "x": 400,
            "y": 740,
            "width": 320,
            "height": 200,
            "color": "1"
        }
    ],
    "edges": [
        {
            "id": "e_hub_p",
            "fromNode": "hub_node",
            "fromSide": "left",
            "toNode": "patient_details_node",
            "toSide": "top",
            "fromEnd": "none",
            "toEnd": "arrow",
            "label": "Master Patient Registry"
        },
        {
            "id": "e_hub_d",
            "fromNode": "hub_node",
            "fromSide": "right",
            "toNode": "doctor_catalog_node",
            "toSide": "top",
            "fromEnd": "none",
            "toEnd": "arrow",
            "label": "Provider Registry"
        },
        {
            "id": "e_pat_blood",
            "fromNode": "patient_details_node",
            "fromSide": "bottom",
            "toNode": "blood_test_results_node",
            "toSide": "top",
            "fromEnd": "none",
            "toEnd": "arrow",
            "label": "1 : N (PatID CASCADE)"
        },
        {
            "id": "e_pat_pda",
            "fromNode": "patient_details_node",
            "fromSide": "right",
            "toNode": "patient_doctor_assignment_node",
            "toSide": "left",
            "fromEnd": "none",
            "toEnd": "arrow",
            "label": "1 : N (PatID CASCADE)"
        },
        {
            "id": "e_doc_pda",
            "fromNode": "doctor_catalog_node",
            "fromSide": "left",
            "toNode": "patient_doctor_assignment_node",
            "toSide": "right",
            "fromEnd": "none",
            "toEnd": "arrow",
            "label": "1 : N (DoctorID CASCADE)"
        },
        {
            "id": "e_pat_tests",
            "fromNode": "patient_details_node",
            "fromSide": "bottom",
            "toNode": "tests_assigned_node",
            "toSide": "left",
            "fromEnd": "none",
            "toEnd": "arrow",
            "label": "1 : N (PatID CASCADE)"
        },
        {
            "id": "e_cat_tests",
            "fromNode": "tests_catalog_node",
            "fromSide": "left",
            "toNode": "tests_assigned_node",
            "toSide": "right",
            "fromEnd": "none",
            "toEnd": "arrow",
            "label": "1 : N (TestID CASCADE)"
        },
        {
            "id": "e_tests_blood",
            "fromNode": "tests_assigned_node",
            "fromSide": "left",
            "toNode": "blood_test_results_node",
            "toSide": "right",
            "fromEnd": "none",
            "toEnd": "arrow",
            "label": "Generates Diagnostics"
        },
        {
            "id": "e_adm_sys",
            "fromNode": "admin_users_node",
            "fromSide": "top",
            "toNode": "hub_node",
            "toSide": "bottom",
            "fromEnd": "none",
            "toEnd": "arrow",
            "label": "Governs & Audits System"
        }
    ]
}

def deploy(target_dir: str, is_vault: bool = True):
    os.makedirs(target_dir, exist_ok=True)
    
    # 1. Write individual note files
    for filename, content in NOTES.items():
        filepath = os.path.join(target_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
    # 2. Write master markdown file
    master_path = os.path.join(target_dir, "Medora_Database_Relations.md")
    with open(master_path, 'w', encoding='utf-8') as f:
        f.write(MASTER_MARKDOWN)
        
    # 3. Write Obsidian Canvas file
    canvas_path = os.path.join(target_dir, "Medora_Database_Schema.canvas")
    with open(canvas_path, 'w', encoding='utf-8') as f:
        json.dump(CANVAS_DATA, f, indent=2)

    # 4. If target is a vault, configure .obsidian/graph.json
    if is_vault:
        obsidian_dir = os.path.join(target_dir, ".obsidian")
        os.makedirs(obsidian_dir, exist_ok=True)
        graph_path = os.path.join(obsidian_dir, "graph.json")
        with open(graph_path, 'w', encoding='utf-8') as f:
            json.dump(GRAPH_CONFIG, f, indent=2)
            
    print(f"[SUCCESS] Deployed files to: {target_dir}")

if __name__ == '__main__':
    # 1. Deploy directly into the active Obsidian vault
    active_vault = "/Users/bhardwajprasad/Documents/Obsidian/Notes"
    deploy(active_vault, is_vault=True)
    
    # 2. Deploy into Project Medora folder
    project_dir = "/Users/bhardwajprasad/Desktop/project medora"
    deploy(os.path.join(project_dir, "Medora_Obsidian_Vault"), is_vault=True)
    
    # Also write master markdown directly into project root
    with open(os.path.join(project_dir, "Medora_Database_Relations.md"), 'w', encoding='utf-8') as f:
        f.write(MASTER_MARKDOWN)
    with open(os.path.join(project_dir, "Medora_Database_Schema.canvas"), 'w', encoding='utf-8') as f:
        json.dump(CANVAS_DATA, f, indent=2)
    print("[SUCCESS] Project Medora root files updated.")
