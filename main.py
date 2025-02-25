import streamlit as st
import pandas as pd
from utils import initialize_data, load_inventory, save_inventory, validate_input, update_stock

def main():
    st.set_page_config(
        page_title="Inventory Management System",
        layout="wide"
    )
    
    initialize_data()
    
    st.title("📦 Inventory Management System")
    
    # Navigation
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Overview", 
        "📥 Stock In", 
        "📤 Stock Out",
        "📊 Reports"
    ])
    
    df = load_inventory()
    
    with tab1:
        st.header("Current Inventory")
        
        # Display current inventory with color coding for reorder levels
        if not df.empty:
            styled_df = df.style.apply(lambda x: [
                'background-color: #ffcccb' if x['quantity'] <= x['reorder_level'] 
                else 'background-color: #90EE90' for i in range(len(x))
            ], axis=1)
            st.dataframe(styled_df, use_container_width=True)
            
            # Show items that need reordering
            reorder_items = df[df['quantity'] <= df['reorder_level']]
            if not reorder_items.empty:
                st.warning("⚠️ Items that need reordering:")
                st.dataframe(reorder_items[['item_code', 'item_name', 'quantity', 'reorder_level']])
        else:
            st.info("No items in inventory yet")
    
    with tab2:
        st.header("Stock In")
        with st.form("stock_in_form"):
            col1, col2 = st.columns(2)
            with col1:
                item_code = st.text_input("Item Code")
                item_name = st.text_input("Item Name")
            with col2:
                quantity = st.number_input("Quantity", min_value=1, step=1)
                reorder_level = st.number_input("Reorder Level", min_value=1, step=1)
            
            submitted = st.form_submit_button("Add Stock")
            if submitted:
                valid, message = validate_input(item_code, item_name, quantity, reorder_level)
                if valid:
                    df, success, message = update_stock(
                        df, item_code, item_name, quantity, reorder_level, "in"
                    )
                    if success:
                        save_inventory(df)
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.error(message)
    
    with tab3:
        st.header("Stock Out")
        with st.form("stock_out_form"):
            item_code = st.text_input("Item Code")
            quantity = st.number_input("Quantity to Remove", min_value=1, step=1)
            
            submitted = st.form_submit_button("Remove Stock")
            if submitted:
                if item_code and quantity:
                    df, success, message = update_stock(
                        df, item_code, "", quantity, 0, "out"
                    )
                    if success:
                        save_inventory(df)
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.error("Please fill in all fields")
    
    with tab4:
        st.header("Inventory Reports")
        
        # Summary Statistics
        if not df.empty:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Items", len(df))
            with col2:
                st.metric("Total Quantity", df['quantity'].sum())
            with col3:
                st.metric("Items Below Reorder Level", 
                         len(df[df['quantity'] <= df['reorder_level']]))
            
            # Last Updated Items
            st.subheader("Recently Updated Items")
            df['last_updated'] = pd.to_datetime(df['last_updated'])
            recent_updates = df.sort_values('last_updated', ascending=False).head(5)
            st.dataframe(recent_updates, use_container_width=True)
            
            # Download Report
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Download Full Inventory Report",
                csv,
                "inventory_report.csv",
                "text/csv",
                key='download-csv'
            )
        else:
            st.info("No data available for reporting")

if __name__ == "__main__":
    main()
