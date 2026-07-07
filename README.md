# amon-hen
A collection of tools for monitoring data sources to support investment research.

Named after *Amon Hen*, a location in J.R.R. Tolkien's *The Lord of the Rings*.  The name is Sindarin and is usually translated as "Hill of Sight", but more literally "Hill of the Eye", *from amon* ("hill") and *hen* ("eye"). See [Amon Hen on Tolkien Gateway.](https://tolkiengateway.net/wiki/Amon_Hen)

## Table of Contents
-   [Tools Overview](#tools-overview)
-   [Structure](#structure)
-   [Installation](#installation)

## Tools Overview
### adp_scraper
Monitors the ADP Career Center for a user-specified company.
- Tracks new job postings
- Tracks removed job postings
- Archives job postings locally

### blue_list_tracker
Monitors the DCMA Blue UAS Cleared Drone List.
- Tracks new listings
- Tracks removed listings
- Tracks listing modifications
- Archives listings locally

### dow_scraper
Monitors the Department of War (DoW) daily contract announcements page.
- Parses awarded company names

### file_tracker
Searches websites for files with user-specified extensions (e.g. .pdf, .csv, .png).
- Tracks file content modifications
- Archives discovered files locally

### Common Utilities
#### crawler
Automated web crawler
#### filesystem
Filesystem operations
#### http
HTTP request helpers
#### log_config
Logging configuration

## Structure
```
amon-hen/
├── src/
│   └── amon_hen/
│       ├── common/
│       │   ├── config_crawler.py
│       │   ├── crawler.py
│       │   ├── filesystem.py
│       │   ├── http.py
│       │   └── log_config.py
│       └── scripts/
│           ├── adp_scraper/
│           │   ├── config.py
│           │   ├── __init__.py
│           │   ├── __main__.py
│           │   └── adp_scraper.py
│           ├── blue_list_tracker/
│           │   ├── config.py
│           │   ├── __init__.py
│           │   ├── __main__.py
│           │   └── blue_list_tracker.py
│           ├── dow_scraper/
│           │   ├── config.py
│           │   ├── __init__.py
│           │   ├── __main__.py
│           │   └── dow_scraper.py
│           └── file_tracker/
│               ├── config.py
│               ├── __init__.py
│               ├── __main__.py
│               └── file_tracker.py
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
### 3. Install dependencies and package
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