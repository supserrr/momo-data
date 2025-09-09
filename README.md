# MoMo Data Processing System

## Team Information
- **Team Name**: Team 11
- **Project**: Enterprise-level fullstack application for MoMo SMS data processing
- **Course**: Enterprise Web Development

### Team Members
- **Shima Serein** - Developer
- **David Shumbusho** - Developer

## Project Overview
This project processes MoMo SMS data in XML format, cleans and categorizes it, stores it in a relational database, and provides a frontend for analysis and visualization. The system demonstrates skills in backend data processing, database management, and frontend development. All monetary values are displayed in Rwandan Francs (RWF).

## System Architecture
![MoMo Data Processing System Architecture](./web/assets/architecture-diagram.png)

## Scrum Board
https://github.com/users/supserrr/projects/3/views/1?system_template=team_planning

## Setup Instructions
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and configure your database settings
4. Run the ETL process: `./scripts/run_etl.sh`
5. Start the frontend server: `./scripts/serve_frontend.sh`

## Project Structure
```
├── README.md                 # Project overview and setup instructions
├── .env.example             # Environment variables template
├── requirements.txt         # Python dependencies
├── index.html              # Dashboard entry point
├── web/                    # Frontend assets
│   ├── styles.css         # Dashboard styling
│   ├── chart_handler.js   # Chart rendering and data fetching
│   └── assets/            # Images and icons
├── data/                   # Data storage
│   ├── raw/               # Raw XML input files
│   ├── processed/         # Cleaned and processed data
│   └── db.sqlite3         # SQLite database
├── logs/                   # Logging
│   ├── etl.log           # ETL process logs
│   └── dead_letter/      # Failed processing logs
├── etl/                    # ETL pipeline
│   ├── __init__.py
│   ├── config.py         # Configuration settings
│   ├── parse_xml.py      # XML parsing logic
│   ├── clean_normalize.py # Data cleaning and normalization
│   ├── categorize.py     # Transaction categorization
│   ├── load_db.py        # Database operations
│   └── run.py            # Main ETL runner
├── api/                    # Optional API layer
│   ├── __init__.py
│   ├── app.py            # FastAPI application
│   ├── db.py             # Database helpers
│   └── schemas.py        # Pydantic models
├── scripts/               # Utility scripts
│   ├── run_etl.sh        # ETL execution script
│   ├── export_json.sh    # JSON export script
│   └── serve_frontend.sh # Frontend server script
└── tests/                 # Test suite
    ├── test_parse_xml.py
    ├── test_clean_normalize.py
    └── test_categorize.py
```

## Development Workflow
This project follows Agile practices with:
- GitHub repository for version control
- Scrum board for task management
- Continuous integration and testing
- Modular architecture for maintainability
