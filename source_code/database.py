import mysql.connector
from mysql.connector import Error
import pandas as pd

class Database:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        self.connect()
        
    def connect(self):
        """Connect to MySQL database"""
        try:
            self.connection = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            if self.connection.is_connected():
                return True
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            return False
            
    def disconnect(self):
        """Disconnect from MySQL database"""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            
    def execute_query(self, query, params=None):
        """Execute a query and return affected rows"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
                
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            self.connection.commit()
            affected_rows = cursor.rowcount
            cursor.close()
            return affected_rows
        except Error as e:
            print(f"Error executing query: {e}")
            return -1
            
    def fetch_data(self, query, params=None):
        """Execute a SELECT query and return results as DataFrame"""
        try:
            if not self.connection or not self.connection.is_connected():
                self.connect()
                
            cursor = self.connection.cursor(dictionary=True)
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            result = cursor.fetchall()
            cursor.close()
            return pd.DataFrame(result) if result else pd.DataFrame()
        except Error as e:
            print(f"Error fetching data: {e}")
            return pd.DataFrame()
            
    def get_tables(self):
        """Get list of all tables in the database"""
        query = "SHOW TABLES"
        df = self.fetch_data(query)
        if not df.empty:
            return df.iloc[:, 0].tolist()
        return []
        
    def get_table_columns(self, table_name):
        """Get column information for a table"""
        query = f"DESCRIBE {table_name}"
        return self.fetch_data(query)
        
    def get_primary_key(self, table_name):
        """Get primary key column(s) for a table"""
        columns = self.get_table_columns(table_name)
        if not columns.empty:
            pk_columns = columns[columns['Key'] == 'PRI']['Field'].tolist()
            return pk_columns
        return []
    
    # CRUD operations for each table
    def create_record(self, table_name, data):
        """Insert a new record into the specified table"""
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['%s'] * len(data))
        query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
        return self.execute_query(query, list(data.values()))
        
    def read_records(self, table_name, limit=100, where_clause=None, params=None):
        """Read records from the specified table"""
        query = f"SELECT * FROM {table_name}"
        if where_clause:
            query += f" WHERE {where_clause}"
        query += f" LIMIT {limit}"
        return self.fetch_data(query, params)
        
    def update_record(self, table_name, data, condition):
        """Update a record in the specified table"""
        set_clause = ', '.join([f"{key} = %s" for key in data.keys()])
        query = f"UPDATE {table_name} SET {set_clause} WHERE {condition}"
        return self.execute_query(query, list(data.values()))
        
    def delete_record(self, table_name, condition, params=None):
        """Delete a record from the specified table"""
        query = f"DELETE FROM {table_name} WHERE {condition}"
        return self.execute_query(query, params)
        
    def search_records(self, table_name, search_column, search_term):
        """Search for records in the specified table"""
        query = f"SELECT * FROM {table_name} WHERE {search_column} LIKE %s LIMIT 100"
        return self.fetch_data(query, [f"%{search_term}%"])
    
    # Table-specific methods for complex operations
    
    # Order operations
    def get_orders_with_details(self):
        """Get orders with customer and item details"""
        query = """
        SELECT o.*, c.cust_firstname, c.cust_lastname, i.item_name, 
               a.delivery_address1, a.delivery_city, a.delivery_zipcode
        FROM orders o
        JOIN customers c ON o.cust_id = c.cust_id
        JOIN item i ON o.item_id = i.item_id
        JOIN address a ON o.add_id = a.add_id
        ORDER BY o.created_at DESC
        LIMIT 100
        """
        return self.fetch_data(query)
    
    # Inventory operations
    def get_inventory_with_items(self):
        """Get inventory with item details"""
        query = """
        SELECT i.inv_id, i.quantity, t.item_id, t.item_name, t.item_cat, t.item_size, t.item_price
        FROM inventory i
        JOIN item t ON i.item_id = t.item_id
        """
        return self.fetch_data(query)
    
    # Staff operations
    def get_staff_schedule(self, staff_id=None):
        """Get staff schedule with shift details"""
        query = """
        SELECT r.row_id, r.rota_id, r.date, s.staff_id, 
               CONCAT(s.first_name, ' ', s.last_name) as staff_name,
               sh.day_of_week, sh.start_time, sh.end_time
        FROM rotation r
        JOIN staff s ON r.staff_id = s.staff_id
        JOIN shift sh ON r.shift_id = sh.shift_id
        """
        params = None
        if staff_id:
            query += " WHERE s.staff_id = %s"
            params = [staff_id]
        query += " ORDER BY r.date DESC"
        return self.fetch_data(query, params)
    
    # Recipe operations
    def get_recipe_with_ingredients(self, recipe_id=None):
        """Get recipe with ingredient details"""
        query = """
        SELECT r.recipe_id, i.item_name, r.row_id, 
               ing.ing_id, ing.ing_name, r.quantity, 
               ing.ing_meas, ing.ing_price
        FROM recipe r
        JOIN ingredient ing ON r.ing_id = ing.ing_id
        JOIN item i ON r.recipe_id = i.sku
        """
        params = None
        if recipe_id:
            query += " WHERE r.recipe_id = %s"
            params = [recipe_id]
        return self.fetch_data(query, params)