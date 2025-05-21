import streamlit as st
import pandas as pd
from database import Database
import datetime

def show_dashboard(db):
    """Display the dashboard with key statistics and quick links"""
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