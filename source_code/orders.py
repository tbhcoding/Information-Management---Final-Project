import streamlit as st
import pandas as pd
import datetime
from database import Database

def show_order_management(db):
    """Display the order management section"""
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