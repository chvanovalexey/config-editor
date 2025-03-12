import sqlite3
import json
from datetime import datetime
import os

class ConfigDatabase:
    def __init__(self, db_file="config_database.db"):
        """Initialize the database connection and create tables if they don't exist."""
        self.db_file = db_file
        self.conn = None
        self.create_tables()
    
    def connect(self):
        """Connect to the SQLite database."""
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_file)
            self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def create_tables(self):
        """Create the necessary tables if they don't exist."""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Table for configurations
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS configurations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT,
            original_config TEXT,
            generated_config TEXT,
            modified_config TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        conn.commit()
    
    def save_initial_config(self, description, original_config):
        """Save the initial configuration and return its ID."""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Validate JSON format
        try:
            json.loads(original_config)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format in original configuration")
        
        cursor.execute(
            "INSERT INTO configurations (description, original_config) VALUES (?, ?)",
            (description, original_config)
        )
        conn.commit()
        return cursor.lastrowid
    
    def update_generated_configs(self, config_id, generated_config, modified_config=None):
        """Update a configuration with generated and optionally modified configs."""
        conn = self.connect()
        cursor = conn.cursor()
        
        # Validate JSON format
        try:
            json.loads(generated_config)
            if modified_config:
                json.loads(modified_config)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format in configuration")
        
        if modified_config is None:
            modified_config = generated_config
        
        cursor.execute(
            "UPDATE configurations SET generated_config = ?, modified_config = ? WHERE id = ?",
            (generated_config, modified_config, config_id)
        )
        conn.commit()
    
    def get_config(self, config_id):
        """Get a configuration by ID."""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM configurations WHERE id = ?", (config_id,))
        return dict(cursor.fetchone())
    
    def get_all_configs(self):
        """Get all configurations with description and timestamp."""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, description, created_at FROM configurations ORDER BY created_at DESC"
        )
        return [dict(row) for row in cursor.fetchall()]
    
    def delete_config(self, config_id):
        """Delete a configuration by ID."""
        conn = self.connect()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM configurations WHERE id = ?", (config_id,))
        conn.commit() 