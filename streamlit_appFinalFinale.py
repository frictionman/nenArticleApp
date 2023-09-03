import streamlit as st
import os
from docx import Document
from docx.shared import Inches
import io
from PIL import Image
import requests
import replicate

# Function to generate response from LLM
def generate_llama2_response(prompt_input):
    string_dialogue = "You are a helpful assistant. You do not respond as 'User' or pretend to be 'User'. You only respond once as 'Assistant'."
    for dict_message in st.session_state.get("messages", []):
        if dict_message["role"] == "user":
            string_dialogue += "User: " + dict_message["content"] + "\n\n"
        else:
            string_dialogue += "Assistant: " + dict_message["content"] + "\n\n"
    output = replicate.run('a16z-infra/llama13b-v2-chat:df7690f1994d94e96ad9d568eac121aecf50684a0b0963b25a41cc40061269e5', 
                           input={"prompt": f"{string_dialogue} {prompt_input} Assistant: "})
    return next(output, {}).get('content', "")

def get_src_original_url(query):
    # ... (this remains unchanged)
    return None

def create_word_docx(user_input, paragraph, image_stream):
    # ... (this remains unchanged)
    return doc

def main():
    st.title("Article Generator App using Llama 2")
    user_input = st.text_input("Please enter the idea/topic for the article you want to generate!")
    image_input = st.text_input("Please enter the topic for the image you want to fetch!")

    result = ""  # Initialize the result variable

    if user_input and image_input:
        col1, col2, col3 = st.columns([1,2,1])

        with col1:
            st.subheader("Generated Content by Llama 2")
            try:
                result = generate_llama2_response(user_input)
                if result:
                    st.info("Your article has been been generated successfully!")
                    st.write(result)
                else:
                    st.error("Your article couldn't be generated or is empty!")
            except Exception as e:
                st.error(f"An error occurred while generating the article: {e}")

        with col2:
            st.subheader("Fetched Image")
            image_url = get_src_original_url(image_input)
            if image_url:
                response = requests.get(image_url)
                image_stream = io.BytesIO(response.content)
                st.image(image_stream)
            else:
                st.error("Couldn't fetch the image for the given topic.")

        with col3:
            st.subheader("Final Article to Download")
            if result and image_url:
                doc = create_word_docx(user_input, result, image_stream)
                doc_buffer = io.BytesIO()
                doc.save(doc_buffer)
                doc_buffer.seek(0)
                st.download_button(
                    label='Download Word Document',
                    data=doc_buffer,
                    file_name='document.docx',
                    mime='application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                )
            else:
                st.error("Couldn't generate the Word document. Ensure both the article and image are generated successfully.")

if __name__ == "__main__":
    main()
