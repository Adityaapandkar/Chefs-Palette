import streamlit as st
from chat_asst import ChatAssistant
from recipe_search import RecipeSearch

# Set page configuration
st.set_page_config(page_icon="🍳", layout="wide", page_title="Groq Cooking Assistant")

# Display an icon
def icon(emoji: str):
    """Displays an emoji as a Notion-style page icon."""
    st.write(
        f'<span style="font-size: 78px; line-height: 1">{emoji}</span>',
        unsafe_allow_html=True,
    )

icon("👩‍🍳")

st.subheader("Groq Cooking Assistant", anchor=False)

# Initialize ChatAssistant
chat_assistant = ChatAssistant(api_key=st.secrets["GROQ_API_KEY"])

# Define model details
models = {
    "gemma-7b-it": {"name": "Gemma-7b-it", "tokens": 8192, "developer": "Google"},
    "llama2-70b-4096": {"name": "LLaMA2-70b-chat", "tokens": 4096, "developer": "Meta"},
    "llama3-70b-8192": {"name": "LLaMA3-70b-8192", "tokens": 8192, "developer": "Meta"},
    "llama3-8b-8192": {"name": "LLaMA3-8b-8192", "tokens": 8192, "developer": "Meta"},
    "mixtral-8x7b-32768": {"name": "Mixtral-8x7b-Instruct-v0.1", "tokens": 32768, "developer": "Mistral"},
}

# Model selection and max_tokens slider
model_option, max_tokens = chat_assistant.select_model(models)

# Initialize RecipeSearch
recipe_search = RecipeSearch(api_key=st.secrets["SPOONACULAR_API_KEY"])

# Initialize selected_recipe in session state
if "selected_recipe" not in st.session_state:
    st.session_state.selected_recipe = None

# Sidebar for Recipe Search and Filtering
st.sidebar.header("🔍 Recipe Search and Filtering")

# Ingredient-Based Search
ingredients = st.sidebar.text_input(
    "Enter ingredients you have (comma separated):",
    placeholder="e.g., chicken, garlic, tomatoes"
)

# Cuisine Filters
cuisines = st.sidebar.multiselect(
    "Select preferred cuisines:",
    options=[
        "Italian", "Chinese", "Mexican", "Indian", "French",
        "Japanese", "Mediterranean", "Thai", "American", "Spanish"
    ]
)

# Dietary Restrictions
dietary_restrictions = st.sidebar.multiselect(
    "Select dietary restrictions:",
    options=[
        "Vegetarian", "Vegan", "Gluten Free", "Keto",
        "Paleo", "Dairy Free", "Pescatarian", "Halal", "Kosher"
    ]
)

# Search Button
search = st.sidebar.button("Search Recipes")

# Handle Recipe Search
if search:
    if not ingredients and not cuisines and not dietary_restrictions:
        st.sidebar.warning("Please enter at least one search criterion.")
    else:
        with st.spinner("Searching for recipes..."):
            recipes = recipe_search.fetch_recipes(
                ingredients=ingredients,
                cuisines=cuisines,
                dietary_restrictions=dietary_restrictions,
                number=10  # Adjust the number as needed
            )
        
        recipe_search.display_search_results(recipes)

# Display Selected Recipe Details
if st.session_state.selected_recipe:
    selected = st.session_state.selected_recipe
    st.subheader("📝 Selected Recipe Details")
    st.markdown(f"### {selected['title']}")
    st.image(selected.get("image"), use_column_width=True)
    st.markdown(f"*Cuisine:* {', '.join(selected.get('cuisines', []))}")
    st.markdown(f"*Diet:* {', '.join(selected.get('diets', []))}")
    st.markdown(f"*Ready in:* {selected.get('readyInMinutes')} minutes")
    st.markdown(f"[View Full Recipe]({selected.get('sourceUrl')})")
    
    # Button to interact with chatbot about the recipe
    if st.button("Ask about this recipe"):
        user_prompt = f"I've selected the recipe '{selected['title']}'. Can you help me with the next steps?"
        chat_assistant.handle_user_input(prompt=user_prompt, models=models, max_tokens=max_tokens)

# Display chat messages from history on app rerun
chat_assistant.display_chat_history()

# Chat input for user prompts
prompt = st.chat_input("Ask me anything about cooking...")

if prompt:
    chat_assistant.handle_user_input(prompt=prompt, models=models, max_tokens=max_tokens)
