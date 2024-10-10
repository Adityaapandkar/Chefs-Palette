from typing import Generator, List, Dict
from groq import Groq
import streamlit as st

class ChatAssistant:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        if "messages" not in st.session_state:
            st.session_state.messages = [
                {
                    "role": "system",
                    "content": (
                        "You are a knowledgeable and friendly cooking assistant. "
                        "Your tasks include providing detailed and easy-to-follow recipes, offering cooking tips and techniques, suggesting ingredient substitutions, "
                        "helping with meal planning, and answering any culinary-related questions. "
                        "Ensure that your responses are clear, concise, and tailored to the user's skill level and dietary preferences. "
                        "Encourage creativity in the kitchen and promote healthy cooking practices when appropriate."
                    )
                }
            ]
        if "selected_model" not in st.session_state:
            st.session_state.selected_model = None

    def select_model(self, models: Dict[str, Dict], default_model: str = "mixtral-8x7b-32768") -> str:
        """
        Allows user to select a model and manages session state.
        """
        col1, col2 = st.columns(2)

        with col1:
            model_option = st.selectbox(
                "Choose a model:",
                options=list(models.keys()),
                format_func=lambda x: models[x]["name"],
                index=list(models.keys()).index(default_model)
            )

        # Detect model change and clear chat history if model has changed
        if st.session_state.selected_model != model_option:
            st.session_state.messages = st.session_state.messages[:1]  # Keep only the system prompt
            st.session_state.selected_model = model_option

        max_tokens_range = models[model_option]["tokens"]

        with col2:
            # Adjust max_tokens slider dynamically based on the selected model
            max_tokens = st.slider(
                "Max Tokens:",
                min_value=512,  # Minimum value to allow some flexibility
                max_value=max_tokens_range,
                # Default value or max allowed if less
                value=min(32768, max_tokens_range),
                step=512,
                help=f"Adjust the maximum number of tokens (words) for the model's response. Max for selected model: {max_tokens_range}"
            )
        return model_option, max_tokens

    def display_chat_history(self):
        """
        Displays the chat history in the Streamlit app.
        """
        for message in st.session_state.messages:
            if message["role"] == "system":
                continue  # Optionally hide the system prompt
            avatar = '🤖' if message["role"] == "assistant" else '👨‍🍳'
            with st.chat_message(message["role"], avatar=avatar):
                st.markdown(message["content"])

    def generate_chat_responses(self, chat_completion) -> Generator[str, None, None]:
        """Yield chat response content from the Groq API response."""
        for chunk in chat_completion:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def handle_user_input(self, prompt: str, models: Dict[str, Dict], max_tokens: int):
        """
        Handles user input and generates assistant responses.
        """
        st.session_state.messages.append({"role": "user", "content": prompt})

        with st.chat_message("user", avatar='👨‍🍳'):
            st.markdown(prompt)

        # Fetch response from Groq API
        try:
            chat_completion = self.client.chat.completions.create(
                model=st.session_state.selected_model,
                messages=[
                    {
                        "role": m["role"],
                        "content": m["content"]
                    }
                    for m in st.session_state.messages
                ],
                max_tokens=max_tokens,
                stream=True
            )

            # Use the generator function with st.write_stream
            with st.chat_message("assistant", avatar="🤖"):
                chat_responses_generator = self.generate_chat_responses(chat_completion)
                full_response = st.write_stream(chat_responses_generator)
        except Exception as e:
            st.error(f"Error: {e}", icon="🚨")
            full_response = None

        # Append the full response to session_state.messages
        if isinstance(full_response, str):
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response})
        elif full_response:
            # Handle the case where full_response is not a string
            combined_response = "\n".join(str(item) for item in full_response)
            st.session_state.messages.append(
                {"role": "assistant", "content": combined_response})

