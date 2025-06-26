"""
Database configuration module.

This module provides configuration management for database connections
and operations settings.
"""

import os
from dataclasses import dataclass
from typing import Optional, Dict, Any
from pathlib import Path


@dataclass
class DatabaseConfig:
    """Database configuration class."""
    
    host: str = "localhost"
    port: int = 5432
    database: str = "postgres"
    username: str = "postgres"
    password: Optional[str] = None
    driver: str = "postgresql"
    connection_timeout: int = 30
    pool_size: int = 5
    max_overflow: int = 10
    echo: bool = False
    
    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        """
        Create configuration from environment variables.
        
        Returns:
            DatabaseConfig: Configuration object with values from environment
        """
        return cls(
            host=os.getenv('DB_HOST', 'localhost'),
            port=int(os.getenv('DB_PORT', '5432')),
            database=os.getenv('DB_NAME', 'postgres'),
            username=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD'),
            driver=os.getenv('DB_DRIVER', 'postgresql'),
            connection_timeout=int(os.getenv('DB_TIMEOUT', '30')),
            pool_size=int(os.getenv('DB_POOL_SIZE', '5')),
            max_overflow=int(os.getenv('DB_MAX_OVERFLOW', '10')),
            echo=os.getenv('DB_ECHO', 'false').lower() == 'true'
        )
    
    @classmethod
    def from_file(cls, config_path: str) -> 'DatabaseConfig':
        """
        Load configuration from a file.
        
        Args:
            config_path (str): Path to configuration file
            
        Returns:
            DatabaseConfig: Configuration object
        """
        config_file = Path(config_path)
        if not config_file.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        # TODO: Implement file loading logic (JSON, YAML, etc.)
        # For now, return default configuration
        return cls()
    
    def get_connection_string(self) -> str:
        """
        Generate database connection string.
        
        Returns:
            str: Database connection string
        """
        if self.password:
            return f"{self.driver}://{self.username}:{self.password}@{self.host}:{self.port}/{self.database}"
        else:
            return f"{self.driver}://{self.username}@{self.host}:{self.port}/{self.database}"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert configuration to dictionary.
        
        Returns:
            Dict[str, Any]: Configuration as dictionary
        """
        return {
            'host': self.host,
            'port': self.port,
            'database': self.database,
            'username': self.username,
            'password': '***' if self.password else None,  # Mask password
            'driver': self.driver,
            'connection_timeout': self.connection_timeout,
            'pool_size': self.pool_size,
            'max_overflow': self.max_overflow,
            'echo': self.echo
        }
    
    def validate(self) -> bool:
        """
        Validate configuration parameters.
        
        Returns:
            bool: True if configuration is valid
        """
        if not self.host:
            raise ValueError("Database host is required")
        if not self.database:
            raise ValueError("Database name is required")
        if not self.username:
            raise ValueError("Database username is required")
        if self.port <= 0 or self.port > 65535:
            raise ValueError("Port must be between 1 and 65535")
        
        return True

