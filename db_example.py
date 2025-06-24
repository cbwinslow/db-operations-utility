#!/usr/bin/env python3
"""
Database Operations Example

Demonstrates how to use the db_operations.py utility for common database tasks.
This script shows practical examples of CRUD operations, queries, and utilities.
"""

import sys
import os
from datetime import datetime
from db_operations import DatabaseManager, DatabaseError
from db_config import DatabaseConfig


def demo_basic_operations():
    """Demonstrate basic CRUD operations."""
    print("=== Basic CRUD Operations Demo ===")
    
    try:
        # Initialize database manager
        config = DatabaseConfig()
        db = DatabaseManager(config.get_connection_string())
        
        # Test connection
        if not db.test_connection():
            print("❌ Failed to connect to database")
            return False
        
        print("✅ Database connection successful")
        
        # List all tables
        tables = db.list_tables()
        print(f"📋 Available tables: {tables}")
        
        if not tables:
            print("ℹ️  No tables found in database")
            return True
        
        # If there are tables, try to get info about the first one
        if tables:
            table_name = tables[0]
            print(f"\n📊 Getting info for table '{table_name}':")
            try:
                table_info = db.get_table_info(table_name)
                print(f"   - Columns: {len(table_info['columns'])}")
                print(f"   - Primary keys: {table_info['primary_keys']}")
                print(f"   - Foreign keys: {len(table_info['foreign_keys'])}")
                print(f"   - Indexes: {len(table_info['indexes'])}")
            except Exception as e:
                print(f"   ⚠️  Could not get table info: {e}")
        
        return True
        
    except DatabaseError as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        if 'db' in locals():
            db.close()


def demo_table_creation_and_crud():
    """Demonstrate creating a test table and performing CRUD operations."""
    print("\n=== Table Creation and CRUD Demo ===")
    
    try:
        config = DatabaseConfig()
        db = DatabaseManager(config.get_connection_string())
        
        if not db.test_connection():
            print("❌ Database connection failed")
            return False
        
        # Create a test table
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS test_users (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            age INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """
        
        print("📝 Creating test table...")
        db.execute_command(create_table_sql)
        print("✅ Test table created successfully")
        
        # INSERT operation
        print("\n➕ Creating test records...")
        test_users = [
            {'name': 'Alice Johnson', 'email': 'alice@example.com', 'age': 28},
            {'name': 'Bob Smith', 'email': 'bob@example.com', 'age': 34},
            {'name': 'Carol Brown', 'email': 'carol@example.com', 'age': 22}
        ]
        
        user_ids = []
        for user in test_users:
            try:
                user_id = db.create_record('test_users', user)
                user_ids.append(user_id)
                print(f"   ✅ Created user '{user['name']}' with ID: {user_id}")
            except Exception as e:
                print(f"   ⚠️  Could not create user '{user['name']}': {e}")
        
        if not user_ids:
            print("❌ No users were created successfully")
            return False
        
        # READ operations
        print(f"\n📖 Reading records...")
        
        # Read single record
        if user_ids[0]:
            user = db.read_record('test_users', user_ids[0])
            if user:
                print(f"   📄 Single record: {user['name']} ({user['email']})")
        
        # Read multiple records
        all_users = db.read_records('test_users', limit=10)
        print(f"   📄 Total records retrieved: {len(all_users)}")
        
        # Read with conditions
        adult_users = db.read_records('test_users', conditions={'age': 28})
        print(f"   📄 Users aged 28: {len(adult_users)}")
        
        # UPDATE operations
        print("\n✏️  Updating records...")
        if user_ids[0]:
            success = db.update_record('test_users', user_ids[0], 
                                     {'name': 'Alice Johnson-Updated', 'age': 29})
            if success:
                print(f"   ✅ Updated user {user_ids[0]}")
        
        # Custom QUERY
        print("\n🔍 Custom query demo...")
        results = db.execute_query(
            "SELECT name, email, age FROM test_users WHERE age > :min_age ORDER BY age",
            {'min_age': 25}
        )
        print(f"   📊 Users over 25: {len(results)}")
        for user in results:
            print(f"      - {user['name']} ({user['age']} years)")
        
        # DELETE operations
        print("\n🗑️  Cleanup - deleting test records...")
        deleted_count = 0
        for user_id in user_ids:
            if user_id and db.delete_record('test_users', user_id):
                deleted_count += 1
        
        print(f"   ✅ Deleted {deleted_count} test records")
        
        # Drop test table
        print("🗑️  Dropping test table...")
        db.execute_command("DROP TABLE IF EXISTS test_users")
        print("   ✅ Test table dropped")
        
        return True
        
    except DatabaseError as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        if 'db' in locals():
            db.close()


def demo_advanced_queries():
    """Demonstrate advanced query capabilities."""
    print("\n=== Advanced Query Demo ===")
    
    try:
        config = DatabaseConfig()
        db = DatabaseManager(config.get_connection_string())
        
        if not db.test_connection():
            print("❌ Database connection failed")
            return False
        
        # Get database metadata
        print("🔍 Database metadata queries...")
        
        # List all tables with row counts
        tables = db.list_tables()
        print(f"📋 Database contains {len(tables)} tables:")
        
        for table in tables[:5]:  # Limit to first 5 tables
            try:
                count_result = db.execute_query(f"SELECT COUNT(*) as row_count FROM {table}")
                row_count = count_result[0]['row_count'] if count_result else 0
                print(f"   - {table}: {row_count} rows")
            except Exception as e:
                print(f"   - {table}: Could not get row count ({e})")
        
        if len(tables) > 5:
            print(f"   ... and {len(tables) - 5} more tables")
        
        # Database version and info
        print("\n🔧 Database system information:")
        try:
            version_result = db.execute_query("SELECT version()")
            if version_result:
                version = version_result[0]['version']
                print(f"   PostgreSQL Version: {version[:50]}...")
            
            # Current database and user
            db_info = db.execute_query("SELECT current_database(), current_user, current_timestamp")
            if db_info:
                info = db_info[0]
                print(f"   Current Database: {info['current_database']}")
                print(f"   Current User: {info['current_user']}")
                print(f"   Current Time: {info['current_timestamp']}")
                
        except Exception as e:
            print(f"   ⚠️  Could not retrieve system info: {e}")
        
        return True
        
    except DatabaseError as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False
    finally:
        if 'db' in locals():
            db.close()


def main():
    """Main demo function."""
    print("🚀 Database Operations Utility Demo")
    print("=" * 50)
    
    # Check if virtual environment is activated
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Warning: Virtual environment may not be activated")
        print("   Run: source venv/bin/activate")
    
    success_count = 0
    total_demos = 3
    
    # Run demonstrations
    if demo_basic_operations():
        success_count += 1
    
    if demo_table_creation_and_crud():
        success_count += 1
    
    if demo_advanced_queries():
        success_count += 1
    
    # Summary
    print(f"\n{'=' * 50}")
    print(f"🎯 Demo Summary: {success_count}/{total_demos} demos completed successfully")
    
    if success_count == total_demos:
        print("🎉 All demonstrations completed successfully!")
        print("\n📚 Next steps:")
        print("   1. Modify db_config.py to set your database credentials")
        print("   2. Use DatabaseManager in your own applications")
        print("   3. Extend with additional utility methods as needed")
    else:
        print("⚠️  Some demonstrations failed. Check your database connection and credentials.")
        print("\n🔧 Troubleshooting:")
        print("   1. Ensure PostgreSQL is running")
        print("   2. Check database credentials in db_config.py")
        print("   3. Verify database 'camel_web' exists")
        print("   4. Check user permissions")


if __name__ == "__main__":
    main()

