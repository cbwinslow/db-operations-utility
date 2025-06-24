"""
Database Configuration Module

Provides configuration management for database connections.
Supports environment variables and default values.
"""

import os
from typing import Dict, Any


class DatabaseConfig:
    """Database configuration manager."""
    
    def __init__(self):
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables with defaults."""
        return {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'camel_web'),
            'username': os.getenv('DB_USER', 'cbwinslow'),
            'password': os.getenv('DB_PASSWORD', ''),  # Empty by default for security
            'pool_size': int(os.getenv('DB_POOL_SIZE', '10')),
            'max_overflow': int(os.getenv('DB_MAX_OVERFLOW', '20')),
            'echo': os.getenv('DB_ECHO', 'false').lower() == 'true'
        }
    
    def get_connection_string(self) -> str:
        """Generate PostgreSQL connection string."""
        if self.config['password']:
            return (f"postgresql://{self.config['username']}:{self.config['password']}"
                   f"@{self.config['host']}:{self.config['port']}/{self.config['database']}")
        else:
            return (f"postgresql://{self.config['username']}"
                   f"@{self.config['host']}:{self.config['port']}/{self.config['database']}")
    
    def get_pool_config(self) -> Dict[str, Any]:
        """Get connection pool configuration."""
        return {
            'pool_size': self.config['pool_size'],
            'max_overflow': self.config['max_overflow'],
            'echo': self.config['echo']
        }


# Example usage
if __name__ == "__main__":
    config = DatabaseConfig()
    print(f"Connection string: {config.get_connection_string()}")
    print(f"Pool config: {config.get_pool_config()}")

