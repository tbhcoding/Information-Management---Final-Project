import streamlit as st
from database import Database

def show_recipe_management(db):
    """Display the recipe management section"""
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