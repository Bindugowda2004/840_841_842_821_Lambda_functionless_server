# Serverless Function Execution Platform

A platform similar to AWS Lambda that enables users to deploy and execute functions on-demand via HTTP requests.

## Features

- Support for multiple programming languages (Python and JavaScript)
- Function execution via HTTP requests
- Docker-based virtualization with proper isolation
- Resource usage restrictions and timeout enforcement
- Web-based monitoring dashboard
- Real-time execution metrics
- User authentication and management
- Function metrics and monitoring

## Project Structure

```
serverless-platform/
├── backend/                # FastAPI backend server
│   ├── api/               # API routes and endpoints
│   │   ├── auth.py       # Authentication endpoints
│   │   ├── execute.py    # Function execution
│   │   ├── functions.py  # Function management
│   │   └── metrics.py    # Metrics and monitoring
│   ├── executor/         # Function execution engine
│   │   └── docker/       # Docker-based isolation
│   ├── models/           # Database models
│   └── main.py          # Main application entry
├── frontend/             # Streamlit frontend
│   └── app.py           # Dashboard interface
└── requirements.txt      # Project dependencies
```

## Prerequisites

- Python 3.9 or higher
- Docker Desktop
- Git

## Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd serverless-platform
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Initialize the database:
```bash
python backend/init_db.py
```

4. Start the backend server:
```bash
uvicorn backend.main:app --reload
```

5. Start the frontend:
```bash
streamlit run frontend/app.py
```

## Usage

1. Open http://localhost:8501 in your browser
2. Register a new account or login
3. Create a new function:
   - Choose Python or JavaScript runtime
   - Write your function code
   - Set execution timeout
   - Assign a route path
4. Execute your function through:
   - Web interface
   - Direct HTTP calls to the API

## Example Functions

### Python Function
```python
def handler():
    numbers = [1, 2, 3, 4, 5]
    return {
        "sum": sum(numbers),
        "average": sum(numbers) / len(numbers)
    }
```

### JavaScript Function
```javascript
function handler() {
    const numbers = [1, 2, 3, 4, 5];
    const sum = numbers.reduce((a, b) => a + b, 0);
    
    console.log(JSON.stringify({
        sum: sum,
        average: sum / numbers.length
    }));
}

handler();
```

## API Documentation

The API documentation is available at http://localhost:8000/docs when running the backend server.

### Key Endpoints

- `POST /functions/`: Create a new function
- `GET /functions/`: List all functions
- `POST /execute/{function_id}`: Execute a function
- `GET /metrics/{function_id}`: Get function metrics

## Security

- Functions are executed in isolated Docker containers
- User authentication required for all operations
- Resource limits and timeouts enforced
- Secure function isolation and cleanup

## Monitoring

- Real-time execution metrics
- Function success/failure tracking
- Execution time monitoring
- Resource usage tracking

## Development

- Backend: FastAPI for high-performance async API
- Frontend: Streamlit for interactive dashboard
- Database: SQLite for data storage
- Virtualization: Docker for secure function isolation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License.