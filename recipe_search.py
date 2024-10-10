import requests
import streamlit as st
from typing import List, Dict

class RecipeSearch:
    def _init_(self, api_key: str):
        self.api_key = api_key

    def fetch_recipes(self, ingredients: str, cuisines: List[str], dietary_restrictions: List[str], number: int = 10) -> List[Dict]:
        """
        Fetch recipes from Spoonacular based on ingredients, cuisines, and dietary restrictions.

        Args:
            ingredients (str): Comma-separated ingredients.
            cuisines (list): List of selected cuisines.
            dietary_restrictions (list): List of dietary restrictions.
            number (int): Number of recipes to fetch.

        Returns:
            list: List of recipes.
        """
        url = "https://api.spoonacular.com/recipes/complexSearch"
        params = {
            "includeIngredients": ingredients,
            "cuisine": ",".join(cuisines) if cuisines else None,
            "diet": ",".join([diet.lower() for diet in dietary_restrictions]) if dietary_restrictions else None,
            "number": number,
            "addRecipeInformation": True,
            "fillIngredients": True,
            "apiKey": self.api_key
        }
        response = requests.get(url, params=params)
        if response.status_code == 200:
            return response.json().get("results", [])
        else:
            st.error(f"Error fetching recipes: {response.status_code}")
            return []

    def display_search_results(self, recipes: List[Dict]):
        """
        Displays the list of fetched recipes in the Streamlit app.

        Args:
            recipes (list): List of recipe dictionaries.
        """
        if recipes:
            st.sidebar.success(f"Found {len(recipes)} recipes!")
            st.subheader("🔍 Search Results")
            for recipe in recipes:
                st.markdown(f"### {recipe['title']}")
                st.image(recipe.get("image"), use_column_width=True)
                st.markdown(f"*Cuisine:* {', '.join(recipe.get('cuisines', []))}")
                st.markdown(f"*Diet:* {', '.join(recipe.get('diets', []))}")
                st.markdown(f"*Ready in:* {recipe.get('readyInMinutes')} minutes")
                st.markdown(f"[View Recipe]({recipe.get('sourceUrl')})")
                
                if st.button(f"Select '{recipe['title']}'", key=recipe['id']):
                    st.session_state.selected_recipe = recipe
                    st.success(f"Selected '{recipe['title']}' for further details.")
                
                st.markdown("---")
        else:
            st.sidebar.warning("No recipes found matching your criteria.")
