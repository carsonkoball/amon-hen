# amon-hen
A collection of tools for monitoring data sources to support investment research.

Named after *Amon Hen*, a location in J.R.R. Tolkien's *The Lord of the Rings*.  The name is Sindarin and is usually translated as "Hill of Sight", but more literally "Hill of the Eye", from *amon* ("hill") and *hen* ("eye"). See [Amon Hen on Tolkien Gateway](https://tolkiengateway.net/wiki/Amon_Hen).

See [case_studies.md](docs/case_studies.md) for past examples of the tools working effectively.


## Table of Contents
-   [Tools Overview](#tools-overview)
-   [User Interface](#user-interface)
-   [Structure](#structure)
-   [Installation](#installation)
-	[Future Work](#future-work)

## Tools Overview
### adp_tracker
Monitors the Automatic Data Processing, Inc. (ADP) Career Center for a user-specified company.
- Tracks new, removed, and modified job postings
- Archives job postings locally

### blue_list_tracker
Monitors the Defense Contract Management Agency (DCMA) Blue Unmanned Aircraft Systems (UAS) List.
- Tracks new, removed, and modified Blue UAS Cleared listings
- Archives Blue UAS Cleared listings locally
- Tracks new, removed, and modified Blue UAS Framework listings
- Archives Blue UAS Framework listings locally

### diu_pathway_tracker
Monitors the Defense Innovation Unit (DIU) solicitation pathways page.
- Tracks new, removed, and modified Commercial Solutions Openings (CSO) pathways
- Archives CSO pathways locally
- Tracks new, removed, and modified Challenges or Commercial Acceleration Opportunities (CCAO) pathways
- Archives CCAO pathways locally

### dow_parser
Monitors the Department of War (DoW) daily contract announcements page.
- Parses awarded company names

### fcc_els_parser
Monitors the Federal Communications Commission (FCC) Experimental Licensing System (ELS) application page.
- Parses application information

### fedramp_tracker
Monitors the Federal Risk and Authorization Management Program (FedRAMP) marketplace.
- Tracks new, removed, and modified products
- Archives product listings locally
- Tracks new, removed, and modified agencies
- Archives agency listings locally
- Tracks new, removed, and modified assessors
- Archives assessor listings locally
- Tracks new, removed, and modified advisors
- Archives advisor listings locally

### navy_sbir_sttr_parser
Monitors the Navy Small Business Innovation Research (SBIR) and Small Business Technology Transfer (STTR) awards and success stories page.
- Parses SBIR award information
- Parses STTR award information

### Common Utilities
#### crawler
Automated web crawler

#### filesystem
Filesystem operations

#### http
HTTP request helpers

#### log_config
Logging configuration

#### tracker
Structured data monitoring

## User Interface
### amon_hen_ui
Browser-based user interface

## Structure
```
amon-hen/
├── docs/
│   └── case_studies.md
├── src/
│   └── amon_hen/
│       ├── common/
│       │   ├── config_crawler.py
│       │   ├── crawler.py
│       │   ├── filesystem.py
│       │   ├── http.py
│       │   ├── log_config.py
│       │   └── tracker.py
│       └── tools/
│           ├── adp_tracker/
│           │   ├── __init__.py
│           │   ├── __main__.py
│           │   ├── config.py
│           │   └── adp_tracker.py
│           ├── blue_list_tracker/
│           │   ├── __init__.py
│           │   ├── __main__.py
│           │   ├── config.py
│           │   └── blue_list_tracker.py
│           ├── diu_pathway_tracker/
│           │   ├── __init__.py
│           │   ├── __main__.py
│           │   ├── config.py
│           │   └── diu_pathway_tracker.py
│           ├── dow_parser/
│           │   ├── __init__.py
│           │   ├── __main__.py
│           │   ├── config.py
│           │   └── dow_parser.py
│           ├── fcc_els_parser/
│           │   ├── __init__.py
│           │   ├── __main__.py
│           │   ├── config.py
│           │   └── fcc_els_parser.py
│           ├── fedramp_tracker/
│           │   ├── __init__.py
│           │   ├── __main__.py
│           │   ├── config.py
│           │   └── fedramp_tracker.py
│           └── navy_sbir_sttr_parser/
│               ├── __init__.py
│               ├── __main__.py
│               ├── config.py
│               └── navy_sbir_sttr_parser.py
├── ui/
│   ├── handlers/
│   │   ├── __init__.py
│   │   ├── adp_tracker.py
│   │   ├── blue_list_tracker.py
│   │   ├── diu_pathway_tracker.py
│   │   ├── dow_parser.py
│   │   ├── fcc_els_parser.py
│   │   └── navy_sbir_sttr_parser.py
│   ├── routes/
│   │   ├── __init__.py
│   │   └── scripts.py
│   ├── static/
│   │   └── style.css
│   ├── templates/
│   │   ├── base.html
│   │   ├── dashboard.html
│   │   ├── adp_tracker.html
│   │   ├── blue_list_tracker.html
│   │   ├── diu_pathway_tracker.html
│   │   ├── dow_parser.html
│   │   ├── fcc_els_parser.html
│   │   └── navy_sbir_sttr_parser.html
│   ├── config.py
│   ├── amon_hen_ui.py
│   ├── requirements.in
│   └── requirements.txt
├── .gitignore
├── LICENSE
├── pyproject.toml
├── README.md
├── requirements.in
├── requirements.txt
├── requirements-dev.in
└── requirements-dev.txt
```

## Installation
### 1. Clone repository
```shell
git clone https://github.com/carsonkoball/amon-hen.git
cd amon-hen
```

### 2. Create virtual environment (recommended)
**Linux / macOS:**
```bash
python3 -m venv venv
source venv/bin/activate
```
**Windows (Command Prompt):**
```cmd
python -m venv venv
venv\Scripts\activate.bat
```
**Windows (PowerShell):**
```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

### 3. Install core dependencies and package
**User:**
```shell
pip install -r requirements.txt
pip install -e .
```
**Developer:**
```shell
pip install -r requirements-dev.txt
pip install -e .
```

### 4. Install UI dependencies (optional)
```shell
cd ui
pip install -r requirements.txt
```

## Future Work
### Fixes/Modifications
- [x] Update UI with existing tools
- [x] Add fcc_els_parser to UI
- [x] Add diu_pathway_tracker to UI
- [x] Update blue_list_tracker to use new list source
- [x] Modify fcc_els_parser to utilize a search date range
- [ ] Add fedramp_tracker to UI
- [ ] Update file_tracker to utilize Tracker system
	
### New Additions
- [x] Add Navy SBIR/STTR parser capability
- [x] Add Case Studies section
- [x] Add FedRAMP tracker capability
- [x] Add a tool example document
- [ ] Add DIU solutions tracker capability
- [ ] Add tool examples to README
- [ ] Add LinkedIn tracker capability