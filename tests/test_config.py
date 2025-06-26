"""
Tests for the database configuration module.
"""

import os
import pytest
from unittest.mock import patch
from src.db_operations.config import DatabaseConfig


class TestDatabaseConfig:
    """Test cases for DatabaseConfig class."""
    
    def test_default_initialization(self):
        """Test default configuration initialization."""
        config = DatabaseConfig()
        
        assert config.host == "localhost"
        assert config.port == 5432
        assert config.database == "postgres"
        assert config.username == "postgres"
        assert config.password is None
        assert config.driver == "postgresql"
        assert config.connection_timeout == 30
        assert config.pool_size == 5
        assert config.max_overflow == 10
        assert config.echo is False
    
    def test_custom_initialization(self):
        """Test configuration with custom values."""
        config = DatabaseConfig(
            host="db.example.com",
            port=3306,
            database="mydb",
            username="myuser",
            password="mypass",
            driver="mysql"
        )
        
        assert config.host == "db.example.com"
        assert config.port == 3306
        assert config.database == "mydb"
        assert config.username == "myuser"
        assert config.password == "mypass"
        assert config.driver == "mysql"
    
    @patch.dict(os.environ, {
        'DB_HOST': 'env.example.com',
        'DB_PORT': '3306',
        'DB_NAME': 'envdb',
        'DB_USER': 'envuser',
        'DB_PASSWORD': 'envpass',
        'DB_DRIVER': 'mysql',
        'DB_TIMEOUT': '60',
        'DB_POOL_SIZE': '10',
        'DB_MAX_OVERFLOW': '20',
        'DB_ECHO': 'true'
    })
    def test_from_env(self):
        """Test configuration from environment variables."""
        config = DatabaseConfig.from_env()
        
        assert config.host == "env.example.com"
        assert config.port == 3306
        assert config.database == "envdb"
        assert config.username == "envuser"
        assert config.password == "envpass"
        assert config.driver == "mysql"
        assert config.connection_timeout == 60
        assert config.pool_size == 10
        assert config.max_overflow == 20
        assert config.echo is True
    
    @patch.dict(os.environ, {}, clear=True)
    def test_from_env_defaults(self):
        """Test from_env with no environment variables (should use defaults)."""
        config = DatabaseConfig.from_env()
        
        assert config.host == "localhost"
        assert config.port == 5432
        assert config.database == "postgres"
        assert config.username == "postgres"
        assert config.password is None
        assert config.driver == "postgresql"
    
    def test_get_connection_string_with_password(self):
        """Test connection string generation with password."""
        config = DatabaseConfig(
            host="localhost",
            port=5432,
            database="testdb",
            username="testuser",
            password="testpass",
            driver="postgresql"
        )
        
        expected = "postgresql://testuser:testpass@localhost:5432/testdb"
        assert config.get_connection_string() == expected
    
    def test_get_connection_string_without_password(self):
        """Test connection string generation without password."""
        config = DatabaseConfig(
            host="localhost",
            port=5432,
            database="testdb",
            username="testuser",
            password=None,
            driver="postgresql"
        )
        
        expected = "postgresql://testuser@localhost:5432/testdb"
        assert config.get_connection_string() == expected
    
    def test_to_dict(self):
        """Test configuration to dictionary conversion."""
        config = DatabaseConfig(
            host="localhost",
            port=5432,
            database="testdb",
            username="testuser",
            password="testpass"
        )
        
        config_dict = config.to_dict()
        
        assert config_dict["host"] == "localhost"
        assert config_dict["port"] == 5432
        assert config_dict["database"] == "testdb"
        assert config_dict["username"] == "testuser"
        assert config_dict["password"] == "***"  # Password should be masked
        assert config_dict["driver"] == "postgresql"
    
    def test_to_dict_no_password(self):
        """Test to_dict with no password."""
        config = DatabaseConfig(password=None)
        config_dict = config.to_dict()
        
        assert config_dict["password"] is None
    
    def test_validate_success(self):
        """Test successful validation."""
        config = DatabaseConfig(
            host="localhost",
            database="testdb",
            username="testuser"
        )
        
        assert config.validate() is True
    
    def test_validate_missing_host(self):
        """Test validation with missing host."""
        config = DatabaseConfig(host="")
        
        with pytest.raises(ValueError, match="Database host is required"):
            config.validate()
    
    def test_validate_missing_database(self):
        """Test validation with missing database."""
        config = DatabaseConfig(database="")
        
        with pytest.raises(ValueError, match="Database name is required"):
            config.validate()
    
    def test_validate_missing_username(self):
        """Test validation with missing username."""
        config = DatabaseConfig(username="")
        
        with pytest.raises(ValueError, match="Database username is required"):
            config.validate()
    
    def test_validate_invalid_port_low(self):
        """Test validation with port too low."""
        config = DatabaseConfig(port=0)
        
        with pytest.raises(ValueError, match="Port must be between 1 and 65535"):
            config.validate()
    
    def test_validate_invalid_port_high(self):
        """Test validation with port too high."""
        config = DatabaseConfig(port=65536)
        
        with pytest.raises(ValueError, match="Port must be between 1 and 65535"):
            config.validate()
    
    def test_from_file_not_found(self):
        """Test from_file with non-existent file."""
        with pytest.raises(FileNotFoundError):
            DatabaseConfig.from_file("/path/that/does/not/exist.json")
    
    def test_from_file_placeholder(self):
        """Test from_file placeholder implementation."""
        # Create a temporary file for testing
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"host": "file.example.com"}')
            temp_path = f.name
        
        try:
            # Current implementation returns default config
            config = DatabaseConfig.from_file(temp_path)
            assert config.host == "localhost"  # Should be default since file loading not implemented
        finally:
            os.unlink(temp_path)

