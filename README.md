# MoMo SMS Data Processing System

A full-stack application that processes mobile money (MoMo) SMS data, categorizes transactions, and provides analytics through a web dashboard.

## Team

- **Team Name**: Team 11
- **Project**: Enterprise-level fullstack application for MoMo SMS data processing
- **Course**: Enterprise Web Development

### Team Members
- **Shima Serein** - Developer
- **David Shumbusho** - Developer

## System Architecture

![MoMo Data Processing System Architecture](./web/assets/architecture-diagram.png)

## Project Management

**Scrum Board**: [View Project Board](https://github.com/users/supserrr/projects/3/views/1?system_template=team_planning)

## Overview

This system processes XML-formatted SMS data from mobile money services, cleans and normalizes the data, categorizes transactions, and stores everything in a SQLite database. The web dashboard provides visual analytics and transaction insights.

## Quick Start

### Prerequisites

- Python 3.8 or later
- SQLite3

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd momo-data
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your database settings
   ```

4. **Run the ETL process**
   ```bash
   ./scripts/run_etl.sh
   ```

5. **Start the web server**
   ```bash
   ./scripts/serve_frontend.sh
   ```

6. **Open the dashboard**
   Navigate to `http://localhost:8000` in your browser.

## Project Structure

```
├── README.md                    # This file
├── .env.example                 # Environment configuration template
├── requirements.txt             # Python dependencies
├── index.html                   # Web dashboard entry point
├── web/                         # Frontend assets
│   ├── styles.css              # Dashboard styling
│   ├── chart_handler.js        # Chart rendering and data fetching
│   └── assets/                 # Images and icons
├── data/                        # Data storage
│   ├── raw/                    # Raw XML input files
│   │   └── momo.xml           # Sample MoMo SMS data
│   ├── processed/              # Cleaned and processed data
│   │   └── dashboard.json     # Dashboard data aggregates
│   ├── db.sqlite3             # SQLite database
│   └── logs/                  # System logs
│       ├── etl.log            # ETL process logs
│       └── dead_letter/       # Failed processing logs
├── etl/                         # ETL pipeline
│   ├── config.py              # Configuration settings
│   ├── parse_xml.py           # XML parsing logic
│   ├── clean_normalize.py     # Data cleaning and normalization
│   ├── categorize.py          # Transaction categorization
│   ├── load_db.py             # Database operations
│   └── run.py                 # Main ETL runner
├── api/                         # Optional API layer
│   ├── app.py                 # FastAPI application
│   ├── db.py                  # Database helpers
│   └── schemas.py             # Pydantic models
├── scripts/                     # Utility scripts
│   ├── run_etl.sh             # ETL execution script
│   ├── export_json.sh         # JSON export script
│   └── serve_frontend.sh      # Frontend server script
└── tests/                       # Test suite
    ├── test_parse_xml.py
    ├── test_clean_normalize.py
    └── test_categorize.py
```

## Features

### Data Processing
- **XML Parsing**: Extracts transaction data from MoMo SMS XML files
- **Data Cleaning**: Normalizes phone numbers, amounts, and dates
- **Transaction Categorization**: Automatically categorizes transactions by type
- **Database Storage**: Stores processed data in SQLite with proper relationships

### Web Dashboard
- **Transaction Analytics**: Visual charts and tables showing transaction patterns
- **User Statistics**: User activity and spending insights
- **Category Breakdown**: Transaction distribution by category
- **Real-time Updates**: Dashboard refreshes with new data

### API (Optional)
- **RESTful Endpoints**: Standard API for data access
- **JSON Responses**: Structured data in JSON format
- **Pagination**: Efficient data retrieval for large datasets

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Database configuration
DATABASE_URL=sqlite:///data/db.sqlite3

# ETL settings
XML_FILE_PATH=data/raw/momo.xml
LOG_LEVEL=INFO
```

### ETL Configuration

Edit `etl/config.py` to customize:
- File paths
- Transaction categorization rules
- Data cleaning thresholds
- Database settings

## Usage

### Running the ETL Process

Process new XML data:
```bash
python etl/run.py --xml data/raw/momo.xml
```

### Starting the API Server

Run the FastAPI server:
```bash
python api/app.py
```

### Exporting Data

Export processed data to JSON:
```bash
./scripts/export_json.sh
```

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Code Style

We followed PEP 8 Python style guidelines throughout the project.

### Database Schema

The system uses a normalized database schema with the following main tables:
- `users` - User information and phone numbers
- `transactions` - Transaction records with amounts and timestamps
- `categories` - Transaction categories and hierarchies
- `merchants` - Business entities for payments

## Troubleshooting

### Common Issues

**ETL process fails**
- Check XML file format and location
- Verify database permissions
- Review logs in `data/logs/etl.log`

**Dashboard not loading**
- Ensure ETL process completed successfully
- Check that `data/processed/dashboard.json` exists
- Verify web server is running on correct port

**Database errors**
- Check SQLite file permissions
- Verify database schema is up to date
- Review database logs for constraint violations

### Logs

- **ETL Logs**: `data/logs/etl.log`
- **Failed Records**: `data/logs/dead_letter/`
- **Web Server Logs**: Check terminal output

## Assignment Details

This project was developed as part of the Enterprise Web Development course. The system demonstrates skills in:

- Backend data processing and ETL pipelines
- Database design and management
- Frontend development and data visualization
- API design and implementation
- Full-stack application architecture