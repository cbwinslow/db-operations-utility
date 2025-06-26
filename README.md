# Database Operations Utility

[![CI](https://github.com/cbwinslow/db-operations-utility/workflows/CI/CD%20Pipeline/badge.svg)](https://github.com/cbwinslow/db-operations-utility/actions/workflows/ci.yml)
[![codecov](https://codecov.io/gh/cbwinslow/db-operations-utility/branch/main/graph/badge.svg)](https://codecov.io/gh/cbwinslow/db-operations-utility)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

A comprehensive Python utility for handling PostgreSQL database operations using SQLAlchemy. This utility provides a clean, robust interface for common database tasks including connection management, CRUD operations, custom queries, and error handling.

## Features

- **Connection Management**: Robust database connection handling with connection pooling
- **CRUD Operations**: Create, Read, Update, Delete operations with automatic error handling
- **Query Interface**: Execute custom SQL queries and commands safely
- **Error Handling**: Comprehensive error handling with custom exceptions
- **Utilities**: Database introspection, table management, and backup functionality
- **Configuration Management**: Environment-based configuration with defaults
- **Logging**: Built-in logging for debugging and monitoring

## Installation

1. **Set up virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install psycopg2-binary sqlalchemy
```

## Files Structure

```
.
├── db_operations.py    # Main database operations utility
├── db_config.py       # Configuration management
├── db_example.py      # Example usage and demonstrations
└── README.md          # This documentation
```

## Quick Start

### Basic Usage

```python
from db_operations import DatabaseManager

# Initialize with default connection
db = DatabaseManager()

# Test connection
if db.test_connection():
    print("Connected successfully!")

# List all tables
tables = db.list_tables()
print(f"Tables: {tables}")

# Clean up
db.close()
```

### CRUD Operations

```python
# Create a record
user_id = db.create_record('users', {
    'name': 'John Doe',
    'email': 'john@example.com',
    'age': 30
})

# Read a record
user = db.read_record('users', user_id)
print(f"User: {user}")

# Update a record
db.update_record('users', user_id, {'age': 31})

# Delete a record
db.delete_record('users', user_id)
```

### Custom Queries

```python
# Execute a SELECT query
results = db.execute_query(
    "SELECT * FROM users WHERE age > :min_age",
    {'min_age': 25}
)

# Execute a command (INSERT, UPDATE, DELETE, etc.)
affected_rows = db.execute_command(
    "UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE active = true"
)
```

## Configuration

### Environment Variables

Configure your database connection using environment variables:

```bash
export DB_HOST=localhost
export DB_PORT=5432
export DB_NAME=your_database
export DB_USER=your_username
export DB_PASSWORD=your_password
export DB_POOL_SIZE=10
export DB_MAX_OVERFLOW=20
export DB_ECHO=false
```

### Programmatic Configuration

```python
from db_config import DatabaseConfig

config = DatabaseConfig()
db = DatabaseManager(config.get_connection_string())
```

## API Reference

### DatabaseManager Class

#### Connection Management

- `__init__(connection_string=None)`: Initialize database manager
- `test_connection()`: Test database connectivity
- `close()`: Close database connections

#### CRUD Operations

- `create_record(table_name, data)`: Create a new record
- `read_record(table_name, record_id)`: Read a single record by ID
- `read_records(table_name, conditions=None, limit=None, offset=None)`: Read multiple records
- `update_record(table_name, record_id, data)`: Update a record by ID
- `delete_record(table_name, record_id)`: Delete a record by ID

#### Query Interface

- `execute_query(query, params=None)`: Execute a SELECT query
- `execute_command(command, params=None)`: Execute non-SELECT commands

#### Utilities

- `list_tables()`: Get list of all tables
- `get_table_info(table_name)`: Get table structure information
- `backup_table(table_name, backup_file)`: Backup a table to SQL file

### Error Handling

The utility uses a custom `DatabaseError` exception for database-related errors:

```python
from db_operations import DatabaseError

try:
    db.create_record('users', data)
except DatabaseError as e:
    print(f"Database operation failed: {e}")
```

## Examples

### Example 1: Basic Database Inspection

```python
from db_operations import DatabaseManager

db = DatabaseManager()

if db.test_connection():
    # List all tables
    tables = db.list_tables()
    
    # Get info about each table
    for table in tables:
        info = db.get_table_info(table)
        print(f"Table: {table}")
        print(f"  Columns: {len(info['columns'])}")
        print(f"  Indexes: {len(info['indexes'])}")

db.close()
```

### Example 2: Data Migration

```python
from db_operations import DatabaseManager

db = DatabaseManager()

# Read data from source table
old_data = db.read_records('old_users')

# Transform and insert into new table
for record in old_data:
    new_record = {
        'name': record['full_name'],
        'email': record['email_address'],
        'created_at': record['registration_date']
    }
    db.create_record('new_users', new_record)

db.close()
```

### Example 3: Batch Operations

```python
from db_operations import DatabaseManager

db = DatabaseManager()

# Batch update using custom command
updated_rows = db.execute_command("""
    UPDATE products 
    SET price = price * 1.1 
    WHERE category = :category
""", {'category': 'electronics'})

print(f"Updated {updated_rows} products")

db.close()
```

## Running the Demo

To see the utility in action, run the example script:

```bash
source venv/bin/activate
python db_example.py
```

This will demonstrate:
1. Basic database operations
2. Table creation and CRUD operations
3. Advanced queries and metadata retrieval

## Security Best Practices

1. **Never hardcode credentials** in your source code
2. **Use environment variables** for configuration
3. **Validate input parameters** before executing queries
4. **Use parameterized queries** to prevent SQL injection
5. **Limit database permissions** to only what's necessary
6. **Enable connection encryption** in production

## Troubleshooting

### Common Issues

1. **Connection Failed**: Check if PostgreSQL is running and credentials are correct
2. **Permission Denied**: Ensure the database user has necessary privileges
3. **Table Not Found**: Verify table names and database schema
4. **Import Errors**: Ensure virtual environment is activated and dependencies are installed

### Debug Mode

Enable SQL query logging by setting `echo=True` in the configuration:

```python
# In db_config.py
'echo': True  # This will log all SQL queries
```

## Performance Tips

1. **Use connection pooling** (enabled by default)
2. **Limit result sets** with LIMIT and OFFSET
3. **Use indexes** for frequently queried columns
4. **Batch operations** when possible
5. **Close connections** when done

## CI/CD Pipeline

This project uses GitHub Actions for automated testing, quality assurance, and deployment. The CI/CD pipeline runs on every push and pull request.

### Pipeline Stages

1. **Code Linting** - Ensures code quality and consistency
   - Black (code formatting)
   - isort (import sorting)
   - Flake8 (style guide enforcement)
   - MyPy (type checking)
   - Pylint (code analysis)

2. **Unit Testing** - Runs comprehensive test suite
   - Tests across Python 3.9, 3.10, 3.11, 3.12
   - PostgreSQL integration testing
   - Code coverage reporting
   - Coverage uploaded to Codecov

3. **Security Scanning** - Identifies potential security issues
   - Bandit (security linter)
   - Safety (dependency vulnerability check)
   - Semgrep (static analysis)

4. **Documentation Building** - Generates project documentation
   - Sphinx documentation generation
   - API documentation with autodoc
   - HTML output for GitHub Pages

5. **Deployment** - Automated releases (main branch only)
   - Package building and validation
   - Automated GitHub releases
   - Version tagging

### Local Development

Run the full CI pipeline locally before pushing:

```bash
# Using Make (recommended)
make ci

# Or using the script directly
./scripts/run_tests.sh

# Individual commands
make format    # Format code
make lint      # Run linting
make test      # Run tests
make security  # Security scans
make docs      # Build docs
```

### Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write code following project conventions
   - Add tests for new functionality
   - Update documentation as needed

3. **Test locally**
   ```bash
   make ci  # Run full CI pipeline
   ```

4. **Commit and push**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   git push origin feature/your-feature-name
   ```

5. **Create pull request**
   - CI pipeline will run automatically
   - All checks must pass before merging
   - Code review required

### Status Badges

The badges at the top of this README show the current status of:
- [![CI](https://github.com/cbwinslow/db-operations-utility/workflows/CI/CD%20Pipeline/badge.svg)](https://github.com/cbwinslow/db-operations-utility/actions/workflows/ci.yml) - Build and test status
- [![codecov](https://codecov.io/gh/cbwinslow/db-operations-utility/branch/main/graph/badge.svg)](https://codecov.io/gh/cbwinslow/db-operations-utility) - Code coverage percentage
- Additional badges for Python version support, license, and code quality tools

## Contributing

1. Follow PEP 8 style guidelines
2. Add type hints for new functions
3. Include comprehensive error handling
4. Write unit tests for new features
5. Update documentation
6. Ensure all CI checks pass

## License

This utility is provided as-is for educational and development purposes.

## Three Ways This Script Can Be Improved

1. **Object-Relational Mapping (ORM) Integration**: 
   - Add support for SQLAlchemy ORM models alongside raw SQL
   - Implement automatic model generation from existing tables
   - Add relationship handling and lazy loading capabilities

2. **Advanced Connection Management**:
   - Implement connection retry logic with exponential backoff
   - Add support for read/write database splitting
   - Include connection health monitoring and automatic failover

3. **Query Builder and Migration Support**:
   - Add a fluent query builder interface for complex queries
   - Implement database migration management (version control for schema changes)
   - Include data validation and serialization features for API integration

