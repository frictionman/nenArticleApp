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

def save_image_from_url(url, filename="temp_image.jpg"):
    response = requests.get(url, stream=True)
    response.raise_for_status()
    with open(filename, 'wb') as file:
        for chunk in response.iter_content(8192):
            file.write(chunk)
    return filename

def create_word_docx(user_input, paragraph, image_filename):
    doc = Document()
    doc.add_heading(user_input, level=1)
    doc.add_paragraph(paragraph)
    doc.add_heading('Image Input', level=1)
    doc.add_picture(image_filename, width=Inches(4))
    return doc

def main():
    st.title("Article Generator App using Llama 2")
    user_input = st.text_input("Please enter the idea/topic for the article you want to generate!")
    image_input = st.text_input("Please enter the topic for the image you want to fetch!")

    if len(user_input) > 0 and len(image_input) > 0:
        col1, col2, col3 = st.columns([1,2,1])
        
        # Generate Article
        with col1:
            st.subheader("Generated Content by Llama 2")
            prompt_template = f"You are a digital marketing and SEO expert and your task is to write an article on the topic: {{user_input}}. The article should be under 800 words."
            
            # Using Replicate
            string_dialogue = ""
            prompt_input = prompt_template.format(user_input=user_input)
            generator_output = replicate.run('a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5', 
                           input={"prompt": f"{string_dialogue} {prompt_input} Assistant: "})
            # Extracting the result from the generator
            result = next(generator_output, {}).get('content', "")
            if result:
                st.info("Your article has been generated successfully!")
                st.write(result)
            else:
                st.error("Your article couldn't be generated!")
        
        # Fetch Image
        with col2:
            st.subheader("Fetched Image")
            image_url = get_src_original_url(image_input)
            image_filename = save_image_from_url(image_url)
            st.image(image_filename)
        
        # Downloadable Word Document
        with col3:
            st.subheader("Final Article to Download")
            doc = create_word_docx(user_input, result, image_filename)
            doc_buffer = io.BytesIO()
            doc.save(doc_buffer)
            doc_buffer.seek(0)
            st.download_button(
                label='Download Word Document',
                data=doc_buffer,
                file_name='document.docx',
                mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
            )

if __name__ == "__main__":
    main()
