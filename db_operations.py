"""
Database Operations Utility

A comprehensive Python utility script for handling common database operations
with PostgreSQL using SQLAlchemy. Provides connection management, CRUD operations,
query interface, and robust error handling.
"""

import logging
from contextlib import contextmanager
from typing import Dict, List, Optional, Any, Union
from sqlalchemy import create_engine, text, MetaData, Table, Column, Integer, String, DateTime, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError
from sqlalchemy.pool import QueuePool
from datetime import datetime
import os


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseError(Exception):
    """Custom exception for database operations"""
    pass


class DatabaseManager:
    """
    Database manager class that handles PostgreSQL operations using SQLAlchemy.
    Provides connection management, CRUD operations, and query execution.
    """
    
    def __init__(self, connection_string: Optional[str] = None):
        """
        Initialize the database manager.
        
        Args:
            connection_string: PostgreSQL connection string. If None, uses default.
        """
        self.connection_string = connection_string or 'postgresql://cbwinslow@localhost/camel_web'
        self.engine = None
        self.Session = None
        self.metadata = MetaData()
        self._connect()
    
    def _connect(self):
        """Establish database connection and create session factory."""
        try:
            self.engine = create_engine(
                self.connection_string,
                poolclass=QueuePool,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,  # Verify connections before use
                echo=False  # Set to True for SQL query logging
            )
            self.Session = sessionmaker(bind=self.engine)
            logger.info("Database connection established successfully")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise DatabaseError(f"Database connection failed: {e}")
    
    @contextmanager
    def session_scope(self):
        """
        Provide a transactional scope around a series of operations.
        Automatically handles commit/rollback and session cleanup.
        """
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        """
        Test database connectivity.
        
        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            with self.session_scope() as session:
                session.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False
    
    # CRUD Operations
    
    def create_record(self, table_name: str, data: Dict[str, Any]) -> Optional[int]:
        """
        Create a new record in the specified table.
        
        Args:
            table_name: Name of the table
            data: Dictionary of column names and values
            
        Returns:
            int: ID of the created record if available, None otherwise
        """
        try:
            with self.session_scope() as session:
                # Build INSERT query
                columns = ', '.join(data.keys())
                placeholders = ', '.join([f":{key}" for key in data.keys()])
                query = text(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders}) RETURNING id")
                
                result = session.execute(query, data)
                record_id = result.fetchone()
                
                logger.info(f"Created record in {table_name} with ID: {record_id[0] if record_id else 'N/A'}")
                return record_id[0] if record_id else None
                
        except IntegrityError as e:
            logger.error(f"Integrity constraint violation: {e}")
            raise DatabaseError(f"Failed to create record due to constraint violation: {e}")
        except Exception as e:
            logger.error(f"Error creating record in {table_name}: {e}")
            raise DatabaseError(f"Failed to create record: {e}")
    
    def read_record(self, table_name: str, record_id: int) -> Optional[Dict[str, Any]]:
        """
        Read a single record by ID.
        
        Args:
            table_name: Name of the table
            record_id: ID of the record to retrieve
            
        Returns:
            Dict containing the record data, or None if not found
        """
        try:
            with self.session_scope() as session:
                query = text(f"SELECT * FROM {table_name} WHERE id = :id")
                result = session.execute(query, {"id": record_id})
                record = result.fetchone()
                
                if record:
                    # Convert to dictionary
                    columns = result.keys()
                    record_dict = dict(zip(columns, record))
                    logger.info(f"Retrieved record {record_id} from {table_name}")
                    return record_dict
                else:
                    logger.warning(f"Record {record_id} not found in {table_name}")
                    return None
                    
        except Exception as e:
            logger.error(f"Error reading record {record_id} from {table_name}: {e}")
            raise DatabaseError(f"Failed to read record: {e}")
    
    def read_records(self, table_name: str, conditions: Optional[Dict[str, Any]] = None, 
                    limit: Optional[int] = None, offset: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Read multiple records with optional filtering.
        
        Args:
            table_name: Name of the table
            conditions: Dictionary of column names and values for WHERE clause
            limit: Maximum number of records to return
            offset: Number of records to skip
            
        Returns:
            List of dictionaries containing record data
        """
        try:
            with self.session_scope() as session:
                query_str = f"SELECT * FROM {table_name}"
                params = {}
                
                # Add WHERE clause if conditions provided
                if conditions:
                    where_clauses = []
                    for key, value in conditions.items():
                        where_clauses.append(f"{key} = :{key}")
                        params[key] = value
                    query_str += " WHERE " + " AND ".join(where_clauses)
                
                # Add LIMIT and OFFSET
                if limit:
                    query_str += f" LIMIT {limit}"
                if offset:
                    query_str += f" OFFSET {offset}"
                
                query = text(query_str)
                result = session.execute(query, params)
                records = result.fetchall()
                
                # Convert to list of dictionaries
                columns = result.keys()
                records_list = [dict(zip(columns, record)) for record in records]
                
                logger.info(f"Retrieved {len(records_list)} records from {table_name}")
                return records_list
                
        except Exception as e:
            logger.error(f"Error reading records from {table_name}: {e}")
            raise DatabaseError(f"Failed to read records: {e}")
    
    def update_record(self, table_name: str, record_id: int, data: Dict[str, Any]) -> bool:
        """
        Update a record by ID.
        
        Args:
            table_name: Name of the table
            record_id: ID of the record to update
            data: Dictionary of column names and new values
            
        Returns:
            bool: True if record was updated, False if not found
        """
        try:
            with self.session_scope() as session:
                # Build UPDATE query
                set_clauses = [f"{key} = :{key}" for key in data.keys()]
                query_str = f"UPDATE {table_name} SET {', '.join(set_clauses)} WHERE id = :id"
                
                params = data.copy()
                params['id'] = record_id
                
                query = text(query_str)
                result = session.execute(query, params)
                
                if result.rowcount > 0:
                    logger.info(f"Updated record {record_id} in {table_name}")
                    return True
                else:
                    logger.warning(f"Record {record_id} not found in {table_name} for update")
                    return False
                    
        except IntegrityError as e:
            logger.error(f"Integrity constraint violation during update: {e}")
            raise DatabaseError(f"Failed to update record due to constraint violation: {e}")
        except Exception as e:
            logger.error(f"Error updating record {record_id} in {table_name}: {e}")
            raise DatabaseError(f"Failed to update record: {e}")
    
    def delete_record(self, table_name: str, record_id: int) -> bool:
        """
        Delete a record by ID.
        
        Args:
            table_name: Name of the table
            record_id: ID of the record to delete
            
        Returns:
            bool: True if record was deleted, False if not found
        """
        try:
            with self.session_scope() as session:
                query = text(f"DELETE FROM {table_name} WHERE id = :id")
                result = session.execute(query, {"id": record_id})
                
                if result.rowcount > 0:
                    logger.info(f"Deleted record {record_id} from {table_name}")
                    return True
                else:
                    logger.warning(f"Record {record_id} not found in {table_name} for deletion")
                    return False
                    
        except IntegrityError as e:
            logger.error(f"Integrity constraint violation during deletion: {e}")
            raise DatabaseError(f"Failed to delete record due to constraint violation: {e}")
        except Exception as e:
            logger.error(f"Error deleting record {record_id} from {table_name}: {e}")
            raise DatabaseError(f"Failed to delete record: {e}")
    
    # Query Interface
    
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a custom SELECT query.
        
        Args:
            query: SQL SELECT query string
            params: Dictionary of query parameters
            
        Returns:
            List of dictionaries containing query results
        """
        try:
            with self.session_scope() as session:
                result = session.execute(text(query), params or {})
                records = result.fetchall()
                
                # Convert to list of dictionaries
                columns = result.keys()
                records_list = [dict(zip(columns, record)) for record in records]
                
                logger.info(f"Executed query, returned {len(records_list)} records")
                return records_list
                
        except Exception as e:
            logger.error(f"Error executing query: {e}")
            raise DatabaseError(f"Query execution failed: {e}")
    
    def execute_command(self, command: str, params: Optional[Dict[str, Any]] = None) -> int:
        """
        Execute a non-SELECT SQL command (INSERT, UPDATE, DELETE, etc.).
        
        Args:
            command: SQL command string
            params: Dictionary of command parameters
            
        Returns:
            int: Number of affected rows
        """
        try:
            with self.session_scope() as session:
                result = session.execute(text(command), params or {})
                affected_rows = result.rowcount
                
                logger.info(f"Executed command, affected {affected_rows} rows")
                return affected_rows
                
        except Exception as e:
            logger.error(f"Error executing command: {e}")
            raise DatabaseError(f"Command execution failed: {e}")
    
    # Utility Methods
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """
        Get information about a table's structure.
        
        Args:
            table_name: Name of the table
            
        Returns:
            Dictionary containing table information
        """
        try:
            inspector = inspect(self.engine)
            columns = inspector.get_columns(table_name)
            primary_keys = inspector.get_pk_constraint(table_name)
            foreign_keys = inspector.get_foreign_keys(table_name)
            indexes = inspector.get_indexes(table_name)
            
            table_info = {
                'columns': columns,
                'primary_keys': primary_keys,
                'foreign_keys': foreign_keys,
                'indexes': indexes
            }
            
            logger.info(f"Retrieved table info for {table_name}")
            return table_info
            
        except Exception as e:
            logger.error(f"Error getting table info for {table_name}: {e}")
            raise DatabaseError(f"Failed to get table info: {e}")
    
    def list_tables(self) -> List[str]:
        """
        Get list of all tables in the database.
        
        Returns:
            List of table names
        """
        try:
            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            
            logger.info(f"Retrieved {len(tables)} tables from database")
            return tables
            
        except Exception as e:
            logger.error(f"Error listing tables: {e}")
            raise DatabaseError(f"Failed to list tables: {e}")
    
    def backup_table(self, table_name: str, backup_file: str) -> bool:
        """
        Backup a table to a SQL file.
        
        Args:
            table_name: Name of the table to backup
            backup_file: Path to the backup file
            
        Returns:
            bool: True if backup was successful
        """
        try:
            import subprocess
            
            # Use pg_dump to backup the specific table
            cmd = [
                'pg_dump',
                '-h', 'localhost',
                '-U', 'cbwinslow',
                '-t', table_name,
                '-f', backup_file,
                'camel_web'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info(f"Successfully backed up table {table_name} to {backup_file}")
                return True
            else:
                logger.error(f"Backup failed: {result.stderr}")
                return False
                
        except Exception as e:
            logger.error(f"Error backing up table {table_name}: {e}")
            return False
    
    def close(self):
        """Close database connections."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connections closed")


