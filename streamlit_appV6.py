
from langchain.llms import CTransformers
from langchain.chains import LLMChain
from langchain import PromptTemplate
import streamlit as st 
import os
from docx import Document
from docx.shared import Inches
import io
from PIL import Image
import requests
import replicate

# Loading the model
def load_llm(max_tokens, prompt_template):
    # Load the model using the correct identifier
    llm_model_identifier = 'a16z-infra/llama7b-v2-chat:4f0a4744c7295c024a1de15e1a63c880d3da035fa1f49bfd344fe076074c8eea'
    
    llm = CTransformers(
        model=llm_model_identifier,
        model_type="llama",
        max_new_tokens=max_tokens,
        temperature=0.7
    )
    
    llm_chain = LLMChain(
        llm=llm,
        prompt=PromptTemplate.from_template(prompt_template)
    )
    return llm_chain

def get_src_original_url(query):
    url = 'https://api.pexels.com/v1/search'
    # Use Streamlit's secrets for the API key
    headers = {
        'Authorization': st.secrets["PEXELS_API_KEY"],
    }

    params = {
        'query': query,
        'per_page': 1,
    }

    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        photos = data.get('photos', [])
        if photos:
            return photos[0]['src']['original']
    return None

# Rest of the code remains unchanged...
