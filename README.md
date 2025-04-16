# lambda Serverless Function Execution Platform

A platform similar to AWS Lambda that enables users to deploy and execute functions on-demand via HTTP requests.

## Features

- Support for multiple programming languages (Python and JavaScript)
- Function execution via HTTP requests
- Multiple virtualization technologies (Docker + gVisor)
- Resource usage restrictions and timeout enforcement
- Web-based monitoring dashboard
- Real-time execution metrics

## Project Structure

```
serverless-platform/
├── backend/              # FastAPI backend server
│   ├── api/             # API routes
│   ├── models/          # Database models
│   └── services/        # Business logic
├── frontend/            # Streamlit frontend
├── executor/            # Function execution engine
│   ├── docker/         # Docker virtualization
│   └── gvisor/         # gVisor virtualization
└── tests/              # Test suite
```

## Setup Instructions

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Start the backend server:
```bash
python backend/main.py
```

3. Start the frontend:
```bash
streamlit run frontend/app.py
```

## Development

- Python 3.9+
- FastAPI for backend
- Streamlit for frontend
- Docker and gVisor for virtualization
- PostgreSQL for data storage

## API Documentation

API documentation is available at `/docs` when running the backend server.