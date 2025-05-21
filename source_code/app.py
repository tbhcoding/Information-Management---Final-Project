import streamlit as st
import pandas as pd
from database import Database
import datetime

# Initialize database connection
@st.cache_resource
def get_database_connection():
    db = Database(
        host=st.secrets.get("db_host", "localhost"),
        user=st.secrets.get("db_user", "root"),
        password=st.secrets.get("db_password", ""),  # Change this to your MySQL password
        database=st.secrets.get("db_name", "icecream_shop")
    )
    return db

# App configuration
st.set_page_config(
    page_title="Ice Cream Shop Management",
    page_icon="🍦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Application title
st.title("🍦 Ice Cream Shop Management System")

# Initialize database connection
db = get_database_connection()

# Get tables
tables = db.get_tables()

# Sidebar for navigation
st.sidebar.title("Navigation")
selected_table = st.sidebar.radio("Select a table or view", 
    ["Dashboard"] + tables + ["Order Management", "Inventory Management", "Staff Schedule", "Recipe Management"])

# CRUD operations
crud_operation = None

if selected_table != "Dashboard" and selected_table not in ["Order Management", "Inventory Management", "Staff Schedule", "Recipe Management"]:
    crud_operation = st.sidebar.radio("Operation", ["View", "Add", "Edit", "Delete", "Search"])

# Dashboard
if selected_table == "Dashboard":
    st.header("Dashboard")
    
    # Create layout with columns
    col1, col2 = st.columns(2)
    
    # Overview statistics
    with col1:
        st.subheader("Overview")
        
        # Get total number of orders
        orders_count = db.fetch_data("SELECT COUNT(*) as count FROM orders").iloc[0, 0]
        # Get total number of items
        items_count = db.fetch_data("SELECT COUNT(*) as count FROM item").iloc[0, 0]
        # Get total number of customers
        customers_count = db.fetch_data("SELECT COUNT(*) as count FROM customers").iloc[0, 0]
        # Get total number of staff
        staff_count = db.fetch_data("SELECT COUNT(*) as count FROM staff").iloc[0, 0]
        
        # Display statistics in a nice format
        st.metric("Total Orders", orders_count)
        st.metric("Total Items", items_count)
        st.metric("Total Customers", customers_count)
        st.metric("Total Staff", staff_count)
    
    with col2:
        st.subheader("Quick Links")
        st.write("Access frequently used sections:")
        
        # Create buttons for quick access
        if st.button("📝 Manage Orders"):
            st.session_state.selected_table = "Order Management"
            st.experimental_rerun()
        
        if st.button("📦 Manage Inventory"):
            st.session_state.selected_table = "Inventory Management"
            st.experimental_rerun()
        
        if st.button("👨‍👩‍👧‍👦 Staff Schedule"):
            st.session_state.selected_table = "Staff Schedule"
            st.experimental_rerun()
        
        if st.button("📋 Recipe Management"):
            st.session_state.selected_table = "Recipe Management"
            st.experimental_rerun()
    
    # Recent orders
    st.subheader("Recent Orders")
    recent_orders = db.get_orders_with_details().head(5)
    if not recent_orders.empty:
        st.dataframe(recent_orders)
    else:
        st.info("No recent orders found.")
    
    # Low stock alert
    st.subheader("Low Stock Alert")
    low_stock = db.fetch_data("""
        SELECT i.inv_id, t.item_name, i.quantity 
        FROM inventory i 
        JOIN item t ON i.item_id = t.item_id 
        WHERE i.quantity < 10
        """)
    
    if not low_stock.empty:
        st.warning("The following items are running low on stock:")
        st.dataframe(low_stock)
    else:
        st.success("All items have sufficient stock.")

# Standard table view/edit/delete operations
elif selected_table in tables:
    st.header(f"{selected_table.capitalize()} Management")
    
    # Get table columns and primary key
    columns_info = db.get_table_columns(selected_table)
    primary_keys = db.get_primary_key(selected_table)
    
    # View operation
    if crud_operation == "View":
        st.subheader(f"View {selected_table}")
        
        # Show the data
        data = db.read_records(selected_table)
        if not data.empty:
            st.dataframe(data)
        else:
            st.info(f"No records found in {selected_table}")
    
    # Add operation
    elif crud_operation == "Add":
        st.subheader(f"Add New {selected_table[:-1] if selected_table.endswith('s') else selected_table}")
        
        # Create a form for adding new records
        with st.form(key=f"add_{selected_table}"):
            # Create input fields for each column
            form_data = {}
            
            for _, row in columns_info.iterrows():
                field = row['Field']
                field_type = row['Type']
                
                # Skip auto-increment fields
                if "auto_increment" in row.get('Extra', ''):
                    continue
                
                # Create appropriate input field based on column type
                if 'int' in field_type.lower():
                    form_data[field] = st.number_input(f"{field}", step=1)
                elif 'decimal' in field_type.lower():
                    form_data[field] = st.number_input(f"{field}", step=0.01, format="%.2f")
                elif 'datetime' in field_type.lower():
                    form_data[field] = st.date_input(f"{field}", datetime.datetime.now())
                elif 'date' in field_type.lower():
                    form_data[field] = st.date_input(f"{field}", datetime.date.today())
                elif 'time' in field_type.lower():
                    form_data[field] = st.time_input(f"{field}", datetime.time(0, 0))
                elif 'boolean' in field_type.lower() or field_type.lower() == 'tinyint(1)':
                    form_data[field] = st.checkbox(f"{field}")
                else:
                    # Text input for other types (varchar, text, etc.)
                    form_data[field] = st.text_input(f"{field}")
            
            submit_button = st.form_submit_button(label="Add Record")
            
            if submit_button:
                # Validate input (basic validation)
                valid_input = True
                missing_fields = []
                
                for field, value in form_data.items():
                    # Check if required field is empty
                    is_nullable = columns_info[columns_info['Field'] == field]['Null'].iloc[0] == 'YES'
                    if not is_nullable and (value is None or value == ''):
                        valid_input = False
                        missing_fields.append(field)
                
                if valid_input:
                    # Process datetime fields
                    for field, value in form_data.items():
                        if isinstance(value, (datetime.date, datetime.time)) and not isinstance(value, datetime.datetime):
                            if 'datetime' in columns_info[columns_info['Field'] == field]['Type'].iloc[0].lower():
                                # Convert date to datetime
                                if isinstance(value, datetime.date):
                                    form_data[field] = datetime.datetime.combine(value, datetime.time())
                                # Convert time to datetime (using today's date)
                                elif isinstance(value, datetime.time):
                                    form_data[field] = datetime.datetime.combine(datetime.date.today(), value)
                    
                    # Add record to the database
                    result = db.create_record(selected_table, form_data)
                    
                    if result > 0:
                        st.success(f"Record added successfully to {selected_table}!")
                    else:
                        st.error("Failed to add record. Please check your input.")
                else:
                    st.error(f"Please fill in all required fields: {', '.join(missing_fields)}")
    
    # Edit operation
    elif crud_operation == "Edit":
        st.subheader(f"Edit {selected_table}")
        
        # Get all records to let user select which to edit
        records = db.read_records(selected_table)
        
        if not records.empty:
            # Create a selectbox to choose a record to edit
            if primary_keys:
                # Create a display column for selection
                if len(primary_keys) == 1:
                    pk = primary_keys[0]
                    display_col = pk
                    
                    # Try to get a more descriptive column if available
                    name_cols = [col for col in records.columns if 'name' in col.lower()]
                    if name_cols:
                        records['_display_'] = records[pk].astype(str) + ' - ' + records[name_cols[0]].astype(str)
                        display_col = '_display_'
                    
                    selected_record_display = st.selectbox(
                        "Select a record to edit",
                        options=records[display_col].tolist()
                    )
                    
                    # Get the selected record ID
                    if display_col == '_display_':
                        selected_id = records.loc[records['_display_'] == selected_record_display, pk].iloc[0]
                    else:
                        selected_id = selected_record_display
                    
                    # Get the selected record
                    condition = f"{pk} = %s"
                    params = [selected_id]
                    selected_record = db.fetch_data(f"SELECT * FROM {selected_table} WHERE {condition}", params)
                    
                    if not selected_record.empty:
                        with st.form(key=f"edit_{selected_table}"):
                            # Create input fields for each column
                            form_data = {}
                            
                            for _, row in columns_info.iterrows():
                                field = row['Field']
                                field_type = row['Type']
                                current_value = selected_record.iloc[0][field]
                                
                                # Skip primary key fields (usually not editable)
                                if field in primary_keys:
                                    st.text_input(f"{field} (Primary Key - Not Editable)", value=str(current_value), disabled=True)
                                    continue
                                
                                # Create appropriate input field based on column type
                                if 'int' in field_type.lower():
                                    form_data[field] = st.number_input(f"{field}", value=float(current_value) if current_value is not None else 0, step=1)
                                elif 'decimal' in field_type.lower():
                                    form_data[field] = st.number_input(f"{field}", value=float(current_value) if current_value is not None else 0.0, step=0.01, format="%.2f")
                                elif 'datetime' in field_type.lower():
                                    default_date = current_value if current_value is not None else datetime.datetime.now()
                                    form_data[field] = st.date_input(f"{field}", default_date)
                                elif 'date' in field_type.lower():
                                    default_date = current_value if current_value is not None else datetime.date.today()
                                    form_data[field] = st.date_input(f"{field}", default_date)
                                elif 'time' in field_type.lower():
                                    default_time = current_value if current_value is not None else datetime.time(0, 0)
                                    form_data[field] = st.time_input(f"{field}", default_time)
                                elif 'boolean' in field_type.lower() or field_type.lower() == 'tinyint(1)':
                                    form_data[field] = st.checkbox(f"{field}", value=bool(current_value))
                                else:
                                    # Text input for other types (varchar, text, etc.)
                                    form_data[field] = st.text_input(f"{field}", value=str(current_value) if current_value is not None else "")
                            
                            submit_button = st.form_submit_button(label="Update Record")
                            
                            if submit_button:
                                # Validate input (basic validation)
                                valid_input = True
                                missing_fields = []
                                
                                for field, value in form_data.items():
                                    # Check if required field is empty
                                    is_nullable = columns_info[columns_info['Field'] == field]['Null'].iloc[0] == 'YES'
                                    if not is_nullable and (value is None or value == ''):
                                        valid_input = False
                                        missing_fields.append(field)
                                
                                if valid_input:
                                    # Process datetime fields
                                    for field, value in form_data.items():
                                        if isinstance(value, (datetime.date, datetime.time)) and not isinstance(value, datetime.datetime):
                                            if 'datetime' in columns_info[columns_info['Field'] == field]['Type'].iloc[0].lower():
                                                # Convert date to datetime
                                                if isinstance(value, datetime.date):
                                                    form_data[field] = datetime.datetime.combine(value, datetime.time())
                                                # Convert time to datetime (using today's date)
                                                elif isinstance(value, datetime.time):
                                                    form_data[field] = datetime.datetime.combine(datetime.date.today(), value)
                                    
                                    # Update record in the database
                                    result = db.update_record(selected_table, form_data, condition)
                                    
                                    if result > 0:
                                        st.success(f"Record updated successfully in {selected_table}!")
                                    else:
                                        st.error("Failed to update record. Please check your input.")
                                else:
                                    st.error(f"Please fill in all required fields: {', '.join(missing_fields)}")
                else:
                    st.warning(f"Editing records with composite primary keys is not supported in this version.")
            else:
                st.error(f"No primary key found for table {selected_table}. Cannot edit records.")
        else:
            st.info(f"No records found in {selected_table}")
    
    # Delete operation
    elif crud_operation == "Delete":
        st.subheader(f"Delete from {selected_table}")
        
        # Get all records to let user select which to delete
        records = db.read_records(selected_table)
        
        if not records.empty:
            # Create a selectbox to choose a record to delete
            if primary_keys:
                # Create a display column for selection
                if len(primary_keys) == 1:
                    pk = primary_keys[0]
                    display_col = pk
                    
                    # Try to get a more descriptive column if available
                    name_cols = [col for col in records.columns if 'name' in col.lower()]
                    if name_cols:
                        records['_display_'] = records[pk].astype(str) + ' - ' + records[name_cols[0]].astype(str)
                        display_col = '_display_'
                    
                    selected_record_display = st.selectbox(
                        "Select a record to delete",
                        options=records[display_col].tolist()
                    )
                    
                    # Get the selected record ID
                    if display_col == '_display_':
                        selected_id = records.loc[records['_display_'] == selected_record_display, pk].iloc[0]
                    else:
                        selected_id = selected_record_display
                    
                    # Get the selected record
                    condition = f"{pk} = %s"
                    params = [selected_id]
                    selected_record = db.fetch_data(f"SELECT * FROM {selected_table} WHERE {condition}", params)
                    
                    if not selected_record.empty:
                        st.write("Record to delete:")
                        st.dataframe(selected_record)
                        
                        # Confirm deletion
                        if st.button("Delete Record", type="primary"):
                            # Check for foreign key constraints
                            confirm_delete = True
                            
                            if confirm_delete:
                                # Delete record from the database
                                result = db.delete_record(selected_table, condition, params)
                                
                                if result > 0:
                                    st.success(f"Record deleted successfully from {selected_table}!")
                                else:
                                    st.error("Failed to delete record. This record might be referenced by other tables.")
                        
                        st.warning("⚠️ Warning: This action cannot be undone!")
                else:
                    st.warning(f"Deleting records with composite primary keys is not supported in this version.")
            else:
                st.error(f"No primary key found for table {selected_table}. Cannot delete records.")
        else:
            st.info(f"No records found in {selected_table}")
    
    # Search operation
    elif crud_operation == "Search":
        st.subheader(f"Search in {selected_table}")
        
        # Get all columns for the table
        if not columns_info.empty:
            search_column = st.selectbox("Select column to search", options=columns_info['Field'].tolist())
            search_term = st.text_input("Enter search term")
            
            if search_term:
                # Perform search
                search_results = db.search_records(selected_table, search_column, search_term)
                
                if not search_results.empty:
                    st.dataframe(search_results)
                else:
                    st.info(f"No records found matching '{search_term}' in {search_column}")

# Special views for complex operations
elif selected_table == "Order Management":
    st.header("Order Management")
    
    tab1, tab2, tab3 = st.tabs(["View Orders", "Create Order", "Order Analytics"])
    
    with tab1:
        st.subheader("All Orders")
        orders = db.get_orders_with_details()
        if not orders.empty:
            st.dataframe(orders)
        else:
            st.info("No orders found.")
    
    with tab2:
        st.subheader("Create New Order")
        
        with st.form(key="create_order"):
            # Get customers for dropdown
            customers = db.fetch_data("SELECT cust_id, CONCAT(cust_firstname, ' ', cust_lastname) as name FROM customers")
            customer_options = {row['cust_id']: row['name'] for _, row in customers.iterrows()}
            
            # Get items for dropdown
            items = db.fetch_data("SELECT item_id, item_name, item_price, item_size FROM item")
            item_options = {row['item_id']: f"{row['item_name']} ({row['item_size']}) - ${row['item_price']}" for _, row in items.iterrows()}
            
            # Get addresses for dropdown
            addresses = db.fetch_data("SELECT add_id, CONCAT(delivery_address1, ', ', delivery_city, ' ', delivery_zipcode) as address FROM address")
            address_options = {row['add_id']: row['address'] for _, row in addresses.iterrows()}
            
            # Create form fields
            customer_id = st.selectbox("Customer", options=list(customer_options.keys()), format_func=lambda x: customer_options.get(x, ""))
            item_id = st.selectbox("Item", options=list(item_options.keys()), format_func=lambda x: item_options.get(x, ""))
            quantity = st.number_input("Quantity", min_value=1, value=1)
            is_delivery = st.checkbox("Delivery")
            address_id = st.selectbox("Delivery Address", options=list(address_options.keys()), format_func=lambda x: address_options.get(x, ""))
            
            # Get the price of the selected item
            item_price = 0
            if item_id:
                selected_item = items[items['item_id'] == item_id]
                if not selected_item.empty:
                    item_price = selected_item.iloc[0]['item_price']
            
            submit_button = st.form_submit_button(label="Create Order")
            
            if submit_button:
                # Generate a new order ID
                last_order = db.fetch_data("SELECT order_id FROM orders ORDER BY row_id DESC LIMIT 1")
                if not last_order.empty:
                    last_id = last_order.iloc[0]['order_id']
                    # Extract the numeric part and increment
                    numeric_part = int(last_id.replace('ORD', '')) + 1
                    new_order_id = f"ORD{numeric_part:04d}"
                else:
                    new_order_id = "ORD0001"
                
                # Get the next row_id
                last_row = db.fetch_data("SELECT MAX(row_id) as max_id FROM orders")
                new_row_id = 1
                if not last_row.empty and last_row.iloc[0]['max_id'] is not None:
                    new_row_id = last_row.iloc[0]['max_id'] + 1
                
                # Create new order
                order_data = {
                    'row_id': new_row_id,
                    'order_id': new_order_id,
                    'created_at': datetime.datetime.now(),
                    'item_id': item_id,
                    'item_price': item_price,
                    'quantity': quantity,
                    'cust_id': customer_id,
                    'delivery': is_delivery,
                    'add_id': address_id
                }
                
                result = db.create_record('orders', order_data)
                
                if result > 0:
                    st.success(f"Order {new_order_id} created successfully!")
                else:
                    st.error("Failed to create order. Please check your input.")
    
    with tab3:
        st.subheader("Order Analytics")
        
        # Get order statistics
        daily_orders = db.fetch_data("""
            SELECT DATE(created_at) as date, COUNT(*) as order_count, SUM(item_price * quantity) as revenue
            FROM orders
            GROUP BY DATE(created_at)
            ORDER BY date DESC
            LIMIT 10
        """)
        
        if not daily_orders.empty:
            st.line_chart(daily_orders.set_index('date')[['order_count']])
            st.line_chart(daily_orders.set_index('date')[['revenue']])
        
        # Top selling items
        top_items = db.fetch_data("""
            SELECT i.item_name, SUM(o.quantity) as total_quantity, SUM(o.item_price * o.quantity) as total_revenue
            FROM orders o
            JOIN item i ON o.item_id = i.item_id
            GROUP BY i.item_name
            ORDER BY total_quantity DESC
            LIMIT 5
        """)
        
        if not top_items.empty:
            st.subheader("Top Selling Items")
            st.bar_chart(top_items.set_index('item_name')[['total_quantity']])

elif selected_table == "Inventory Management":
    st.header("Inventory Management")
    
    tab1, tab2 = st.tabs(["View Inventory", "Update Inventory"])
    
    with tab1:
        st.subheader("Current Inventory")
        inventory = db.get_inventory_with_items()
        if not inventory.empty:
            st.dataframe(inventory)
        else:
            st.info("No inventory items found.")
        
        # Low stock alert
        low_stock = inventory[inventory['quantity'] < 10] if not inventory.empty else pd.DataFrame()
        if not low_stock.empty:
            st.warning("Low Stock Items (quantity < 10):")
            st.dataframe(low_stock)
    
    with tab2:
        st.subheader("Update Inventory")
        
        # Get inventory items for dropdown
        inventory = db.get_inventory_with_items()
        if not inventory.empty:
            inv_options = {row['inv_id']: f"{row['item_name']} (Current stock: {row['quantity']})" for _, row in inventory.iterrows()}
            
            with st.form(key="update_inventory"):
                inv_id = st.selectbox("Select Item", options=list(inv_options.keys()), format_func=lambda x: inv_options.get(x, ""))
                quantity = st.number_input("New Quantity", min_value=0, value=10)
                
                submit_button = st.form_submit_button(label="Update Inventory")
                
                if submit_button:
                    # Update inventory
                    result = db.update_record('inventory', {'quantity': quantity}, f"inv_id = {inv_id}")
                    
                    if result > 0:
                        st.success("Inventory updated successfully!")
                    else:
                        st.error("Failed to update inventory. Please try again.")
        else:
            st.info("No inventory items found.")

elif selected_table == "Staff Schedule":
    st.header("Staff Schedule")
    
    tab1, tab2 = st.tabs(["View Schedule", "Create Rotation"])
    
    with tab1:
        st.subheader("Staff Schedule")
        
        # Get staff for filtering
        staff = db.fetch_data("SELECT staff_id, CONCAT(first_name, ' ', last_name) as name FROM staff")
        staff_options = {row['staff_id']: row['name'] for _, row in staff.iterrows()}
        staff_options[''] = "All Staff"
        
        selected_staff = st.selectbox("Filter by Staff", options=list(staff_options.keys()), format_func=lambda x: staff_options.get(x, ""))
        
        schedule = db.get_staff_schedule(selected_staff if selected_staff else None)
        if not schedule.empty:
            st.dataframe(schedule)
        else:
            st.info("No schedule found for the selected criteria.")
    
    with tab2:
        st.subheader("Create New Rotation")
        
        with st.form(key="create_rotation"):
            # Get staff for dropdown
            staff = db.fetch_data("SELECT staff_id, CONCAT(first_name, ' ', last_name) as name FROM staff")
            staff_options = {row['staff_id']: row['name'] for _, row in staff.iterrows()}
            
            # Get shifts for dropdown
            shifts = db.fetch_data("SELECT shift_id, CONCAT(day_of_week, ' (', start_time, ' - ', end_time, ')') as shift_desc FROM shift")
            shift_options = {row['shift_id']: row['shift_desc'] for _, row in shifts.iterrows()}
            
            # Create form fields
            # Get the next row_id
            last_row = db.fetch_data("SELECT MAX(row_id) as max_id FROM rotation")
            new_row_id = 1
            if not last_row.empty and last_row.iloc[0]['max_id'] is not None:
                new_row_id = last_row.iloc[0]['max_id'] + 1
                
            # Generate rotation ID
            last_rota = db.fetch_data("SELECT rota_id FROM rotation ORDER BY row_id DESC LIMIT 1")
            if not last_rota.empty:
                last_id = last_rota.iloc[0]['rota_id']
                # Extract the numeric part and increment
                numeric_part = int(last_id.replace('ROT', '')) + 1
                new_rota_id = f"ROT{numeric_part:04d}"
            else:
                new_rota_id = "ROT0001"
            
            staff_id = st.selectbox("Staff", options=list(staff_options.keys()), format_func=lambda x: staff_options.get(x, ""))
            shift_id = st.selectbox("Shift", options=list(shift_options.keys()), format_func=lambda x: shift_options.get(x, ""))
            date = st.date_input("Date")
            
            submit_button = st.form_submit_button(label="Create Rotation")
            
            if submit_button:
                # Create new rotation
                rotation_data = {
                    'row_id': new_row_id,
                    'rota_id': new_rota_id,
                    'date': date,
                    'shift_id': shift_id,
                    'staff_id': staff_id
                }
                
                result = db.create_record('rotation', rotation_data)
                
                if result > 0:
                    st.success(f"Rotation {new_rota_id} created successfully!")
                else:
                    st.error("Failed to create rotation. Please check your input.")

elif selected_table == "Recipe Management":
    st.header("Recipe Management")
    
    tab1, tab2 = st.tabs(["View Recipes", "Create Recipe"])
    
    with tab1:
        st.subheader("Recipes")
        
        # Get items for recipes
        items = db.fetch_data("SELECT sku, item_name FROM item")
        recipe_options = {row['sku']: row['item_name'] for _, row in items.iterrows()}
        recipe_options[''] = "All Recipes"
        
        selected_recipe = st.selectbox("Select Recipe", options=list(recipe_options.keys()), format_func=lambda x: recipe_options.get(x, ""))
        
        recipes = db.get_recipe_with_ingredients(selected_recipe if selected_recipe else None)
        if not recipes.empty:
            st.dataframe(recipes)
        else:
            st.info("No recipes found for the selected criteria.")
    
    with tab2:
        st.subheader("Create New Recipe Item")
        
        with st.form(key="create_recipe"):
            # Get items for dropdown
            items = db.fetch_data("SELECT sku, item_name FROM item")
            item_options = {row['sku']: row['item_name'] for _, row in items.iterrows()}
            
            # Get ingredients for dropdown
            ingredients = db.fetch_data("SELECT ing_id, ing_name FROM ingredient")
            ing_options = {row['ing_id']: row['ing_name'] for _, row in ingredients.iterrows()}
            
            # Create form fields
            # Get the next row_id
            last_row = db.fetch_data("SELECT MAX(row_id) as max_id FROM recipe")
            new_row_id = 1
            if not last_row.empty and last_row.iloc[0]['max_id'] is not None:
                new_row_id = last_row.iloc[0]['max_id'] + 1
            
            recipe_id = st.selectbox("Item SKU", options=list(item_options.keys()), format_func=lambda x: item_options.get(x, ""))
            ing_id = st.selectbox("Ingredient", options=list(ing_options.keys()), format_func=lambda x: ing_options.get(x, ""))
            quantity = st.number_input("Quantity", min_value=1, value=1)
            
            submit_button = st.form_submit_button(label="Add to Recipe")
            
            if submit_button:
                # Create new recipe item
                recipe_data = {
                    'row_id': new_row_id,
                    'recipe_id': recipe_id,
                    'ing_id': ing_id,
                    'quantity': quantity
                }
                
                result = db.create_record('recipe', recipe_data)
                
                if result > 0:
                    st.success(f"Recipe item added successfully!")
                else:
                    st.error("Failed to add recipe item. Please check your input.")

# Footer
st.markdown("---")
st.markdown("© 2025 Ice Cream Shop Management System")