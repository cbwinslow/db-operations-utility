"""
Tests for the core database operations module.
"""

import pytest
from unittest.mock import Mock, patch
from src.db_operations.core import DatabaseOperations
from src.db_operations.config import DatabaseConfig


class TestDatabaseOperations:
    """Test cases for DatabaseOperations class."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = DatabaseConfig(
            host="localhost",
            port=5432,
            database="test_db",
            username="test_user",
            password="test_pass"
        )
        self.db_ops = DatabaseOperations(self.config)
    
    def test_initialization(self):
        """Test DatabaseOperations initialization."""
        assert self.db_ops.config == self.config
        assert self.db_ops.connection is None
        assert self.db_ops.utils is not None
    
    def test_connect(self):
        """Test database connection."""
        with patch.object(self.db_ops, 'connection') as mock_conn:
            self.db_ops.connect()
            # Connection logic will be implemented later
            # For now, just test that the method doesn't raise an exception
    
    def test_disconnect(self):
        """Test database disconnection."""
        self.db_ops.connection = Mock()
        self.db_ops.disconnect()
        assert self.db_ops.connection is None
    
    def test_disconnect_no_connection(self):
        """Test disconnection when no connection exists."""
        self.db_ops.connection = None
        # Should not raise an exception
        self.db_ops.disconnect()
    
    def test_get_connection_context_manager(self):
        """Test connection context manager."""
        with patch.object(self.db_ops, 'connect') as mock_connect, \
             patch.object(self.db_ops, 'disconnect') as mock_disconnect:
            
            with self.db_ops.get_connection():
                pass
            
            mock_connect.assert_called_once()
            mock_disconnect.assert_called_once()
    
    def test_execute_query(self):
        """Test query execution."""
        query = "SELECT * FROM users"
        params = {"limit": 10}
        
        result = self.db_ops.execute_query(query, params)
        
        # Currently returns empty list as placeholder
        assert isinstance(result, list)
        assert len(result) == 0
    
    def test_execute_command(self):
        """Test command execution."""
        command = "INSERT INTO users (name) VALUES ('test')"
        params = {"name": "test"}
        
        result = self.db_ops.execute_command(command, params)
        
        # Currently returns 0 as placeholder
        assert isinstance(result, int)
        assert result == 0
    
    def test_bulk_insert(self):
        """Test bulk insert operation."""
        table = "users"
        data = [
            {"name": "John", "email": "john@example.com"},
            {"name": "Jane", "email": "jane@example.com"}
        ]
        
        result = self.db_ops.bulk_insert(table, data)
        
        # Currently returns length of data as placeholder
        assert isinstance(result, int)
        assert result == len(data)
    
    def test_bulk_insert_empty_data(self):
        """Test bulk insert with empty data."""
        table = "users"
        data = []
        
        result = self.db_ops.bulk_insert(table, data)
        
        assert isinstance(result, int)
        assert result == 0


class TestDatabaseOperationsIntegration:
    """Integration tests for DatabaseOperations."""
    
    def test_full_workflow(self):
        """Test a complete database operations workflow."""
        config = DatabaseConfig.from_env()
        db_ops = DatabaseOperations(config)
        
        # Test that all components work together
        assert db_ops.config is not None
        assert db_ops.utils is not None
        
        # Test query and command methods exist and are callable
        assert callable(db_ops.execute_query)
        assert callable(db_ops.execute_command)
        assert callable(db_ops.bulk_insert)

