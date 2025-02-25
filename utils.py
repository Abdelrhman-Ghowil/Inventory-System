import pandas as pd
from datetime import datetime
import streamlit as st
import os

def initialize_data():
    """Initialize the inventory data file if it doesn't exist"""
    if not os.path.exists('data'):
        os.makedirs('data')

    if not os.path.exists('data/inventory.csv'):
        df = pd.DataFrame(columns=[
            'item_code', 'item_name', 'quantity', 
            'reorder_level', 'last_updated'
        ])
        df.to_csv('data/inventory.csv', index=False)

def load_inventory():
    """Load the inventory data from CSV"""
    df = pd.read_csv('data/inventory.csv')
    # Convert item_code to string to ensure consistent comparison
    df['item_code'] = df['item_code'].astype(str)
    return df

def save_inventory(df):
    """Save the inventory data to CSV"""
    df.to_csv('data/inventory.csv', index=False)

def validate_input(item_code, item_name, quantity, reorder_level):
    """Validate input data"""
    if not item_code or not item_name:
        return False, "Item code and name are required"

    try:
        quantity = int(quantity)
        reorder_level = int(reorder_level)
        if quantity < 0 or reorder_level < 0:
            return False, "Quantity and reorder level must be positive numbers"
    except ValueError:
        return False, "Quantity and reorder level must be valid numbers"

    return True, ""

def update_stock(df, item_code, item_name, quantity, reorder_level, operation):
    """Update stock levels"""
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    # Convert item_code to string for consistent comparison
    item_code = str(item_code)

    if operation == "in":
        if item_code in df['item_code'].values:
            df.loc[df['item_code'] == item_code, 'quantity'] += quantity
            df.loc[df['item_code'] == item_code, 'last_updated'] = now
        else:
            new_row = pd.DataFrame({
                'item_code': [item_code],
                'item_name': [item_name],
                'quantity': [quantity],
                'reorder_level': [reorder_level],
                'last_updated': [now]
            })
            df = pd.concat([df, new_row], ignore_index=True)
    elif operation == "out":
        if item_code not in df['item_code'].values:
            return df, False, "Item not found in inventory"

        current_quantity = df.loc[df['item_code'] == item_code, 'quantity'].iloc[0]
        if current_quantity < quantity:
            return df, False, f"Insufficient stock (available: {current_quantity})"

        df.loc[df['item_code'] == item_code, 'quantity'] -= quantity
        df.loc[df['item_code'] == item_code, 'last_updated'] = now

    return df, True, "Operation successful"
