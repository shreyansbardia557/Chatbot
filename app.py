# main_app.py

import streamlit as st
import openai
import os
from dotenv import load_dotenv
from helper import upload_file_to_blob, list_blob_files, read_blob_data, tanslator,calculate_cost
from streamlit.logger import get_logger
from PIL import Image

logger = get_logger(__name__)

# Configure OpenAI API
load_dotenv('.env')
openai.api_type = os.getenv('api_type')
openai.api_base = os.getenv('api_base')
openai.api_version = os.getenv('api_version')
openai.api_key = os.getenv('api_key')

# Azure Blob Storage configuration
STORAGEACCOUNTURL = os.getenv('STORAGEACCOUNTURL')
STORAGEACCOUNTKEY = os.getenv('STORAGEACCOUNTKEY')
CONTAINERNAME = os.getenv('CONTAINERNAME')

#Translator config
key = os.getenv('key')
endpoint = os.getenv('endpoint')
location = os.getenv('location')
path = '/translate'

# List of target languages for translation
target_languages = ["fr", "hi", "es", "de"]

# Define the Streamlit app
def main():
    st.set_page_config(page_title="HSBC WittyFeed")
    st.title("HSBC WittyFeed🤓")
    st.text("Welcome! Interact with the Data World 📂")
    #image = Image.open('C:\\Users\\acer\\OneDrive\\Desktop\\HSBC-Symbol.jpeg')

    st.image("https://1000logos.net/wp-content/uploads/2017/02/HSBC-Logo.png", width=300)

    # Sidebar navigation
    page = st.sidebar.selectbox("Select Page", ["Upload Data", "Chat","Costing"], index=1)

    if page == "Chat":
        chat_page()
        
    elif page == "Upload Data":
        upload_page()
    elif page == "Costing":
        costing_page()




# Costing page
def costing_page():
    st.subheader("Cost Estimation 💲")

    # Get the latest response from the session state
    if 'latest_response' in st.session_state:
        latest_response = st.session_state['latest_response']
        cost, total_tokens, input_cost, pt, generative_cost, ct = calculate_cost(latest_response)
        st.write(f"Estimated cost: ${cost:.6f}")
        st.write(f"Total Tokens: {total_tokens}")
        st.write(f"input prompt cost: {input_cost}")
        st.write(f"Prompt Tokens: {pt}")
        st.write(f"Completion cost: {generative_cost}")
        st.write(f"Completion Tokens: {ct}")
# Upload data to Azure Blob Storage
def upload_page():
   
    st.subheader("Upload Files to Storage 📤")

    # Upload multiple files to Azure Blob Storage
    files = st.file_uploader("", type=["txt"], accept_multiple_files=True)
    if files:
        for file in files:
            file_name = upload_file_to_blob(file, STORAGEACCOUNTURL, STORAGEACCOUNTKEY, CONTAINERNAME)
            st.success(f"File '{file_name}' uploaded to '{CONTAINERNAME}/{file_name}'")

    # Sidebar to display uploaded files
    st.sidebar.caption("Uploaded Files in Azure Blob Storage")
    uploaded_files = list_blob_files(STORAGEACCOUNTURL, STORAGEACCOUNTKEY, CONTAINERNAME)
    for file_name in uploaded_files:
        st.sidebar.write(file_name)

# Chat with the uploaded data
def chat_page():
    
    st.caption("Please input your query below 👇")
    uploaded_files = list_blob_files(STORAGEACCOUNTURL, STORAGEACCOUNTKEY, CONTAINERNAME)
    all_data = []

    for file_name in uploaded_files:
        file_data = read_blob_data(STORAGEACCOUNTURL, STORAGEACCOUNTKEY, CONTAINERNAME, file_name)
        if file_data:
            all_data.append(file_data)

    # Combine all data from uploaded files
    combined_data = "\n".join(all_data)

    # Chat with the combined data
    user_input = st.text_input("You:", "")

    if st.button("Generate Response"):
        input_prompt = f"All Uploaded Data:\n{combined_data}\nUser Input: {user_input}"

        response = openai.Completion.create(
            engine="restaurant",
            prompt=input_prompt,
            temperature=0.7,
            max_tokens=1000,  # Increase token limit to accommodate longer responses
        )
        
        assistant_reply = response.choices[0].text.strip()
        st.text(assistant_reply)
        st.session_state['latest_response'] = response
        # st.text(response.usage.prompt_tokens)
        # st.text(response.usage.completion_tokens)
        # st.text(response.usage.total_tokens)
        st.session_state['translate_text'] = assistant_reply

    selected_language = st.selectbox("Select Target Language:", target_languages)

    if st.button("Translate"):
        if 'translate_text' not in st.session_state:
            st.session_state['translate_text'] = 'Value not Added'
            logger.info(st.session_state['translate_text'])
        else:
            logger.info(st.session_state['translate_text'])
            translate_text = st.session_state['translate_text']
            translate = tanslator(key, endpoint, location, path, translate_text, selected_language)
            logger.info(translate)
            st.text(translate)

if __name__ == "__main__":
    main()
