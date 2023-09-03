import streamlit as st 
import os
from docx import Document
from docx.shared import Inches
import io
from PIL import Image
import requests
import replicate

# Loading the model
def generate_response_with_replicate(string_dialogue, prompt_input):
    # Use the correct model identifier for Llama 13
    model_identifier = 'a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5'
    response = replicate.run(
        model_identifier, 
        input={"prompt": f"{string_dialogue} {prompt_input} Assistant: "}
    )
    return response

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

def main():
    with st.sidebar:
        st.title('🦙💬 Llama 2 Chatbot')
        if 'REPLICATE_API_TOKEN' in st.secrets:
            st.success('API key already provided!', icon='✅')
        else:
            replicate_api = st.text_input('Enter Replicate API token:', type='password')
            os.environ['REPLICATE_API_TOKEN'] = replicate_api
    
    st.title("Article Generator App using Replicate Llama 13")
    user_input = st.text_input("Please enter the idea/topic for the article you want to generate!")
    image_input = st.text_input("Please enter the topic for the image you want to fetch!")

    if len(user_input) > 0 and len(image_input) > 0:
        col1, col2, col3 = st.columns([1,2,1])
        
        with col1:
            st.subheader("Generated Content by Llama 13")
            string_dialogue = "Assistant: Please provide an article on the topic."
            result = generate_response_with_replicate(string_dialogue, user_input)
            if result:
                st.info("Your article has been generated successfully!")
                st.write(result)
            else:
                st.error("Your article couldn't be generated!")

        with col2:
            st.subheader("Fetched Image")
            image_url = get_src_original_url(image_input)
            st.image(image_url)

        with col3:
            st.subheader("Final Article to Download")
            image_filename = "temp_image.jpg"
            # Save the image locally
            image = Image.open(requests.get(image_url, stream=True).raw)
            image.save(image_filename)
            
            doc = Document()
            doc.add_heading(user_input, level=1)
            doc.add_paragraph(result)
            doc.add_heading('Image Input', level=1)
            doc.add_picture(image_filename, width=Inches(4))
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
