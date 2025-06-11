# Async PostgreSQL Worker with FastAPI

A production-ready asynchronous job queue system built with FastAPI, PostgreSQL, and asyncio. This project demonstrates modern async Python patterns for building scalable background job processing systems.

## 🚀 Features

- **Async-First Design**: Built with asyncio and async/await patterns throughout
- **Job Queue System**: PostgreSQL-backed job queue with atomic job claiming
- **REST API**: FastAPI endpoints for job submission and status tracking
- **Background Worker**: Continuous job processing with graceful shutdown
- **Connection Pooling**: Efficient database connection management
- **Duplicate Detection**: Smart handling of duplicate job submissions
- **Concurrent Processing**: Multiple jobs processed simultaneously

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   FastAPI App   │    │   PostgreSQL     │    │ Background      │
│                 │    │                  │    │ Worker          │
│ • Job Creation  │◄──►│ • Job Queue      │◄──►│                 │
│ • Status Check  │    │ • Connection     │    │ • Job Processing│
│ • Health Check  │    │   Pool           │    │ • Error Handling│
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL 12+
- Docker (optional, for easy PostgreSQL setup)

## 🔧 Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd async-worker-project
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up PostgreSQL**:
   
   **Option A: Using Docker**:
   ```bash
   docker-compose up -d
   ```
   
   **Option B: Local PostgreSQL**:
   ```bash
   createdb async_worker_db
   ```

4. **Run database migrations**:
   ```bash
   psql -d async_worker_db -f migrations/init.sql
   ```

5. **Configure environment**:
   ```bash
   export DATABASE_URL="postgresql://user:password@localhost/async_worker_db"
   ```

## 🚀 Quick Start

1. **Start the application**:
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Create a job**:
   ```bash
   curl -X POST "http://localhost:8000/jobs" \
        -H "Content-Type: application/json" \
        -d '{"payload": {"task": "hello_world", "data": "test message"}}'
   ```

3. **Check job status**:
   ```bash
   curl "http://localhost:8000/jobs/{job_id}"
   ```

4. **Health check**:
   ```bash
   curl "http://localhost:8000/health"
   ```

## 📁 Project Structure

```
async_worker/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application and lifespan management
│   ├── models.py            # Pydantic models for request/response
│   ├── database.py          # Database connection and operations
│   ├── worker.py            # Background job processor
├── migrations/
│   └── init.sql             # Database schema
├── tests/
│   ├── __init__.py
│   ├── test_api.py          # API endpoint tests
│   ├── test_worker.py       # Worker logic tests
├── requirements.txt
├── docker-compose.yml       # PostgreSQL for development
└── README.md
```

## 🔄 Job Lifecycle

```
┌─────────┐    ┌─────────────┐    ┌───────────┐    ┌────────────┐
│ queued  │───►│ processing  │───►│ completed │    │   failed   │
└─────────┘    └─────────────┘    └───────────┘    └────────────┘
                       │                                  ▲
                       └──────────────────────────────────┘
                              (on error)
```

## 🎯 API Endpoints

### Create Job
- **POST** `/jobs`
- **Body**: `{"payload": {"key": "value"}}`
- **Response**: `{"job_id": "uuid", "status": "queued"}`

### Get Job Status
- **GET** `/jobs/{job_id}`
- **Response**: 
  ```json
  {
    "job_id": "uuid",
    "status": "completed",
    "attempt_count": 1,
    "payload": {"key": "value"}
  }
  ```

### Health Check
- **GET** `/health`
- **Response**: `{"status": "healthy"}`

## 🧪 Testing

Run the test suite:

```bash
# Install test dependencies
uv pip install -r requirements.txt

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html
```

## 🏗️ Key Design Patterns

### 1. Async Database Operations
- Connection pooling for concurrent request handling
- Atomic job claiming with `FOR UPDATE SKIP LOCKED`
- Proper resource cleanup with async context managers

### 2. Job Queue Management
- PostgreSQL-based persistence for reliability
- Duplicate job detection and replacement
- Worker polling with graceful shutdown

### 3. Error Handling
- Structured error responses
- Basic retry logic (extensible for advanced patterns)
- Connection failure recovery

## 📈 Performance Characteristics

- **Concurrent Jobs**: Handles multiple jobs simultaneously
- **Database Connections**: Efficient pooling (2-5 connections by default)
- **Response Time**: Sub-100ms for job submission
- **Throughput**: Depends on job complexity and database performance

## 🛣️ Roadmap

### Phase 3: Robust Error Handling
- [ ] Exponential backoff with jitter
- [ ] Circuit breaker pattern
- [ ] Dead letter queue for failed jobs
- [ ] Comprehensive timeout hierarchy

### Phase 4: Real Task Execution
- [ ] Task registry system
- [ ] Email sending tasks
- [ ] File processing tasks
- [ ] Rate limiting and resource management

### Phase 5: Production Features
- [ ] Structured logging and monitoring
- [ ] Health check improvements
- [ ] Horizontal scaling support
- [ ] Admin dashboard

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 Development Notes

### Core Async Principles Applied

1. **Control Flow Management**: Just-in-time connection acquisition, proper use of `await` vs `asyncio.gather()`
2. **Critical Section Protection**: Atomic job claiming prevents race conditions
3. **Task Lifecycle Management**: Proper cleanup with async context managers
4. **Resource Management**: Connection pooling with health monitoring
5. **Graceful Degradation**: Error handling with structured responses

### Database Design Decisions

- **Connection as Parameter Pattern**: Enables flexible transaction boundaries
- **Atomic Operations**: Single SQL queries for consistency
- **Pool-Level Health Checks**: More efficient than per-connection validation
- **Structured Return Values**: Clear distinction between business logic and system errors

## 📚 Learning Resources

This project demonstrates several advanced async Python concepts:

- [AsyncIO Documentation](https://docs.python.org/3/library/asyncio.html)
- [FastAPI Async Guide](https://fastapi.tiangolo.com/async/)
- [asyncpg Documentation](https://magicstack.github.io/asyncpg/current/)
- [PostgreSQL Connection Pooling](https://www.postgresql.org/docs/current/runtime-config-connection.html)

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

**Database Connection Errors**:
```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Verify database exists
psql -l | grep async_worker_db
```

**Import Errors**:
```bash
# Ensure you're in the project root and PYTHONPATH is set
export PYTHONPATH=$(pwd)
```

**Worker Not Processing Jobs**:
- Check database connectivity
- Verify worker is running (check logs)
- Ensure jobs are in 'queued' status

### Debug Mode

Run with debug logging:
```bash
uvicorn app.main:app --reload --log-level debug
```

## 📊 Monitoring

Basic monitoring endpoints:

- `/health` - Application health status  
- `/metrics` - Basic application metrics (planned)
- Database queries for job queue depth and processing rates

For production deployments, consider integrating with:
- Prometheus for metrics collection
- Grafana for dashboards  
- Sentry for error tracking
- Structured logging with ELK stack