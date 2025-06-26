"""
Database utilities module.

This module provides utility functions and helper classes for database operations.
"""

import re
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
from decimal import Decimal


logger = logging.getLogger(__name__)


class DatabaseUtils:
    """Utility class for database operations."""
    
    @staticmethod
    def sanitize_table_name(table_name: str) -> str:
        """
        Sanitize table name to prevent SQL injection.
        
        Args:
            table_name (str): Table name to sanitize
            
        Returns:
            str: Sanitized table name
        """
        # Remove any characters that are not alphanumeric or underscore
        sanitized = re.sub(r'[^a-zA-Z0-9_]', '', table_name)
        
        # Ensure it doesn't start with a number
        if sanitized and sanitized[0].isdigit():
            sanitized = f"t_{sanitized}"
            
        return sanitized
    
    @staticmethod
    def escape_string(value: str) -> str:
        """
        Escape string for SQL queries.
        
        Args:
            value (str): String to escape
            
        Returns:
            str: Escaped string
        """
        # Basic escaping - in production, use parameterized queries instead
        return value.replace("'", "''").replace("\\", "\\\\")
    
    @staticmethod
    def format_value_for_sql(value: Any) -> str:
        """
        Format Python value for SQL insertion.
        
        Args:
            value (Any): Value to format
            
        Returns:
            str: SQL-formatted value
        """
        if value is None:
            return "NULL"
        elif isinstance(value, str):
            return f"'{DatabaseUtils.escape_string(value)}'"
        elif isinstance(value, bool):
            return "TRUE" if value else "FALSE"
        elif isinstance(value, (int, float, Decimal)):
            return str(value)
        elif isinstance(value, (datetime, date)):
            return f"'{value.isoformat()}'"
        else:
            return f"'{str(value)}'"
    
    @staticmethod
    def build_insert_query(table: str, data: Dict[str, Any]) -> str:
        """
        Build INSERT query from data dictionary.
        
        Args:
            table (str): Table name
            data (Dict[str, Any]): Data to insert
            
        Returns:
            str: INSERT query
        """
        table = DatabaseUtils.sanitize_table_name(table)
        columns = list(data.keys())
        values = [DatabaseUtils.format_value_for_sql(data[col]) for col in columns]
        
        columns_str = ", ".join(columns)
        values_str = ", ".join(values)
        
        return f"INSERT INTO {table} ({columns_str}) VALUES ({values_str})"
    
    @staticmethod
    def build_update_query(table: str, data: Dict[str, Any], where_clause: str) -> str:
        """
        Build UPDATE query from data dictionary.
        
        Args:
            table (str): Table name
            data (Dict[str, Any]): Data to update
            where_clause (str): WHERE clause
            
        Returns:
            str: UPDATE query
        """
        table = DatabaseUtils.sanitize_table_name(table)
        set_clauses = []
        
        for column, value in data.items():
            formatted_value = DatabaseUtils.format_value_for_sql(value)
            set_clauses.append(f"{column} = {formatted_value}")
        
        set_clause = ", ".join(set_clauses)
        
        return f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
    
    @staticmethod
    def parse_connection_string(connection_string: str) -> Dict[str, str]:
        """
        Parse database connection string into components.
        
        Args:
            connection_string (str): Connection string
            
        Returns:
            Dict[str, str]: Connection components
        """
        # Pattern for: driver://username:password@host:port/database
        pattern = r'(\w+)://([^:]+):([^@]+)@([^:]+):(\d+)/(.+)'
        match = re.match(pattern, connection_string)
        
        if match:
            return {
                'driver': match.group(1),
                'username': match.group(2),
                'password': match.group(3),
                'host': match.group(4),
                'port': match.group(5),
                'database': match.group(6)
            }
        else:
            raise ValueError(f"Invalid connection string format: {connection_string}")
    
    @staticmethod
    def validate_sql_query(query: str) -> bool:
        """
        Basic SQL query validation.
        
        Args:
            query (str): SQL query to validate
            
        Returns:
            bool: True if query appears valid
        """
        if not query or not query.strip():
            return False
        
        # Check for basic SQL injection patterns
        dangerous_patterns = [
            r';\s*drop\s+table',
            r';\s*delete\s+from',
            r';\s*truncate\s+table',
            r'union\s+select.*from',
            r'--\s*',
            r'/\*.*\*/'
        ]
        
        query_lower = query.lower()
        for pattern in dangerous_patterns:
            if re.search(pattern, query_lower):
                logger.warning(f"Potentially dangerous SQL pattern detected: {pattern}")
                return False
        
        return True
    
    @staticmethod
    def get_table_info_query(table_name: str, database_type: str = 'postgresql') -> str:
        """
        Generate query to get table information.
        
        Args:
            table_name (str): Name of the table
            database_type (str): Type of database
            
        Returns:
            str: Query to get table information
        """
        table_name = DatabaseUtils.sanitize_table_name(table_name)
        
        if database_type.lower() == 'postgresql':
            return f"""
                SELECT column_name, data_type, is_nullable, column_default
                FROM information_schema.columns
                WHERE table_name = '{table_name}'
                ORDER BY ordinal_position;
            """
        elif database_type.lower() == 'mysql':
            return f"DESCRIBE {table_name};"
        elif database_type.lower() == 'sqlite':
            return f"PRAGMA table_info({table_name});"
        else:
            raise ValueError(f"Unsupported database type: {database_type}")
    
    @staticmethod
    def format_query_results(results: List[Dict[str, Any]], max_width: int = 80) -> str:
        """
        Format query results for display.
        
        Args:
            results (List[Dict[str, Any]]): Query results
            max_width (int): Maximum column width
            
        Returns:
            str: Formatted results
        """
        if not results:
            return "No results found."
        
        # Get column names
        columns = list(results[0].keys())
        
        # Calculate column widths
        col_widths = {}
        for col in columns:
            col_widths[col] = min(max_width, max(
                len(col),
                max(len(str(row.get(col, ''))) for row in results)
            ))
        
        # Format header
        header = " | ".join(col.ljust(col_widths[col]) for col in columns)
        separator = "-+-".join("-" * col_widths[col] for col in columns)
        
        # Format rows
        rows = []
        for row in results:
            formatted_row = " | ".join(
                str(row.get(col, '')).ljust(col_widths[col])[:col_widths[col]]
                for col in columns
            )
            rows.append(formatted_row)
        
        return "\n".join([header, separator] + rows)

