import streamlit as st
from pypdf import PdfReader
from PIL import Image
import io
import base64
import google.generativeai as genai
from google.generativeai.types import GenerationConfig
import os

# --- Page Configuration ---
# Set the layout to wide and give the app a title.
st.set_page_config(layout="wide", page_title="Legal Document Analyzer")

# --- CSS for Sidebar Width ---
# This injects custom CSS to control the width of the sidebar.
st.markdown(
    """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        width: 400px;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        width: 400px;
        margin-left: -400px;
    }
    .stSelectbox > div > div {
        max-width: 100%;
        overflow: hidden;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Sidebar for Configuration ---
with st.sidebar:
    st.header("Configuration")
    user_key = st.text_input(
        "Gemini API Key (optional)",
        type="password",
        help="Enter your own key if the host's is down or limited."
    )
    selected_model = st.selectbox(
        "Choose AI Model",
        options=["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash","gemini-2.5-flash-lite"]
    )

# --- API Key Configuration ---
# Fallback to secrets (Streamlit) or env var if no user key
api_key = user_key if user_key else st.secrets.get("GEMINI_API_KEY") or os.environ.get("GEMINI_API_KEY")
if not api_key:
    st.error("No Gemini API key found. Please provide one in the sidebar or set GEMINI_API_KEY in secrets/env.")
    st.stop()

# Configure Gemini
genai.configure(api_key=api_key)

# App title
st.title("Legal Document Analyzer: AI-Powered Legal Document Assistant")

# --- Session State Initialization ---
# Initialize session state for document text and chat history if they don't exist.
if "doc_text" not in st.session_state:
    st.session_state.doc_text = ""
if "messages" not in st.session_state:
    st.session_state.messages = []


# --- Generation Functions ---

def generate_completion(prompt_content, model, max_tokens=8000, temperature=0.3):
    """Generate a completion using the selected model."""
    if model.startswith("gemini"):
        # **UPDATED GEMINI API USAGE**
        gen_config = GenerationConfig(max_output_tokens=max_tokens, temperature=temperature)
        gemini_model = genai.GenerativeModel(
            model_name=model,
            generation_config=gen_config
        )
        response = gemini_model.generate_content(
            contents=prompt_content
        )
        return response.text
    else:
        raise ValueError(f"Unsupported model: {model}")

def generate_chat_response(full_messages, model, max_tokens=8000, temperature=0.5):
    """Generate a chat response using the selected model."""
    if model.startswith("gemini"):
        # **UPDATED GEMINI API USAGE**
        # Extract system prompt and format message history for Gemini
        system_prompt = ""
        gemini_history = []
        
        if full_messages and full_messages[0]['role'] == 'system':
            system_prompt = full_messages[0]['content']
            messages_for_history = full_messages[1:]
        else:
            messages_for_history = full_messages

        for msg in messages_for_history:
            # Map 'assistant' role to 'model' for the Gemini API
            role = "model" if msg["role"] == "assistant" else "user"
            gemini_history.append({'role': role, 'parts': [msg['content']]})

        gen_config = GenerationConfig(max_output_tokens=max_tokens, temperature=temperature)
        gemini_model = genai.GenerativeModel(
            model_name=model,
            system_instruction=system_prompt,
            generation_config=gen_config
        )
        
        response = gemini_model.generate_content(gemini_history)
        return response.text
    else:
        raise ValueError(f"Unsupported model: {model}")

def auto_scroll():
    """Auto-scroll to the bottom of the chat."""
    st.components.v1.html(
        """
        <script>
        const messagesContainer = window.parent.document.querySelector('.main .block-container');
        if (messagesContainer) {
            messagesContainer.scrollTop = messagesContainer.scrollHeight;
        }
        </script>
        """,
        height=0
    )


# --- App Layout ---
# Layout: Two columns for the uploader and the chat interface
left_col, right_col = st.columns([2, 3])

with left_col:
    st.header("Document Uploader")
    uploaded_file = st.file_uploader(
        "Upload a legal document (PDF or Image)",
        type=["pdf", "png", "jpg", "jpeg"],
        help="Upload a PDF or image file to be summarized and analyzed."
    )
    
    if uploaded_file is not None:
        file_bytes = uploaded_file.getvalue()
        base64_pdf = None  # For PDF handling
        base64_image = None  # For image handling
        
        # Process and display based on file type
        if uploaded_file.type == "application/pdf":
            # Display PDF preview using st.pdf
            st.pdf(uploaded_file, height=600)
            
            # Base64 for Gemini multimodal input
            base64_pdf = base64.b64encode(file_bytes).decode('utf-8')
            
            # Extract text (for chat context)
            reader = PdfReader(io.BytesIO(file_bytes))
            text = "".join(page.extract_text() + "\n" for page in reader.pages)
            st.session_state.doc_text = text.strip()
            st.success("PDF text extracted successfully!")
        else:  # Image file
            image = Image.open(io.BytesIO(file_bytes))
            st.image(image, caption="Uploaded Image Preview", use_container_width=True)
            
            # Base64 for Gemini multimodal input
            base64_image = base64.b64encode(file_bytes).decode('utf-8')
            st.session_state.doc_text = "Image document uploaded"  # Placeholder for chat check
            st.success("Image uploaded successfully!")
        
        # Display a truncated preview of the extracted text (for PDFs only)
        if st.session_state.doc_text != "Image document uploaded":
            with st.expander("View Extracted Text (first 2000 tokens)"):
                st.text_area("", st.session_state.doc_text[:2000], height=200, disabled=True)
        
        # Button to generate the summary
        if st.button("Generate Summary", type="primary", use_container_width=True):
            if uploaded_file is None:
                st.warning("Please upload a valid file.")
            else:
                with st.spinner("Generating summary... This may take a moment."):
                    if uploaded_file.type == "application/pdf" and base64_pdf:
                        # Pass PDF inline to Gemini (multimodal)
                        prompt_content = [
                            "You are a legal expert. Provide a concise, accurate summary of the following document. Highlight key clauses, parties involved, main obligations, and potential risks.",
                            {
                                "mime_type": "application/pdf",
                                "data": base64_pdf
                            }
                        ]
                    else:
                        # Pass image inline to Gemini (multimodal)
                        mime_type = "image/png" if uploaded_file.type == "image/png" else "image/jpeg"
                        prompt_content = [
                            "You are a legal expert. Provide a concise, accurate summary of the following image document. Highlight key clauses, parties involved, main obligations, and potential risks.",
                            {
                                "mime_type": mime_type,
                                "data": base64_image
                            }
                        ]
                    
                    summary = generate_completion(prompt_content, selected_model)
                    
                    if summary:
                        # Clear previous chat and add the new summary as the first message
                        st.session_state.messages = [{"role": "assistant", "content": f"**Document Summary:**\n{summary}"}]
                        st.rerun()  # Refresh the app to display the summary in the chat

with right_col:
    st.header("Chat Interface")
    
    # Display chat messages (renders new ones at bottom naturally in Streamlit)
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input box (always at bottom)
    if prompt := st.chat_input("Ask a follow-up question about the document..."):
        if not st.session_state.doc_text:
            st.warning("Please upload and summarize a document first.")
        else:
            # Add user's message to history and display it
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Generate and display the AI's response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    system_prompt = (
                        "You are a helpful legal AI assistant. The first message you received was a summary of a legal document. "
                        "Answer the user's follow-up questions"
                        
                    )
                    
                    # Prepend system prompt for the API call
                    messages_for_api = [{"role": "system", "content": system_prompt}] + st.session_state.messages
                    
                    ai_response = generate_chat_response(messages_for_api, selected_model)
                    
                    if ai_response:
                        st.markdown(ai_response)
                        # Add AI's response to the session state
                        st.session_state.messages.append({"role": "assistant", "content": ai_response})
    
    # Auto-scroll to bottom after new messages
    auto_scroll()

# --- Footer ---
st.markdown("---")
st.markdown("*Legal_ease is an AI assistant for informational purposes only. Always consult a qualified attorney for professional legal advice.*")