# Example usage and testing functions
def main():
    """Example usage of the DatabaseManager class."""
    try:
        # Initialize database manager
        db = DatabaseManager()
        
        # Test connection
        if not db.test_connection():
            print("Failed to connect to database")
            return
        
        # List all tables
        tables = db.list_tables()
        print(f"Available tables: {tables}")
        
        # Example CRUD operations (commented out to avoid errors if table doesn't exist)
        """
        # Create a record
        new_id = db.create_record('users', {
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            'created_at': datetime.now()
        })
        print(f"Created user with ID: {new_id}")
        
        # Read the record
        user = db.read_record('users', new_id)
        print(f"Retrieved user: {user}")
        
        # Update the record
        db.update_record('users', new_id, {'name': 'Jane Doe'})
        print("Updated user name")
        
        # Read multiple records
        users = db.read_records('users', limit=10)
        print(f"Retrieved {len(users)} users")
        
        # Execute custom query
        results = db.execute_query(
            "SELECT * FROM users WHERE email LIKE :pattern",
            {'pattern': '%@example.com'}
        )
        print(f"Query returned {len(results)} results")
        """
        
    except DatabaseError as e:
        print(f"Database error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        # Clean up
        if 'db' in locals():
            db.close()


if __name__ == "__main__":
    main()

