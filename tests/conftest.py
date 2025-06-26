"""
Pytest configuration and shared fixtures for db-operations-utility tests.
"""

import pytest
import os
import tempfile
from unittest.mock import Mock
from src.db_operations.config import DatabaseConfig
from src.db_operations.core import DatabaseOperations


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_config():
    """Provide a sample database configuration for testing."""
    return DatabaseConfig(
        host="localhost",
        port=5432,
        database="test_db",
        username="test_user",
        password="test_pass",
        driver="postgresql"
    )


@pytest.fixture
def sample_config_no_password():
    """Provide a sample database configuration without password."""
    return DatabaseConfig(
        host="localhost",
        port=5432,
        database="test_db",
        username="test_user",
        password=None,
        driver="postgresql"
    )


@pytest.fixture
def db_operations(sample_config):
    """Provide a DatabaseOperations instance with sample config."""
    return DatabaseOperations(sample_config)


@pytest.fixture
def mock_connection():
    """Provide a mock database connection."""
    mock_conn = Mock()
    mock_conn.execute.return_value = Mock()
    mock_conn.fetchall.return_value = []
    mock_conn.fetchone.return_value = None
    mock_conn.rowcount = 0
    return mock_conn


@pytest.fixture
def sample_data():
    """Provide sample data for testing database operations."""
    return [
        {"id": 1, "name": "John Doe", "email": "john@example.com", "age": 30},
        {"id": 2, "name": "Jane Smith", "email": "jane@example.com", "age": 25},
        {"id": 3, "name": "Bob Johnson", "email": "bob@example.com", "age": 35}
    ]


@pytest.fixture
def sample_insert_data():
    """Provide sample data for insert operations."""
    return [
        {"name": "Alice Brown", "email": "alice@example.com", "age": 28},
        {"name": "Charlie Wilson", "email": "charlie@example.com", "age": 32}
    ]


@pytest.fixture(autouse=True)
def clear_env_vars():
    """Clear database-related environment variables before each test."""
    env_vars = [
        'DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD',
        'DB_DRIVER', 'DB_TIMEOUT', 'DB_POOL_SIZE', 'DB_MAX_OVERFLOW', 'DB_ECHO'
    ]
    
    original_values = {}
    for var in env_vars:
        original_values[var] = os.environ.get(var)
        if var in os.environ:
            del os.environ[var]
    
    yield
    
    # Restore original values
    for var, value in original_values.items():
        if value is not None:
            os.environ[var] = value


@pytest.fixture
def config_file_content():
    """Provide sample configuration file content."""
    return {
        "host": "config.example.com",
        "port": 3306,
        "database": "config_db",
        "username": "config_user",
        "password": "config_pass",
        "driver": "mysql",
        "connection_timeout": 60,
        "pool_size": 15,
        "max_overflow": 25,
        "echo": True
    }


@pytest.fixture
def temp_config_file(temp_dir, config_file_content):
    """Create a temporary configuration file."""
    import json
    config_path = os.path.join(temp_dir, "config.json")
    with open(config_path, 'w') as f:
        json.dump(config_file_content, f)
    return config_path


class MockCursor:
    """Mock database cursor for testing."""
    
    def __init__(self, results=None):
        self.results = results or []
        self.rowcount = len(self.results) if self.results else 0
        self._index = 0
    
    def execute(self, query, params=None):
        """Mock execute method."""
        pass
    
    def fetchall(self):
        """Mock fetchall method."""
        return self.results
    
    def fetchone(self):
        """Mock fetchone method."""
        if self._index < len(self.results):
            result = self.results[self._index]
            self._index += 1
            return result
        return None
    
    def close(self):
        """Mock close method."""
        pass


@pytest.fixture
def mock_cursor():
    """Provide a mock database cursor."""
    return MockCursor()


# Test markers
pytest.mark.unit = pytest.mark.unit
pytest.mark.integration = pytest.mark.integration
pytest.mark.slow = pytest.mark.slow

