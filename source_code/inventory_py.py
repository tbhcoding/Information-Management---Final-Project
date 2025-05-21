import streamlit as st
import pandas as pd
from database import Database

def show_inventory_management(db):
    """Display the inventory management section"""
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