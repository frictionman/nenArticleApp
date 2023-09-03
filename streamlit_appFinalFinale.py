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

def load_llm(max_tokens, prompt_template):
    # Load the model using the correct identifier
    llm_model_identifier = 'a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5'
    
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

def main():
    st.title("Article Generator App using Llama 2")
    user_input = st.text_input("Please enter the idea/topic for the article you want to generate!")
    image_input = st.text_input("Please enter the topic for the image you want to fetch!")

    if len(user_input) > 0 and len(image_input) > 0:
        col1, col2, col3 = st.columns([1,2,1])
        with col1:
            st.subheader("Generated Content by Llama 2")
            prompt_template = f"You are a digital marketing and SEO expert and your task is to write an article on the given topic: {user_input}. The article must be under 800 words."
            
            result = ""  # Initialize the result variable
            try:
                llm_chain = load_llm(max_tokens=800, prompt_template=prompt_template)
                generator_output = llm_chain(user_input)
                result = next(generator_output, {}).get('content', "")
                
                if result:
                    st.info("Your article has been been generated successfully!")
                    st.write(result)
                else:
                    st.error("Your article couldn't be generated or is empty!")

            except Exception as e:
                st.error(f"An error occurred while generating the article: {e}")

        # ... rest of the code ...

if __name__ == "__main__":
    main()
