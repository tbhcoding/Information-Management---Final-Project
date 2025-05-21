import streamlit as st
import datetime
from database import Database

def show_staff_schedule(db):
    """Display the staff schedule section"""
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