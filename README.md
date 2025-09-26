# MoMo SMS Data Processing System

A full-stack application that processes mobile money (MoMo) SMS data, categorizes transactions, and provides analytics through a web dashboard.

## Team

- **Team Name**: Team 11
- **Project**: MoMo SMS data processing system
- **Course**: Enterprise Web Development

### Team Members
- **Shima Serein** - Lead Developer
- **David Shumbusho** - Developer

## System Architecture

![MoMo Data Processing System Architecture](./web/assets/architecture-diagram.png)

## Project Management

**Scrum Board**: [View Project Board](https://github.com/users/supserrr/projects/3/views/1?system_template=team_planning)

## Overview

This system processes XML-formatted SMS data from mobile money services, cleans and normalizes the data, categorizes transactions, and stores everything in a normalized MySQL database. The web dashboard provides analytics and transaction insights.

## Database Foundation

### Entity Relationship Diagram (ERD)
- **ERD Documentation**: [docs/ERD_Documentation.md](./docs/ERD_Documentation.md)
- **ERD Diagram**: [docs/ERD.png](./docs/ERD.png)
- **Design**: Fully normalized schema with 8 core entities following 3NF principles
- **Key Entities**: Users, Transactions, Transaction_Categories, Tags, System_Logs, Transaction_Statistics
- **Relationships**: Many-to-many relationships resolved with junction tables

### Database Implementation
- **SQL Schema**: [database/database_setup.sql](./database/database_setup.sql)
- **Features**: Foreign key constraints, indexes, triggers, stored procedures
- **Performance**: Optimized for complex queries and analytics
- **Testing**: CRUD operations included in setup script

### JSON Data Modeling
- **JSON Schemas**: [examples/json_schemas.json](./examples/json_schemas.json)
- **Complete Example**: [examples/complete_transaction_example.json](./examples/complete_transaction_example.json)
- **Mapping Documentation**: [examples/json_schema_mapping.md](./examples/json_schema_mapping.md)
- **API Integration**: Proper serialization for REST endpoints

## Quick Start

### Prerequisites

- Python 3.8 or later
- MySQL 8.0 or later
- MySQL server running and accessible

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

3. **Setup MySQL database**
   ```bash
   # Create database and run setup script
   mysql -u root -p < database/database_setup.sql
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your MySQL database settings
   ```

5. **Run the ETL process**
   ```bash
   ./scripts/run_etl.sh
   ```

6. **Start the API server**
   ```bash
   ./scripts/start_server.sh
   ```

7. **Open the dashboard**
   Navigate to `http://localhost:8000` in your browser.

## Project Structure

```
├── README.md                    # Project documentation
├── env.example                  # Environment configuration template
├── requirements.txt             # Python dependencies
├── index.html                   # Web dashboard entry point
├── web/                         # Frontend assets
│   ├── styles.css              # Dashboard styling
│   ├── chart_handler.js        # Chart rendering and data fetching
│   └── assets/                 # Images and icons
│       └── architecture-diagram.png
├── data/                        # Data storage
│   ├── raw/                    # Raw XML input files
│   │   └── modified_sms_v2.xml # Sample MoMo SMS data
│   ├── processed/              # Cleaned and processed data
│   │   └── dashboard.json     # Dashboard data aggregates
│   └── logs/                  # System logs
│       ├── etl.log            # ETL process logs
│       └── dead_letter/       # Failed processing logs
├── database/                    # Database schema and setup
│   ├── database_setup.sql     # Normalized MySQL schema with sample data
│   ├── create_file_tracking.sql
│   ├── create_missing_tables.sql
│   └── migrate_to_enhanced.sql
├── docs/                        # Documentation
│   ├── ERD_Documentation.md   # ERD design documentation
│   ├── ERD.png                # Entity Relationship Diagram
│   ├── api_docs.md            # API documentation
│   └── API_Security_Report.pdf # Security analysis report
├── examples/                    # JSON schema examples
│   ├── complete_transaction_example.json # Transaction with relations
│   ├── json_schema_mapping.md # SQL to JSON mapping documentation
│   └── json_schemas.json      # All JSON schemas
├── etl/                         # ETL pipeline
│   ├── config.py              # Configuration settings
│   ├── parser.py              # Transaction parser
│   ├── loader.py              # Database operations
│   ├── file_tracker.py        # File processing tracking
│   └── run.py                 # Main ETL runner
├── dsa/                         # Data Structures & Algorithms
│   ├── data_structures.py     # Data structure implementations
│   ├── search_comparison.py   # Search algorithm comparisons
│   └── sorting_comparison.py  # Sorting algorithm comparisons
├── api/                         # API server
│   ├── momo_api_server.py     # Main API server
│   ├── config.py              # API configuration
│   ├── db.py                  # Database helpers
│   └── schemas.py             # Pydantic models
├── scripts/                     # Utility scripts
│   ├── start_server.sh        # Start API server
│   ├── run_etl.sh             # ETL execution script
│   ├── export_json.sh         # JSON export script
│   ├── generate_pdf_report.py # PDF report generator
│   ├── run_unified_rest_api.sh # Unified API server script
│   └── test_api.sh            # API testing script
└── tests/                       # Test suite
    ├── test_auth.py           # Authentication tests
    └── test_dsa.py            # DSA algorithm tests
```

## Features

### Data Processing
- **XML Parsing**: Extracts transaction data from MoMo SMS XML files
- **Data Cleaning**: Normalizes phone numbers, amounts, and dates
- **Transaction Categorization**: Categorizes transactions by type
- **Database Storage**: Stores processed data in normalized MySQL database with proper relationships

### Web Dashboard
- **Transaction Analytics**: Charts and tables showing transaction patterns
- **User Statistics**: User activity and spending insights
- **Category Breakdown**: Transaction distribution by category
- **Real-time Updates**: Dashboard refreshes with new data

### API
- **RESTful Endpoints**: Complete CRUD operations for transactions
- **Authentication**: Basic Auth with admin:password
- **JSON Responses**: Structured data in JSON format
- **Pagination**: Data retrieval for large datasets
- **DSA Integration**: Algorithm performance comparisons
- **Export Functionality**: JSON and CSV data export

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# MySQL Database configuration
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_DATABASE=momo_sms_processing
MYSQL_USER=momo_app
MYSQL_PASSWORD=secure_password_123

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

Start the API server:
```bash
# Using the startup script (recommended)
./scripts/start_server.sh

# Or directly with Python
python3 api/momo_api_server.py --port 8000
```

### Exporting Data

Export processed data to JSON:
```bash
./scripts/export_json.sh
```

### API Endpoints

The API provides REST endpoints:

#### Authentication
- **Method**: Basic Authentication
- **Credentials**: `admin:password`

#### Transaction Endpoints
- `GET /api/transactions` - List all transactions with pagination
- `GET /api/transactions/{id}` - Get specific transaction by ID
- `POST /api/transactions` - Create new transaction
- `PUT /api/transactions/{id}` - Update existing transaction
- `DELETE /api/transactions/{id}` - Delete transaction

#### Analytics Endpoints
- `GET /api/dashboard-data` - Dashboard summary statistics
- `GET /api/analytics` - Detailed analytics data
- `GET /api/category-distribution` - Transaction category breakdown
- `GET /api/monthly-stats` - Monthly transaction statistics

#### DSA Endpoints
- `GET /api/dsa/linear-search?id={id}` - Linear search demonstration
- `GET /api/dsa/dictionary-lookup?id={id}` - Dictionary lookup demonstration
- `GET /api/dsa/comparison` - Algorithm performance comparison

#### Export Endpoints
- `GET /api/export/transactions` - Export transactions as JSON/CSV
- `GET /api/export/analytics` - Export analytics data
- `GET /api/export/dashboard` - Export dashboard data

### Data Structures & Algorithms

The system implements and compares various algorithms:

#### Search Algorithms
- **Linear Search**: O(n) time complexity for finding transactions
- **Dictionary Lookup**: O(1) time complexity using hash tables
- **Performance Comparison**: Detailed analysis with execution time metrics

#### Sorting Algorithms
- **Bubble Sort**: O(n²) time complexity
- **Selection Sort**: O(n²) time complexity
- **Insertion Sort**: O(n²) time complexity
- **Merge Sort**: O(n log n) time complexity
- **Quick Sort**: O(n log n) average case

#### Data Structures
- **Linked Lists**: Doubly linked list implementation
- **Stacks**: LIFO data structure using linked lists
- **Queues**: FIFO data structure using linked lists
- **Binary Search Trees**: Sorted tree structure for efficient searching

## Development

### Running Tests

```bash
python -m pytest tests/
```

### Code Style

We follow PEP 8 Python style guidelines.

### Database Schema

The system uses a fully normalized MySQL database schema with 8 core entities:

#### Core Entities
- **Users** - User information and phone numbers
- **Transactions** - Main transaction records with full metadata
- **Transaction_Categories** - Transaction type definitions
- **Tags** - Flexible tagging system for transactions
- **Transaction_Tags** - Many-to-many relationship junction table
- **User_Preferences** - User-specific settings and preferences
- **System_Logs** - ETL process tracking and monitoring
- **Transaction_Statistics** - Pre-calculated analytics for performance

#### Key Features
- **Normalized Design** - 3NF compliant schema with proper relationships
- **Performance Optimization** - Indexes on frequently queried columns
- **Audit Trail** - Complete transaction history with processing timestamps
- **Flexible Metadata** - JSON storage for variable transaction attributes
- **Statistics Pre-calculation** - Dashboard performance through aggregated data
- **Referential Integrity** - Foreign key constraints ensure data consistency

#### Database Design
- **ERD Documentation**: See `docs/ERD_Documentation.md` for design rationale
- **Schema Implementation**: Database structure for ETL processing
- **Data Processing**: Integration with XML parsing and categorization

#### Data Processing
The database supports transaction processing including:
- XML data parsing and normalization
- Transaction categorization with confidence scoring
- ETL process monitoring and logging
- Category-level statistics aggregation for analytics

## Troubleshooting

### Common Issues

**ETL process fails**
- Check XML file format and location
- Verify database permissions
- Review logs in `data/logs/etl.log`

**Dashboard not loading**
- Ensure ETL process completed
- Check that `data/processed/dashboard.json` exists
- Verify web server is running on correct port

**Database errors**
- Check MySQL server is running and accessible
- Verify database credentials in environment variables
- Ensure database schema is up to date
- Review MySQL logs for constraint violations

### Logs

- **ETL Logs**: `data/logs/etl.log`
- **Failed Records**: `data/logs/dead_letter/`
- **Web Server Logs**: Check terminal output


## Project Development

This project was developed by our team as part of the Enterprise Web Development course. The system demonstrates our skills in:

### Development Phases

**Phase 1 - Project Setup and Planning**
- Project structure and organization
- ETL pipeline design and implementation
- Database schema planning
- Frontend dashboard development

**Phase 2 - Database Design and Implementation**
- Entity Relationship Diagram (ERD) design
- Normalized MySQL database schema (3NF)
- JSON data modeling and serialization
- Database optimization with indexes and constraints

**Phase 3 - API Development and Security**
- Complete CRUD API implementation
- Basic Authentication with security analysis
- Data Structures & Algorithms integration
- Performance comparison and analysis
- Comprehensive API documentation

### Technical Skills Demonstrated
- **Backend Development**: Python ETL pipelines, MySQL database management
- **API Development**: RESTful endpoints with authentication and validation
- **Frontend Development**: Interactive dashboard with Chart.js and responsive design
- **Database Design**: Normalized schema with proper relationships and constraints
- **Algorithm Implementation**: Search and sorting algorithms with performance analysis
- **Security**: Authentication implementation and security best practices analysis
- **Testing**: Comprehensive test suite for all components
- **Documentation**: Professional documentation and API specifications