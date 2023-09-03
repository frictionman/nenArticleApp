import streamlit as st
import os
from docx import Document
from docx.shared import Inches
import io
import requests
import replicate
from io import BytesIO

# This function retrieves the API token
def get_replicate_api():
    if 'REPLICATE_API_TOKEN' in st.secrets:
        return st.secrets['REPLICATE_API_TOKEN']
    else:
        return st.text_input('Enter Replicate API token:', type='password')

@st.cache_data
def load_llm(replicate_api, selected_model):
    os.environ['REPLICATE_API_TOKEN'] = replicate_api
    ...
    return llm

def get_image_url(query):
    url = 'https://api.pexels.com/v1/search'
    headers = {
        'Authorization': st.secrets["PEXELS_API_KEY"],  # Using Streamlit secrets for security
    }
    ...

def generate_article(prompt_input, llm_model):
    # Detailed prompt template from 'beta' for better context
    prompt_template = (f"You are a digital marketing and SEO expert. Your task is to write an article on the topic: '{prompt_input}'. "
                       "The article must be under 800 words and should be lengthy.")
    string_dialogue = f"User: {prompt_template}\n\n"
    generator_output = replicate.run(llm_model, input={"prompt": f"{string_dialogue} Assistant: "})
    response = next(generator_output, {})
    return response.get('content', "") if isinstance(response, dict) else response

def main():
    ...
    # The rest of the 'main' function remains unchanged

if __name__ == "__main__":
    main()
