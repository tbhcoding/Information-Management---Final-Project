import streamlit as st
import pandas as pd
import datetime
from database import Database

def show_table_operations(db, selected_table, crud_operation):
    """Display CRUD operations for a specific table"""
    st.header(f"{selected_table.capitalize()} Management")
    
    # Get table columns and primary key
    columns_info = db.get_table_columns(selected_table)
    primary_keys = db.get_primary_key(selected_table)
    
    # View operation
    if crud_operation == "View":
        view_table(db, selected_table)
    
    # Add operation
    elif crud_operation == "Add":
        add_record(db, selected_table, columns_info)
    
    # Edit operation
    elif crud_operation == "Edit":
        edit_record(db, selected_table, columns_info, primary_keys)
    
    # Delete operation
    elif crud_operation == "Delete":
        delete_record(db, selected_table, primary_keys)
    
    # Search operation
    elif crud_operation == "Search":
        search_records(db, selected_table, columns_info)

def view_table(db, selected_table):
    """View all records in a table"""
    st.subheader(f"View {selected_table}")
    
    # Show the data
    data = db.read_records(selected_table)
    if not data.empty:
        st.dataframe(data)
    else:
        st.info(f"No records found in {selected_table}")

def add_record(db, selected_table, columns_info):
    """Add a new record to a table"""
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

def edit_record(db, selected_table, columns_info, primary_keys):
    """Edit an existing record in a table"""
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

def delete_record(db, selected_table, primary_keys):
    """Delete a record from a table"""
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

def search_records(db, selected_table, columns_info):
    """Search for records in a table"""
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